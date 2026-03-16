from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.video_feed import get_video_feed

router = APIRouter()

@router.get("/videos/feed")
def video_feed(
    org_id: int = 1,
    user_id: int | None = None,
    language: str = "en",
    location: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Returns personalized video feed scored by recommendation engine."""
    try:
        videos = get_video_feed(
            db=db,
            org_id=org_id,
            user_id=user_id,
            user_language=language,
            user_location=location,
            limit=limit,
            offset=offset,
        )
        return {"videos": videos, "total": len(videos)}
    except Exception as e:
        import traceback
        print(f"[video_feed] ERROR: {e}")
        print(traceback.format_exc()[:1000])
        return {"videos": [], "total": 0, "error": str(e)}
