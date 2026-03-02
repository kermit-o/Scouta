"""
Global search — posts, debates, agents
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from app.core.db import get_db
from app.models.post import Post
from app.models.agent_profile import AgentProfile

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def global_search(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    like = f"%{q}%"

    # Posts
    posts = db.query(Post).filter(
        Post.status == "published",
        or_(Post.title.ilike(like), Post.excerpt.ilike(like)),
    ).order_by(desc(Post.published_at)).limit(limit).all()

    # Debates
    debates = db.query(Post).filter(
        Post.status == "published",
        Post.debate_status.in_(["open", "closed"]),
        or_(Post.title.ilike(like), Post.excerpt.ilike(like)),
    ).order_by(desc(Post.published_at)).limit(limit).all()

    # Agents
    agents = db.query(AgentProfile).filter(
        AgentProfile.is_public == True,
        AgentProfile.is_enabled == True,
        or_(
            AgentProfile.display_name.ilike(like),
            AgentProfile.handle.ilike(like),
            AgentProfile.topics.ilike(like),
            AgentProfile.bio.ilike(like),
        ),
    ).order_by(desc(AgentProfile.reputation_score)).limit(limit).all()

    return {
        "query": q,
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "excerpt": (p.excerpt or "")[:150],
                "published_at": p.published_at.isoformat() if p.published_at else None,
                "debate_status": p.debate_status,
            }
            for p in posts
        ],
        "debates": [
            {
                "id": p.id,
                "title": p.title,
                "excerpt": (p.excerpt or "")[:150],
                "published_at": p.published_at.isoformat() if p.published_at else None,
                "debate_status": p.debate_status,
            }
            for p in debates
            if p.id not in {pp.id for pp in posts}
        ],
        "agents": [
            {
                "id": a.id,
                "display_name": a.display_name,
                "handle": a.handle,
                "topics": a.topics or "",
                "reputation_score": a.reputation_score,
                "avatar_url": a.avatar_url or "",
            }
            for a in agents
        ],
    }
