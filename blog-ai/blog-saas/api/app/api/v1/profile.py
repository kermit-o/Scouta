from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.comment import Comment
from app.models.vote import Vote

router = APIRouter(tags=["profile"])


def _user_stats(db: Session, user: User) -> dict:
    # Comentarios del usuario
    comment_count = db.query(func.count(Comment.id)).filter(
        Comment.author_user_id == user.id,
        Comment.status == "published",
    ).scalar() or 0

    # Likes recibidos en sus comentarios
    likes_received = db.query(func.count(Vote.id)).join(
        Comment, Comment.id == Vote.comment_id
    ).filter(
        Comment.author_user_id == user.id,
        Vote.value == 1,
    ).scalar() or 0

    # Followers
    followers = db.execute(
        text("SELECT COUNT(*) FROM follows WHERE following_id=:uid"),
        {"uid": user.id}
    ).scalar() or 0

    # Following
    following = db.execute(
        text("SELECT COUNT(*) FROM follows WHERE follower_id=:uid"),
        {"uid": user.id}
    ).scalar() or 0

    return {
        "comment_count": comment_count,
        "likes_received": likes_received,
        "followers": followers,
        "following": following,
    }


@router.get("/profile/me")
def get_my_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stats = _user_stats(db, user)
    # Últimos comentarios del usuario
    comments = db.query(Comment).filter(
        Comment.author_user_id == user.id,
        Comment.status == "published",
    ).order_by(Comment.id.desc()).limit(10).all()

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url or "",
        "bio": user.bio or "",
        "created_at": str(user.created_at),
        **stats,
        "recent_comments": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "body": (c.body or "")[:120],
                "created_at": str(c.created_at),
                "source": c.source,
            }
            for c in comments
        ],
        "recent_posts": [
            {
                "id": p.id,
                "title": p.title,
                "excerpt": getattr(p, "excerpt", None) or "",
                "created_at": str(p.created_at),
            }
            for p in db.query(Post).filter(
                Post.author_user_id == user.id,
                Post.status == "published",
            ).order_by(Post.created_at.desc()).limit(10).all()
        ],
    }


@router.get("/u/{username}")
def get_public_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = _user_stats(db, user)
    comments = db.query(Comment).filter(
        Comment.author_user_id == user.id,
        Comment.status == "published",
    ).order_by(Comment.id.desc()).limit(10).all()

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url or "",
        "bio": user.bio or "",
        "created_at": str(user.created_at),
        **stats,
        "recent_comments": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "body": (c.body or "")[:120],
                "created_at": str(c.created_at),
                "source": c.source,
            }
            for c in comments
        ],
        "recent_posts": [
            {
                "id": p.id,
                "title": p.title,
                "excerpt": getattr(p, "excerpt", None) or "",
                "created_at": str(p.created_at),
            }
            for p in db.query(Post).filter(
                Post.author_user_id == user.id,
                Post.status == "published",
            ).order_by(Post.created_at.desc()).limit(10).all()
        ],
    }


@router.post("/u/{username}/follow")
def follow_user(
    username: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target = db.query(User).filter(User.username == username).one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing = db.execute(
        text("SELECT id FROM follows WHERE follower_id=:fid AND following_id=:tid"),
        {"fid": user.id, "tid": target.id}
    ).first()

    if existing:
        db.execute(
            text("DELETE FROM follows WHERE follower_id=:fid AND following_id=:tid"),
            {"fid": user.id, "tid": target.id}
        )
        db.commit()
        action = "unfollowed"
    else:
        db.execute(
            text("INSERT INTO follows (follower_id, following_id) VALUES (:fid, :tid)"),
            {"fid": user.id, "tid": target.id}
        )
        db.commit()
        action = "followed"

    followers = db.execute(
        text("SELECT COUNT(*) FROM follows WHERE following_id=:tid"),
        {"tid": target.id}
    ).scalar() or 0

    return {"action": action, "followers": followers}


@router.get("/profile/my-posts")
def my_posts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.post import Post
    from app.models.comment import Comment
    from sqlalchemy import func
    posts = db.query(Post).filter(
        Post.author_user_id == user.id,
        Post.status == "published"
    ).order_by(Post.created_at.desc()).limit(50).all()

    comment_counts = dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_([p.id for p in posts]), Comment.status == "published")
        .group_by(Comment.post_id).all()
    ) if posts else {}

    return [{"id": p.id, "title": p.title, "slug": p.slug,
             "created_at": p.created_at.isoformat(),
             "debate_status": p.debate_status,
             "comment_count": comment_counts.get(p.id, 0)} for p in posts]


@router.get("/profile/my-comments")
def my_comments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.comment import Comment
    from app.models.post import Post
    from sqlalchemy.orm import joinedload
    comments = db.query(Comment).filter(
        Comment.author_user_id == user.id,
        Comment.status == "published"
    ).order_by(Comment.created_at.desc()).limit(100).all()

    post_ids = list({c.post_id for c in comments})
    posts_map = {p.id: p.title for p in db.query(Post).filter(Post.id.in_(post_ids)).all()} if post_ids else {}

    return [{"id": c.id, "body": c.body, "post_id": c.post_id,
             "post_title": posts_map.get(c.post_id, ""),
             "created_at": c.created_at.isoformat()} for c in comments]
