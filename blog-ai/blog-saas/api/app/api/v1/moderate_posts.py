from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.post import Post
from app.services.post_moderation_adapter import PostModerationAdapter

router = APIRouter(prefix="/moderate-posts", tags=["moderation"])

@router.post("/run")
def run_moderation(limit: int = 20, db: Session = Depends(get_db)):
    """Ejecuta moderación en posts sin score"""
    adapter = PostModerationAdapter()
    posts = db.query(Post).filter(
        Post.status == "needs_review",
        Post.policy_score.is_(None)
    ).limit(limit).all()
    
    results = []
    for post in posts:
        moderated = adapter.moderate_post(db, post.id)
        if moderated:
            results.append({
                "id": moderated.id,
                "score": moderated.policy_score,
                "status": moderated.status,
                "reason": moderated.policy_reason
            })
    
    return {
        "total": len(posts),
        "moderated": len(results),
        "results": results
    }

@router.get("/queue")
def get_queue(limit: int = 50, db: Session = Depends(get_db)):
    """Lista posts pendientes de moderación"""
    posts = db.query(Post).filter(
        Post.status == "needs_review",
        Post.policy_score.is_(None)
    ).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "title": p.title[:50],
            "created": p.created_at.isoformat() if p.created_at else None
        }
        for p in posts
    ]
