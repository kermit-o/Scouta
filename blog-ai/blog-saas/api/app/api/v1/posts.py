from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.vote import Vote
from app.models.agent_profile import AgentProfile
from app.api.v1.schemas.posts import PostCreateIn, PostPatchIn, PostOut
from sqlalchemy import func

router = APIRouter(tags=["posts"])

@router.get("/orgs/{org_id}/posts")
def list_posts(
    org_id: int,
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="recent"),
    tag: str | None = Query(default=None),
):
    import datetime as _dt
    from sqlalchemy import text as _text

    query = db.query(Post).filter(Post.org_id == org_id)
    if status:
        query = query.filter(Post.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter((Post.title.ilike(like)) | (Post.body_md.ilike(like)))
    if tag:
        tag_ids = [r[0] for r in db.execute(_text(
            "SELECT post_id FROM post_tags WHERE tag = :tag"
        ), {"tag": tag.lower()}).fetchall()]
        if not tag_ids:
            return []
        query = query.filter(Post.id.in_(tag_ids))

    if sort == "commented":
        comment_sub = (
            db.query(Comment.post_id, func.count(Comment.id).label("cnt"))
            .filter(Comment.status == "published")
            .group_by(Comment.post_id).subquery()
        )
        rows = (
            query.outerjoin(comment_sub, Post.id == comment_sub.c.post_id)
            .order_by(desc(func.coalesce(comment_sub.c.cnt, 0)), desc(Post.created_at))
            .offset(offset).limit(limit).all()
        )
    elif sort == "hot":
        all_rows = query.order_by(desc(Post.created_at)).limit(limit * 3).all()
        cc = dict(
            db.query(Comment.post_id, func.count(Comment.id))
            .filter(Comment.post_id.in_([p.id for p in all_rows]), Comment.status == "published")
            .group_by(Comment.post_id).all()
        )
        now = _dt.datetime.now(_dt.timezone.utc)
        def _score(p):
            age = max((now - p.created_at.replace(tzinfo=_dt.timezone.utc)).total_seconds() / 3600, 0.1)
            return (cc.get(p.id, 0) * 5) / (age + 2) ** 1.5
        rows = sorted(all_rows, key=_score, reverse=True)[:limit]
    else:
        rows = query.order_by(desc(Post.created_at)).offset(offset).limit(limit).all()
    post_ids = [p.id for p in rows]

    # Agentes lookup
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Agentes lookup
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Comment counts
    comment_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published")
        .group_by(Comment.post_id).all()
    ) if post_ids else {}

    # Upvote counts
    upvote_counts = dict(
        db.query(Comment.post_id, func.count(Vote.id))
        .join(Vote, Vote.comment_id == Comment.id)
        .filter(Comment.post_id.in_(post_ids), Vote.value == 1)
        .group_by(Comment.post_id).all()
    ) if post_ids else {}

    # Contar total para paginación
    total_query = db.query(func.count(Post.id)).filter(Post.org_id == org_id)
    if status:
        total_query = total_query.filter(Post.status == status)
    total = total_query.scalar() or 0
    # Cargar usuarios humanos
    user_ids = [p.author_user_id for p in rows if p.author_user_id]
    user_rows = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    users = {u.id: u.display_name or u.username for u in user_rows}
    usernames = {u.id: u.username for u in user_rows}

    post_list = [
        PostOut(
            id=p.id,
            org_id=p.org_id,
            author_user_id=p.author_user_id,
            title=p.title,
            slug=p.slug,
            body_md=p.body_md,
            excerpt=getattr(p, "excerpt", None),
            status=p.status,
            debate_status=getattr(p, "debate_status", None),
            source=getattr(p, "source", None),
            created_at=p.created_at.isoformat() if p.created_at else "",
            published_at=p.published_at.isoformat() if p.published_at else None,
            comment_count=comment_counts.get(p.id, 0),
            upvote_count=upvote_counts.get(p.id, 0),
            author_agent_id=p.author_agent_id,
            author_agent_name=agents[p.author_agent_id].display_name if p.author_agent_id and p.author_agent_id in agents else None,
            author_type=getattr(p, "author_type", "agent"),
            author_display_name=agents[p.author_agent_id].display_name if p.author_agent_id and p.author_agent_id in agents else users.get(p.author_user_id),
            author_username=usernames.get(p.author_user_id),
            media_url=getattr(p, "media_url", None),
            media_type=getattr(p, "media_type", None),
        )
        for p in rows
    ]
    return {"posts": [p.model_dump() for p in post_list], "total": total}

@router.post("/orgs/{org_id}/posts", response_model=PostOut)
def create_post(
    org_id: int,
    payload: PostCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PostOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    p = Post(
        org_id=org_id,
        author_user_id=user.id,
        title=payload.title,
        slug=payload.slug,
        body_md=payload.body_md or "",
        status="draft",
        media_url=payload.media_url or None,
        media_type=payload.media_type or None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    try:
        from app.services.email_service import send_admin_notification
        send_admin_notification("new_post", username=user.username or user.email, title=p.title, post_id=p.id)
    except Exception as e:
        print("[email] admin post notification failed:", e)

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=None,
        media_url=getattr(p, "media_url", None),
        media_type=getattr(p, "media_type", None),
    )

@router.get("/orgs/{org_id}/posts/{post_id}", response_model=PostOut)
def get_post(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
) -> PostOut:
    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=p.published_at.isoformat() if p.published_at else None,
        media_url=getattr(p, "media_url", None),
        media_type=getattr(p, "media_type", None),
    )

@router.patch("/orgs/{org_id}/posts/{post_id}", response_model=PostOut)
def patch_post(
    org_id: int,
    post_id: int,
    payload: PostPatchIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PostOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        if data["status"] not in {"draft", "published"}:
            raise HTTPException(status_code=400, detail="Invalid status")
        if data["status"] == "published" and not p.published_at:
            p.published_at = datetime.now(timezone.utc)

    for k, v in data.items():
        setattr(p, k, v)

    db.add(p)
    db.commit()
    db.refresh(p)

    return PostOut(
        id=p.id,
        org_id=p.org_id,
        author_user_id=p.author_user_id,
        title=p.title,
        slug=p.slug,
        body_md=p.body_md,
        excerpt=getattr(p, "excerpt", None),
        status=p.status,
        debate_status=getattr(p, "debate_status", None),
        source=getattr(p, "source", None),
        created_at=p.created_at.isoformat() if p.created_at else "",
        published_at=p.published_at.isoformat() if p.published_at else None,
    )


@router.post("/orgs/{org_id}/posts/{post_id}/vote")
def vote_post(
    org_id: int,
    post_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from sqlalchemy import text
    value = payload.get("value", 1)
    if value not in (1, -1):
        raise HTTPException(status_code=400, detail="value must be 1 or -1")

    post = db.query(Post).filter(Post.id == post_id, Post.org_id == org_id).one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = db.execute(
        text("SELECT id, value FROM post_votes WHERE user_id=:uid AND post_id=:pid"),
        {"uid": user.id, "pid": post_id}
    ).first()

    if existing:
        if existing.value == value:
            db.execute(text("DELETE FROM post_votes WHERE user_id=:uid AND post_id=:pid"),
                      {"uid": user.id, "pid": post_id})
            action = "removed"
        else:
            db.execute(text("UPDATE post_votes SET value=:v WHERE user_id=:uid AND post_id=:pid"),
                      {"v": value, "uid": user.id, "pid": post_id})
            action = "changed"
    else:
        db.execute(text("INSERT INTO post_votes (user_id, post_id, value) VALUES (:uid, :pid, :v)"),
                  {"uid": user.id, "pid": post_id, "v": value})
        action = "added"
    db.commit()

    ups = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=1"), {"pid": post_id}).scalar()
    downs = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=-1"), {"pid": post_id}).scalar()
    # Notificar al autor del post si recibe upvote
    try:
        from sqlalchemy import text as sql_text
        if post.author_user_id and post.author_user_id != user.id and action == "added" and value == 1:
            db.execute(sql_text(
                "INSERT INTO notifications (user_id, type, actor_name, post_id, post_title) "
                "VALUES (:uid, 'post_upvote', :actor, :pid, :ptitle)"
            ), {
                "uid": post.author_user_id,
                "actor": user.display_name or user.username,
                "pid": post_id,
                "ptitle": post.title or "",
            })
            db.commit()
    except Exception as e:
        print("[notifications] post_upvote insert failed:", e)


    return {"action": action, "upvotes": ups, "downvotes": downs}


@router.get("/orgs/{org_id}/posts/{post_id}/votes")
def get_post_votes(org_id: int, post_id: int, db: Session = Depends(get_db)) -> dict:
    from sqlalchemy import text
    ups = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=1"), {"pid": post_id}).scalar()
    downs = db.execute(text("SELECT COUNT(*) FROM post_votes WHERE post_id=:pid AND value=-1"), {"pid": post_id}).scalar()
    return {"upvotes": ups, "downvotes": downs}


@router.get("/orgs/{org_id}/feed")
def get_feed(
    org_id: int,
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list:
    from sqlalchemy import text
    import math
    from datetime import datetime, timezone

    rows = db.query(Post).filter(
        Post.org_id == org_id,
        Post.status == "published",
    ).order_by(desc(Post.created_at)).limit(100).all()

    post_ids = [p.id for p in rows]
    if not post_ids:
        return []

    # Comment counts
    comment_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published")
        .group_by(Comment.post_id).all()
    )

    # Human comment counts (más valiosos)
    human_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids), Comment.status == "published", Comment.author_type == "user")
        .group_by(Comment.post_id).all()
    )

    # Upvote counts post
    placeholders = ",".join(str(i) for i in post_ids)
    upvote_counts = dict(
        db.execute(text(
            f"SELECT post_id, COUNT(*) as c FROM post_votes WHERE post_id IN ({placeholders}) AND value=1 GROUP BY post_id"
        )).fetchall()
    ) if post_ids else {}

    # Agentes
    agent_ids = {p.author_agent_id for p in rows if p.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    now = datetime.now(timezone.utc)

    def score(p):
        age_hours = max((now - p.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600, 0.1)
        ups = upvote_counts.get(p.id, 0)
        comments = comment_counts.get(p.id, 0)
        humans = human_counts.get(p.id, 0)
        raw = (ups * 3) + (humans * 5) + (comments * 1)
        return raw / math.pow(age_hours + 2, 1.5)

    scored = sorted(rows, key=score, reverse=True)[:limit]

    return [
        {
            "id": p.id,
            "org_id": p.org_id,
            "title": p.title,
            "slug": p.slug,
            "excerpt": getattr(p, "excerpt", None),
            "status": p.status,
            "debate_status": getattr(p, "debate_status", None),
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "author_type": getattr(p, "author_type", "agent"),
            "author_agent_id": p.author_agent_id,
            "author_agent_name": agents[p.author_agent_id].display_name if p.author_agent_id and p.author_agent_id in agents else None,
            "comment_count": comment_counts.get(p.id, 0),
            "upvote_count": upvote_counts.get(p.id, 0),
            "body_md": "",
        }
        for p in scored
    ]


@router.delete("/orgs/{org_id}/posts/{post_id}")
def delete_post(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    # Solo superuser o autor puede borrar
    is_superuser = getattr(user, "is_superuser", False)
    is_author = p.author_user_id == user.id
    if not is_superuser and not is_author:
        raise HTTPException(status_code=403, detail="Not allowed")
    # Borrar media de R2 si existe
    if p.media_url:
        try:
            import boto3, os
            key = p.media_url.split(".r2.dev/")[-1]
            s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
                region_name="auto",
            )
            s3.delete_object(Bucket=os.getenv("R2_BUCKET", "scouta-media"), Key=key)
            print(f"[delete_post] R2 deleted: {key}")
        except Exception as e:
            print(f"[delete_post] R2 delete error: {e}")
    db.delete(p)
    db.commit()
    return {"ok": True, "id": post_id}

@router.get("/orgs/{org_id}/posts/{post_id}/og-image")
def get_post_og_image(org_id: int, post_id: int, db: Session = Depends(get_db)):
    """Returns og:image as SVG for social sharing."""
    from fastapi.responses import Response

    p = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).first()
    raw_title = (p.title or "Scouta Debate") if p else "Scouta — AI Debates"
    excerpt = (getattr(p, "excerpt", None) or "")[:120] if p else ""
    comments = getattr(p, "comment_count", 0) or 0 if p else 0
    debate_status = getattr(p, "debate_status", "none") if p else "none"

    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

    # Smart word-wrap title into 2 lines ~38 chars each
    def wrap(text, width=38):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= width:
                cur = (cur + " " + w).strip()
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines[:2]  # max 2 lines

    title_lines = wrap(raw_title)
    line1 = esc(title_lines[0]) if len(title_lines) > 0 else ""
    line2 = esc(title_lines[1]) if len(title_lines) > 1 else ""
    excerpt_display = esc(excerpt[:90] + ("..." if len(excerpt) > 90 else "")) if excerpt else ""

    # Debate badge
    badge_color = "#4a9a4a" if debate_status == "open" else "#555"
    badge_text = "LIVE DEBATE" if debate_status == "open" else ("DEBATE CLOSED" if debate_status == "closed" else "DISCUSSION")
    badge_dot = "#4a9a4a" if debate_status == "open" else "#333"

    title_y2 = "260" if line2 else "230"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0a0a0a"/>
      <stop offset="100%" stop-color="#0d0f0d"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect x="0" y="0" width="3" height="630" fill="{badge_color}"/>
  <rect x="0" y="580" width="1200" height="50" fill="#050505"/>

  <!-- Header -->
  <text x="60" y="75" font-family="monospace" font-size="14" fill="#4a9a4a" letter-spacing="6">S C O U T A</text>

  <!-- Debate badge -->
  <circle cx="64" cy="118" r="5" fill="{badge_dot}"/>
  <text x="78" y="124" font-family="monospace" font-size="13" fill="{badge_color}" letter-spacing="3">{badge_text}</text>

  <!-- Title -->
  <text x="60" y="210" font-family="Georgia,serif" font-size="56" fill="#f0e8d8" font-weight="400">{line1}</text>
  <text x="60" y="280" font-family="Georgia,serif" font-size="56" fill="#f0e8d8" font-weight="400">{line2}</text>

  <!-- Excerpt -->
  <text x="60" y="360" font-family="Georgia,serif" font-size="22" fill="#666" font-style="italic">{excerpt_display}</text>

  <!-- Divider -->
  <rect x="60" y="490" width="80" height="1" fill="#2a2a2a"/>

  <!-- Footer -->
  <text x="60" y="605" font-family="monospace" font-size="14" fill="#333">{comments} comments</text>
  <text x="1140" y="605" font-family="monospace" font-size="14" fill="#2a2a2a" text-anchor="end">scouta.co</text>
</svg>"""
    headers = {"Cache-Control": "public, max-age=3600"}
    return Response(content=svg, media_type="image/svg+xml", headers=headers)
# redeploy 1773607284
