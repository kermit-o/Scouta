from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.agent_policy import AgentPolicy
from app.api.v1.schemas.settings import AgentPolicyOut, AgentPolicyPatch

router = APIRouter(tags=["agent-policies"])

def _get_or_create_policy(db: Session, org_id: int) -> AgentPolicy:
    p = db.query(AgentPolicy).filter(AgentPolicy.org_id == org_id).one_or_none()
    if p:
        return p
    p = AgentPolicy(org_id=org_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.get("/orgs/{org_id}/agent-policies", response_model=AgentPolicyOut)
def get_policy(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentPolicyOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)
    p = _get_or_create_policy(db, org_id)
    return AgentPolicyOut(
        org_id=p.org_id,
        allow_replies=p.allow_replies,
        allow_reactions=p.allow_reactions,
        allow_critique=p.allow_critique,
        max_risk_score=p.max_risk_score,
        require_human_review=p.require_human_review,
        banned_topics=p.banned_topics,
    )

@router.patch("/orgs/{org_id}/agent-policies", response_model=AgentPolicyOut)
def patch_policy(
    org_id: int,
    payload: AgentPolicyPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentPolicyOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin"}, db=db, user=user)
    p = _get_or_create_policy(db, org_id)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)

    db.add(p)
    db.commit()
    db.refresh(p)

    return AgentPolicyOut(
        org_id=p.org_id,
        allow_replies=p.allow_replies,
        allow_reactions=p.allow_reactions,
        allow_critique=p.allow_critique,
        max_risk_score=p.max_risk_score,
        require_human_review=p.require_human_review,
        banned_topics=p.banned_topics,
    )
