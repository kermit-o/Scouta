from __future__ import annotations

from typing import Any

from app.models.agent_action import AgentAction


def list_moderation_queue(db, org_id: int, limit: int = 100) -> list[AgentAction]:
    return (
        db.query(AgentAction)
        .filter(AgentAction.org_id == org_id)
        .filter(AgentAction.status == "needs_review")
        .order_by(AgentAction.created_at.desc())
        .limit(limit)
        .all()
    )


def approve_action(db, org_id: int, action_id: int) -> AgentAction:
    a = (
        db.query(AgentAction)
        .filter(AgentAction.org_id == org_id)
        .filter(AgentAction.id == action_id)
        .one()
    )
    if a.status != "needs_review":
        return a
    a.status = "published"
    db.commit()
    db.refresh(a)
    return a


def reject_action(db, org_id: int, action_id: int, reason: str = "rejected") -> AgentAction:
    a = (
        db.query(AgentAction)
        .filter(AgentAction.org_id == org_id)
        .filter(AgentAction.id == action_id)
        .one()
    )
    if a.status != "needs_review":
        return a
    a.status = "rejected"
    a.policy_reason = reason
    db.commit()
    db.refresh(a)
    return a
