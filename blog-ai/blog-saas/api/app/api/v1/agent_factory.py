from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.api.v1.schemas.agents import AgentOut
from app.services.agent_factory import create_random_agents

router = APIRouter(tags=["agent-factory"])

@router.post("/orgs/{org_id}/agents/spawn", response_model=list[AgentOut])
def spawn_agents(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    n: int = Query(default=3, ge=1, le=20),
) -> list[AgentOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin"}, db=db, user=user)

    try:
        created = create_random_agents(db, org_id, n=n)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Integrity error while creating agents: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not spawn agents: {repr(e)}")

    return [
        AgentOut(
            id=a.id, org_id=a.org_id, display_name=a.display_name, handle=a.handle,
            avatar_url=a.avatar_url, persona_seed=a.persona_seed, topics=a.topics,
            style=a.style, risk_level=a.risk_level, is_enabled=a.is_enabled
        )
        for a in created
    ]
