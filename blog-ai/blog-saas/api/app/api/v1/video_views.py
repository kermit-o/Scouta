from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db
from app.core.security import decode_token

router = APIRouter()


def _try_user_id_from_request(request: Request) -> int | None:
    """Extract user_id from a Bearer token if present. Returns None for
    anonymous callers — video views are public stats so we don't reject."""
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = decode_token(auth[7:])
        sub = payload.get("sub")
        return int(sub) if sub else None
    except Exception:
        return None


@router.post("/videos/{post_id}/view")
def record_view(
    post_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Record a video view with watch time.

    Authenticated callers: the JWT subject is used as user_id (the request
    body's user_id field is ignored to prevent stat manipulation).
    Anonymous callers: must supply a session_id in the body, used as the
    deduplication key.
    """
    # Trust the token, never the payload — the previous version accepted
    # `user_id` from the body, letting any anonymous caller inflate any
    # other user's view count.
    user_id = _try_user_id_from_request(request)
    session_id = (payload.get("session_id") or "").strip()[:100] or None

    if not user_id and not session_id:
        raise HTTPException(status_code=400, detail="session_id required for anonymous views")

    # Clamp watch_seconds — a malicious client could send 999999 to skew
    # avg_watch_seconds in stats. Cap at 24h.
    try:
        watch_seconds = int(payload.get("watch_seconds", 0))
    except (TypeError, ValueError):
        watch_seconds = 0
    watch_seconds = max(0, min(watch_seconds, 86400))
    completed = bool(payload.get("completed", False))

    try:
        if user_id:
            existing = db.execute(
                text("SELECT id, watch_seconds FROM video_views WHERE post_id=:pid AND user_id=:uid"),
                {"pid": post_id, "uid": user_id}
            ).first()
        else:
            existing = db.execute(
                text("SELECT id, watch_seconds FROM video_views WHERE post_id=:pid AND session_id=:sid"),
                {"pid": post_id, "sid": session_id}
            ).first()

        if existing:
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
        # Don't leak internal error details (was returning str(e) — exposed
        # SQL fragments and column names). Log server-side instead.
        db.rollback()
        print(f"[video_views] record_view error post_id={post_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not record view")


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
        print(f"[video_views] stats error post_id={post_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not load stats")
