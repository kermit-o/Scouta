from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db
from typing import Optional

router = APIRouter()

@router.post("/videos/{post_id}/view")
def record_view(
    post_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Record a video view with watch time.
    payload: { user_id?, session_id?, watch_seconds, completed }
    """
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    watch_seconds = int(payload.get("watch_seconds", 0))
    completed = bool(payload.get("completed", False))

    try:
        # Upsert — si ya existe para este user/session, actualizar si es mayor
        if user_id:
            existing = db.execute(
                text("SELECT id, watch_seconds FROM video_views WHERE post_id=:pid AND user_id=:uid"),
                {"pid": post_id, "uid": user_id}
            ).first()
        else:
            existing = db.execute(
                text("SELECT id, watch_seconds FROM video_views WHERE post_id=:pid AND session_id=:sid"),
                {"pid": post_id, "sid": session_id}
            ).first() if session_id else None

        if existing:
            # Solo actualizar si watch_seconds es mayor
            if watch_seconds > existing.watch_seconds:
                db.execute(
                    text("UPDATE video_views SET watch_seconds=:ws, completed=:c, updated_at=NOW() WHERE id=:id"),
                    {"ws": watch_seconds, "c": completed, "id": existing.id}
                )
        else:
            db.execute(
                text("INSERT INTO video_views (post_id, user_id, session_id, watch_seconds, completed) VALUES (:pid, :uid, :sid, :ws, :c)"),
                {"pid": post_id, "uid": user_id, "sid": session_id, "ws": watch_seconds, "c": completed}
            )
        db.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/videos/{post_id}/stats")
def video_stats(post_id: int, db: Session = Depends(get_db)):
    """Returns view stats for a video."""
    try:
        stats = db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_views,
                    COUNT(DISTINCT COALESCE(user_id::text, session_id)) as unique_views,
                    AVG(watch_seconds) as avg_watch_seconds,
                    SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completions
                FROM video_views WHERE post_id = :pid
            """),
            {"pid": post_id}
        ).first()
        return {
            "post_id": post_id,
            "total_views": stats[0] or 0,
            "unique_views": stats[1] or 0,
            "avg_watch_seconds": round(float(stats[2] or 0), 1),
            "completions": stats[3] or 0,
        }
    except Exception as e:
        return {"post_id": post_id, "error": str(e)}
