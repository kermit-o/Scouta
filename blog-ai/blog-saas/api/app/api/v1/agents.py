from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.agent_profile import AgentProfile
from app.api.v1.schemas.agents import AgentCreateIn, AgentPatchIn, AgentOut

router = APIRouter(tags=["agents"])

@router.get("/orgs/{org_id}/agents", response_model=list[AgentOut])
def list_agents(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    enabled: bool | None = Query(default=None),
) -> list[AgentOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)

    q = db.query(AgentProfile).filter(AgentProfile.org_id == org_id)
    if enabled is not None:
        q = q.filter(AgentProfile.is_enabled == enabled)
    rows = q.order_by(AgentProfile.id.asc()).all()

    return [
        AgentOut(
            id=a.id, org_id=a.org_id, display_name=a.display_name, handle=a.handle,
            avatar_url=a.avatar_url, persona_seed=a.persona_seed, topics=a.topics,
            style=a.style, risk_level=a.risk_level, is_enabled=a.is_enabled
        )
        for a in rows
    ]

@router.post("/orgs/{org_id}/agents", response_model=AgentOut)
def create_agent(
    org_id: int,
    payload: AgentCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin"}, db=db, user=user)

    existing = (
        db.query(AgentProfile)
        .filter(AgentProfile.org_id == org_id, AgentProfile.handle == payload.handle)
        .one_or_none()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Handle already exists in org")

    a = AgentProfile(
        org_id=org_id,
        display_name=payload.display_name,
        handle=payload.handle,
        avatar_url=payload.avatar_url or "",
        persona_seed=payload.persona_seed or "",
        topics=payload.topics or "",
        style=payload.style or "concise",
        risk_level=payload.risk_level if payload.risk_level is not None else 1,
        is_enabled=True,
    )
    db.add(a)
    db.commit()
    db.refresh(a)

    return AgentOut(
        id=a.id, org_id=a.org_id, display_name=a.display_name, handle=a.handle,
        avatar_url=a.avatar_url, persona_seed=a.persona_seed, topics=a.topics,
        style=a.style, risk_level=a.risk_level, is_enabled=a.is_enabled
    )

@router.patch("/orgs/{org_id}/agents/{agent_id}", response_model=AgentOut)
def patch_agent(
    org_id: int,
    agent_id: int,
    payload: AgentPatchIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin"}, db=db, user=user)

    a = db.query(AgentProfile).filter(AgentProfile.org_id == org_id, AgentProfile.id == agent_id).one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(a, k, v)

    db.add(a)
    db.commit()
    db.refresh(a)

    return AgentOut(
        id=a.id, org_id=a.org_id, display_name=a.display_name, handle=a.handle,
        avatar_url=a.avatar_url, persona_seed=a.persona_seed, topics=a.topics,
        style=a.style, risk_level=a.risk_level, is_enabled=a.is_enabled
    )
