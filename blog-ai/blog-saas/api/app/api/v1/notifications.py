from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["notifications"])


@router.get("/notifications")
def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import text
    rows = db.execute(
        text(
            "SELECT id, type, comment_id, actor_name, post_id, post_title, read, created_at "
            "FROM notifications WHERE user_id=:uid ORDER BY id DESC "
            "LIMIT :limit OFFSET :offset"
        ),
        {"uid": user.id, "limit": limit, "offset": offset},
    ).fetchall()

    return {
        "unread": sum(1 for r in rows if not r.read),
        "notifications": [dict(r._mapping) for r in rows],
    }


@router.post("/notifications/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import text
    db.execute(text("UPDATE notifications SET read=1 WHERE user_id=:uid"), {"uid": user.id})
    db.commit()
    return {"ok": True}
