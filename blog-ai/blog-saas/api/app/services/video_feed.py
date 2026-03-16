"""
Video recommendation engine — Fase 1
Score = trending(0.30) + tags(0.25) + saves(0.20) + following(0.15) + language(0.10)
"""
import math
import re
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.post import Post
from app.models.saved_post import SavedPost


def _hours_ago(dt) -> float:
    if dt is None:
        return 720.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    return max(delta.total_seconds() / 3600, 0.1)


def _trending_score(upvotes: int, comments: int, hours: float) -> float:
    """HackerNews-style decay: (score) / (age + 2)^1.5"""
    score = upvotes * 2 + comments
    return score / math.pow(hours + 2, 1.5)


def _detect_language(text_content: str) -> str:
    """Simple heuristic — detect Arabic, Chinese, Korean, Spanish, etc."""
    if not text_content:
        return "en"
    arabic = len(re.findall(r'[\u0600-\u06FF]', text_content))
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text_content))
    korean = len(re.findall(r'[\uAC00-\uD7A3]', text_content))
    latin = len(re.findall(r'[a-zA-Z]', text_content))
    spanish_markers = len(re.findall(r'\b(el|la|los|las|es|que|con|por|para|una|un)\b', text_content.lower()))
    if arabic > 5:
        return "ar"
    if chinese > 3:
        return "zh"
    if korean > 3:
        return "ko"
    if spanish_markers > 2:
        return "es"
    return "en"


def get_video_feed(
    db: Session,
    org_id: int = 1,
    user_id: int | None = None,
    user_language: str = "en",
    user_location: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """
    Returns scored and ranked video posts for a user.
    """

    # ── Fetch all video posts ─────────────────────────────────────────
    posts = (
        db.query(Post)
        .filter(
            Post.org_id == org_id,
            Post.status == "published",
            Post.media_type == "video",
            Post.media_url.isnot(None),
        )
        .order_by(Post.created_at.desc())
        .limit(200)
        .all()
    )

    if not posts:
        return []

    # ── User context ──────────────────────────────────────────────────
    user_saved_post_ids: set[int] = set()
    user_liked_post_ids: set[int] = set()
    user_tag_ids: set[int] = set()
    following_user_ids: set[int] = set()

    if user_id:
        # Saved posts
        saved = db.execute(
            text("SELECT post_id FROM saved_posts WHERE user_id = :uid"),
            {"uid": user_id}
        ).fetchall()
        user_saved_post_ids = {r[0] for r in saved}

        # Liked posts
        liked = db.execute(
            text("SELECT post_id FROM post_votes WHERE user_id = :uid AND value = 1"),
            {"uid": user_id}
        ).fetchall()
        user_liked_post_ids = {r[0] for r in liked}

        # Tags from liked/saved posts
        all_engaged = user_saved_post_ids | user_liked_post_ids
        if all_engaged:
            try:
                tags = db.execute(
                    text("SELECT DISTINCT tag FROM post_tags WHERE post_id = ANY(:pids)"),
                    {"pids": list(all_engaged)}
                ).fetchall()
                user_tag_ids = {r[0] for r in tags}
            except Exception:
                pass

        # Following (user follows)
        follows = db.execute(
            text("SELECT following_id FROM user_follows WHERE follower_id = :uid"),
            {"uid": user_id}
        ).fetchall()
        following_user_ids = {r[0] for r in follows}

    # ── Saved by others (social proof) ───────────────────────────────
    save_counts: dict[int, int] = {}
    save_rows = db.execute(
        text("SELECT post_id, COUNT(*) as cnt FROM saved_posts GROUP BY post_id")
    ).fetchall()
    for row in save_rows:
        save_counts[row[0]] = row[1]

    # ── Post tags ─────────────────────────────────────────────────────
    post_tag_map: dict[int, set[int]] = {}
    post_ids = [p.id for p in posts]
    try:
        tag_rows = db.execute(
            text("SELECT post_id, tag FROM post_tags WHERE post_id = ANY(:pids)"),
            {"pids": post_ids}
        ).fetchall()
        for row in tag_rows:
            post_tag_map.setdefault(row[0], set()).add(row[1])
    except Exception:
        pass

    # ── Load author usernames ────────────────────────────────────────
    user_ids = [p.author_user_id for p in posts if p.author_user_id]
    username_map: dict[int, str] = {}
    display_map: dict[int, str] = {}
    if user_ids:
        try:
            urows = db.execute(
                text("SELECT id, username, display_name FROM users WHERE id = ANY(:uids)"),
                {"uids": user_ids}
            ).fetchall()
            for row in urows:
                username_map[row[0]] = row[1] or ""
                display_map[row[0]] = row[2] or row[1] or ""
        except Exception:
            pass

    # ── Watch time scores ────────────────────────────────────────────
    watch_scores: dict[int, float] = {}
    try:
        watch_rows = db.execute(
            text("""
                SELECT post_id, 
                    COUNT(*) as views,
                    AVG(watch_seconds) as avg_watch,
                    SUM(CASE WHEN completed THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as completion_rate
                FROM video_views
                GROUP BY post_id
            """)
        ).fetchall()
        for row in watch_rows:
            # Score: completion_rate * 0.6 + normalized_views * 0.4
            views = row[1] or 0
            completion = float(row[3] or 0)
            watch_scores[row[0]] = min(completion * 0.6 + min(views / 100.0, 1.0) * 0.4, 1.0)
    except Exception:
        pass

    # ── User already watched ──────────────────────────────────────────
    user_watched_ids: set[int] = set()
    if user_id:
        try:
            watched = db.execute(
                text("SELECT post_id FROM video_views WHERE user_id=:uid"),
                {"uid": user_id}
            ).fetchall()
            user_watched_ids = {r[0] for r in watched}
        except Exception:
            pass

    # ── Score each post ───────────────────────────────────────────────
    scored = []
    for post in posts:
        hours = _hours_ago(post.created_at)
        upvotes = getattr(post, "upvote_count", 0) or 0
        comments = getattr(post, "comment_count", 0) or 0

        # 1. Trending score (0-1 normalized roughly)
        trending = min(_trending_score(upvotes, comments, hours) / 10.0, 1.0)

        # 2. Tag relevance score
        post_tags = post_tag_map.get(post.id, set())
        if user_tag_ids and post_tags:
            tag_score = len(user_tag_ids & post_tags) / max(len(post_tags), 1)
        else:
            tag_score = 0.0

        # 3. Save score (social proof + personal)
        total_saves = save_counts.get(post.id, 0)
        save_score = min(total_saves / 10.0, 1.0)
        if post.id in user_saved_post_ids:
            save_score = min(save_score + 0.5, 1.0)

        # 4. Following score
        following_score = 0.0
        if post.author_user_id and post.author_user_id in following_user_ids:
            following_score = 1.0

        # 5. Language score
        post_lang = _detect_language((post.title or "") + " " + (post.body_md or ""))
        language_score = 1.0 if post_lang == user_language else 0.0

        # Watch time score
        watch_score = watch_scores.get(post.id, 0.0)

        # ── Final weighted score ──────────────────────────────────────
        final_score = (
            trending        * 0.25 +
            tag_score       * 0.20 +
            save_score      * 0.15 +
            following_score * 0.15 +
            language_score  * 0.10 +
            watch_score     * 0.15
        )

        # Demote already watched videos
        if post.id in user_watched_ids:
            final_score *= 0.4

        # Slight demote already saved
        if post.id in user_saved_post_ids:
            final_score *= 0.8

        scored.append((final_score, post))

    # ── Sort by score descending ──────────────────────────────────────
    scored.sort(key=lambda x: x[0], reverse=True)

    # ── Serialize ─────────────────────────────────────────────────────
    result = []
    for score, post in scored[offset:offset + limit]:
        result.append({
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "media_url": post.media_url,
            "media_type": post.media_type,
            "author_user_id": post.author_user_id,
            "author_agent_id": post.author_agent_id,
            "author_display_name": display_map.get(post.author_user_id) if post.author_user_id else None,
            "author_username": username_map.get(post.author_user_id) if post.author_user_id else None,
            "comment_count": getattr(post, "comment_count", 0) or 0,
            "upvote_count": getattr(post, "upvote_count", 0) or 0,
            "created_at": post.created_at.isoformat() if post.created_at else "",
            "_score": round(score, 4),
        })

    return result
