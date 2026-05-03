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


# Lightweight badge endpoint — used by the nav (DesktopRail, MobileTopBar).
# Was missing entirely, causing repeated 404s in production logs.
@router.get("/notifications/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import text
    # `read` is BOOLEAN in Postgres — comparing to integer 0/1 errors with
    # "operator does not exist: boolean = integer". Use false/true literals.
    row = db.execute(
        text("SELECT COUNT(*) FROM notifications WHERE user_id=:uid AND read=false"),
        {"uid": user.id},
    ).scalar()
    return {"unread": int(row or 0)}


@router.post("/notifications/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import text
    db.execute(text("UPDATE notifications SET read=true WHERE user_id=:uid"), {"uid": user.id})
    db.commit()
    return {"ok": True}
