from __future__ import annotations
import hashlib
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User

router = APIRouter(tags=["comments"])


class CommentIn(BaseModel):
    body: str
    parent_comment_id: Optional[int] = None


def _comment_dict(c: Comment, user: User | None = None, agent=None) -> dict:
    return {
        "id": c.id,
        "post_id": c.post_id,
        "parent_comment_id": c.parent_comment_id,
        "author_type": c.author_type,
        "author_agent_id": c.author_agent_id,
        "author_user_id": c.author_user_id,
        "author_username": user.username if user else None,
        "author_display_name": (user.display_name if user else None) or (agent.display_name if agent else None),
        "author_avatar_url": user.avatar_url if user else None,
        "status": c.status,
        "source": getattr(c, "source", None),
        "body": c.body,
        "created_at": str(c.created_at),
    }


@router.get("/orgs/{org_id}/posts/{post_id}/comments")
def list_comments(
    org_id: int,
    post_id: int,
    status: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    post = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    q = db.query(Comment).filter(Comment.org_id == org_id, Comment.post_id == post_id)
    if status:
        q = q.filter(Comment.status == status)
    if source:
        q = q.filter(Comment.source == source)
    total = q.count()
rows = (
    q.order_by(Comment.id.asc())
    .limit(limit)
    .offset(offset)
    .all()
)

    # Cargar usuarios para comentarios humanos
    user_ids = {c.author_user_id for c in rows if c.author_user_id}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    # Cargar agentes para comentarios de agentes
    from app.models.agent_profile import AgentProfile
    agent_ids = {c.author_agent_id for c in rows if c.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Cargar agentes para comentarios de agentes
    from app.models.agent_profile import AgentProfile
    agent_ids = {c.author_agent_id for c in rows if c.author_agent_id}
    agents = {a.id: a for a in db.query(AgentProfile).filter(AgentProfile.id.in_(agent_ids)).all()} if agent_ids else {}

    # Cargar vote counts para todos los comentarios
    from app.models.vote import Vote
    from sqlalchemy import func
    comment_ids = [c.id for c in rows]
    up_counts = dict(
        db.query(Vote.comment_id, func.count(Vote.id))
        .filter(Vote.comment_id.in_(comment_ids), Vote.value == 1)
        .group_by(Vote.comment_id).all()
    ) if comment_ids else {}
    down_counts = dict(
        db.query(Vote.comment_id, func.count(Vote.id))
        .filter(Vote.comment_id.in_(comment_ids), Vote.value == -1)
        .group_by(Vote.comment_id).all()
    ) if comment_ids else {}

    def enrich(c):
        d = _comment_dict(c, users.get(c.author_user_id), agents.get(c.author_agent_id))
        d["upvotes"] = up_counts.get(c.id, 0)
        d["downvotes"] = down_counts.get(c.id, 0)
        return d

    return {
        "post_id": post_id,
        "debate_status": getattr(post, "debate_status", "none"),
        "total": total,
        "comments": [enrich(c) for c in rows],
    }


@router.post("/orgs/{org_id}/posts/{post_id}/comments")
def create_comment(
    org_id: int,
    post_id: int,
    payload: CommentIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    post = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not payload.body or len(payload.body.strip()) < 2:
        raise HTTPException(status_code=400, detail="Comment too short")

    if len(payload.body) > 2000:
        raise HTTPException(status_code=400, detail="Comment too long (max 2000 chars)")

    # Verificar parent existe si se especifica
    if payload.parent_comment_id:
        parent = db.query(Comment).filter(
            Comment.id == payload.parent_comment_id,
            Comment.post_id == post_id,
        ).one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    body = payload.body.strip()
    comment_hash = hashlib.sha256(f"{user.id}:{post_id}:{body}".encode()).hexdigest()[:64]

    comment = Comment(
        org_id=org_id,
        post_id=post_id,
        parent_comment_id=payload.parent_comment_id,
        author_type="user",
        author_user_id=user.id,
        body=body,
        status="published",
        source="human",
        comment_hash=comment_hash,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Notificar al autor del parent si es reply
    if payload.parent_comment_id:
        try:
            from sqlalchemy import text
            parent = db.query(Comment).filter(Comment.id == payload.parent_comment_id).one_or_none()
            if parent and parent.author_user_id and parent.author_user_id != user.id:
                post_obj = db.query(Post).filter(Post.id == post_id).one_or_none()
                db.execute(text(
                    "INSERT INTO notifications (user_id, type, comment_id, actor_name, post_id, post_title) "
                    "VALUES (:uid, 'reply', :cid, :actor, :pid, :ptitle)"
                ), {
                    "uid": parent.author_user_id,
                    "cid": comment.id,
                    "actor": user.display_name or user.username,
                    "pid": post_id,
                    "ptitle": post_obj.title if post_obj else "",
                })
                db.commit()
        except Exception as e:
            print("[notifications] insert failed:", e)

    return _comment_dict(comment, user)


class VoteIn(BaseModel):
    value: int  # 1 or -1


@router.post("/orgs/{org_id}/posts/{post_id}/comments/{comment_id}/vote")
def vote_comment(
    org_id: int,
    post_id: int,
    comment_id: int,
    payload: VoteIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from app.models.vote import Vote
    from sqlalchemy import func

    if payload.value not in (1, -1):
        raise HTTPException(status_code=400, detail="value must be 1 or -1")

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing = db.query(Vote).filter(Vote.user_id == user.id, Vote.comment_id == comment_id).one_or_none()

    if existing:
        if existing.value == payload.value:
            # Toggle off — eliminar voto
            db.delete(existing)
            db.commit()
            action = "removed"
        else:
            existing.value = payload.value
            db.commit()
            action = "changed"
    else:
        vote = Vote(org_id=org_id, user_id=user.id, comment_id=comment_id, value=payload.value)
        db.add(vote)
        db.commit()
        action = "added"

    # Contar totales
    ups = db.query(func.count(Vote.id)).filter(Vote.comment_id == comment_id, Vote.value == 1).scalar()
    downs = db.query(func.count(Vote.id)).filter(Vote.comment_id == comment_id, Vote.value == -1).scalar()

    # Notificar al autor del comentario si recibe upvote
    try:
        from sqlalchemy import text as sql_text
        target = db.query(Comment).filter(Comment.id == comment_id).one_or_none()
        if target and target.author_user_id and target.author_user_id != user.id and action == "added" and payload.value == 1:
            post_obj = db.query(Post).filter(Post.id == post_id).one_or_none()
            db.execute(sql_text(
                "INSERT INTO notifications (user_id, type, comment_id, actor_name, post_id, post_title) "
                "VALUES (:uid, 'upvote', :cid, :actor, :pid, :ptitle)"
            ), {
                "uid": target.author_user_id,
                "cid": comment_id,
                "actor": user.display_name or user.username,
                "pid": post_id,
                "ptitle": post_obj.title if post_obj else "",
            })
            db.commit()
    except Exception as e:
            print("[notifications] insert failed:", e)

    return {"action": action, "upvotes": ups, "downvotes": downs}


@router.get("/orgs/{org_id}/posts/{post_id}/comments/{comment_id}/votes")
def get_votes(
    org_id: int,
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
) -> dict:
    from app.models.vote import Vote
    from sqlalchemy import func

    ups = db.query(func.count(Vote.id)).filter(Vote.comment_id == comment_id, Vote.value == 1).scalar()
    downs = db.query(func.count(Vote.id)).filter(Vote.comment_id == comment_id, Vote.value == -1).scalar()
    return {"upvotes": ups, "downvotes": downs}
