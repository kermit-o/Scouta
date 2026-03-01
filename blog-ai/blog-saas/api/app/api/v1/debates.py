"""
Debates feed endpoint
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import Optional

from app.core.deps import get_db
from app.models.post import Post
from app.models.comment import Comment
from app.models.vote import Vote

router = APIRouter(prefix="/debates", tags=["debates"])


@router.get("")
def list_debates(
    page: int = 1,
    limit: int = 15,
    status: str = "open",
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit

    q = db.query(Post).filter(
        Post.status == "published",
        Post.debate_status.in_(["open", "closed"]),
    )
    if status in ("open", "closed"):
        q = q.filter(Post.debate_status == status)

    total = q.with_entities(func.count(Post.id)).scalar() or 0
    posts = q.order_by(desc(Post.published_at)).offset(offset).limit(limit).all()

    items = []
    for post in posts:
        # Stats de comments
        total_c = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id,
            Comment.status == "published",
        ).scalar() or 0
        agent_c = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id,
            Comment.status == "published",
            Comment.author_type == "agent",
        ).scalar() or 0
        human_c = total_c - agent_c

        # Top 3 agents por comment count
        top = db.query(
            Comment.author_agent_id,
            Comment.author_display_name if hasattr(Comment, 'author_display_name') else Comment.author_agent_id,
            func.count(Comment.id).label("cnt"),
        ).filter(
            Comment.post_id == post.id,
            Comment.author_type == "agent",
            Comment.status == "published",
        ).group_by(Comment.author_agent_id).order_by(desc("cnt")).limit(3).all()

        top_agents = [{"name": str(r[1] or f"Agent {r[0]}"), "count": r[2], "score": 0} for r in top]

        items.append({
            "id": post.id,
            "org_id": post.org_id,
            "title": post.title,
            "slug": post.slug or "",
            "excerpt": post.excerpt or "",
            "debate_status": post.debate_status,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "total_comments": total_c,
            "agent_comments": agent_c,
            "human_comments": human_c,
            "top_agents": top_agents,
        })

    return {
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
        "items": items,
    }
