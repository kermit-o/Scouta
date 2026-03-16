from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.saved_post import SavedPost

router = APIRouter()

@router.post("/posts/{post_id}/save")
def save_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(SavedPost).filter_by(user_id=user.id, post_id=post_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False}
    db.add(SavedPost(user_id=user.id, post_id=post_id))
    db.commit()
    return {"saved": True}

@router.get("/posts/{post_id}/save")
def get_save_status(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(SavedPost).filter_by(user_id=user.id, post_id=post_id).first()
    return {"saved": bool(exists)}

@router.get("/saved-posts")
def list_saved_posts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(SavedPost).filter_by(user_id=user.id).order_by(SavedPost.created_at.desc()).all()
    return {"post_ids": [r.post_id for r in rows]}
