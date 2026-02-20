from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.services.agent_post_generator import generate_post_for_agent

router = APIRouter(prefix="/orgs/{org_id}/agents", tags=["agent-posts"])

@router.post("/{agent_id}/generate-post")
def generate_post(
    org_id: int,
    agent_id: int,
    publish: bool = Query(False),
    topic_hint: str | None = Query(None),
    source: str = Query("manual", pattern="^(manual|autopost|api|scheduler)$"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    try:
        post = generate_post_for_agent(
            db=db,
            org_id=org_id,
            agent_id=agent_id,
            topic_hint=topic_hint,
            publish=publish,
            source=source,
        )
        return {
            "id": post.id,
            "org_id": post.org_id,
            "title": post.title,
            "status": post.status,
            "published_at": post.published_at
        }    
    except Exception as e:
        import traceback
        print("AGENT_POSTS_ERROR:\n", traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))