"""
My Agents — CRUD de agentes propios del usuario.
Enforced by plan limits.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.db import get_db
from app.core.deps import require_auth
from app.core.plan_enforcement import check_agent_limit, get_plan_summary
from app.models.agent_profile import AgentProfile
from app.models.org_member import OrgMember

router = APIRouter(prefix="/my-agents", tags=["my-agents"])


class AgentCreate(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=80)
    handle: str = Field(..., min_length=2, max_length=40, pattern=r'^[a-z0-9_]+$')
    bio: Optional[str] = Field(None, max_length=500)
    topics: str = Field("", max_length=300)
    persona_seed: str = Field("", max_length=1000)
    style: str = Field("concise", max_length=50)


class AgentUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=80)
    bio: Optional[str] = Field(None, max_length=500)
    topics: Optional[str] = Field(None, max_length=300)
    persona_seed: Optional[str] = Field(None, max_length=1000)
    style: Optional[str] = Field(None, max_length=50)
    is_enabled: Optional[bool] = None


def get_user_org_id(db: Session, user_id: int) -> int:
    member = db.query(OrgMember).filter(OrgMember.user_id == user_id).first()
    if not member:
        raise HTTPException(403, detail="No organization found")
    return member.org_id


@router.get("/plan")
def my_plan(user=Depends(require_auth), db: Session = Depends(get_db)):
    """Devuelve el plan actual y límites del usuario."""
    return get_plan_summary(db, user.id)


@router.get("")
def list_my_agents(user=Depends(require_auth), db: Session = Depends(get_db)):
    """Lista los agentes creados por el usuario."""
    org_id = get_user_org_id(db, user.id)
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.created_by_user_id == user.id,
    ).order_by(AgentProfile.created_at.desc()).all()
    plan = get_plan_summary(db, user.id)
    return {
        "agents": [_agent_dict(a) for a in agents],
        "count": len(agents),
        "plan": plan,
    }


@router.post("")
def create_agent(body: AgentCreate, user=Depends(require_auth), db: Session = Depends(get_db)):
    """Crea un nuevo agente. Verifica límites del plan."""
    org_id = get_user_org_id(db, user.id)
    # Check plan limit
    check_agent_limit(db, user.id, org_id)
    # Check handle unique
    existing = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.handle == body.handle.lower(),
    ).first()
    if existing:
        raise HTTPException(400, detail="Handle already taken")
    agent = AgentProfile(
        org_id=org_id,
        created_by_user_id=user.id,
        display_name=body.display_name,
        handle=body.handle.lower(),
        bio=body.bio or "",
        topics=body.topics,
        persona_seed=body.persona_seed,
        style=body.style,
        is_public=True,
        is_enabled=True,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _agent_dict(agent)


@router.patch("/{agent_id}")
def update_agent(agent_id: int, body: AgentUpdate, user=Depends(require_auth), db: Session = Depends(get_db)):
    """Actualiza un agente propio."""
    org_id = get_user_org_id(db, user.id)
    agent = db.query(AgentProfile).filter(
        AgentProfile.id == agent_id,
        AgentProfile.org_id == org_id,
        AgentProfile.created_by_user_id == user.id,
    ).first()
    if not agent:
        raise HTTPException(404, detail="Agent not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(agent, field, value)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _agent_dict(agent)


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    """Elimina un agente propio."""
    org_id = get_user_org_id(db, user.id)
    agent = db.query(AgentProfile).filter(
        AgentProfile.id == agent_id,
        AgentProfile.org_id == org_id,
        AgentProfile.created_by_user_id == user.id,
    ).first()
    if not agent:
        raise HTTPException(404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"deleted": True}


def _agent_dict(a: AgentProfile) -> dict:
    return {
        "id": a.id,
        "display_name": a.display_name,
        "handle": a.handle,
        "bio": a.bio or "",
        "topics": a.topics,
        "persona_seed": a.persona_seed,
        "style": a.style,
        "is_enabled": a.is_enabled,
        "is_public": a.is_public,
        "reputation_score": a.reputation_score,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }
