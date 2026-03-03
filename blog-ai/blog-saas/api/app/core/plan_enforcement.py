"""
Plan enforcement utilities.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.org import Org
from app.models.plan import Plan
from app.models.org_member import OrgMember


def get_user_org_plan(db: Session, user_id: int) -> tuple[Org, Plan]:
    """Returns (org, plan) for the user."""
    member = db.query(OrgMember).filter(OrgMember.user_id == user_id).first()
    if not member:
        raise HTTPException(403, detail="No organization found for user")
    org = db.query(Org).filter(Org.id == member.org_id).first()
    if not org:
        raise HTTPException(403, detail="Organization not found")
    plan = db.query(Plan).filter(Plan.id == org.plan_id).first()
    if not plan:
        plan = db.query(Plan).filter(Plan.id == 1).first()
    return org, plan


def check_agent_limit(db: Session, user_id: int, org_id: int):
    """Raises 403 if user has reached agent limit."""
    from app.models.agent_profile import AgentProfile
    org, plan = get_user_org_plan(db, user_id)
    if plan.max_agents == 0:
        raise HTTPException(status_code=403, detail={
            "code": "PLAN_LIMIT_AGENTS",
            "message": f"Your {plan.name} plan doesn't include AI agents. Upgrade to Creator ($19/mo) or Brand ($79/mo).",
            "current_plan": plan.name,
            "upgrade_url": "/pricing",
        })
    current = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.created_by_user_id == user_id,
    ).count()
    if current >= plan.max_agents:
        raise HTTPException(status_code=403, detail={
            "code": "PLAN_LIMIT_AGENTS",
            "message": f"You've reached your limit of {plan.max_agents} agents on the {plan.name} plan.",
            "current_plan": plan.name,
            "max_agents": plan.max_agents,
            "current_count": current,
            "upgrade_url": "/pricing",
        })
    return org, plan


def check_post_limit(db: Session, user_id: int):
    """Raises 403 if plan doesn't allow post creation."""
    org, plan = get_user_org_plan(db, user_id)
    if not plan.can_create_posts:
        raise HTTPException(status_code=403, detail={
            "code": "PLAN_LIMIT_POSTS",
            "message": f"Your {plan.name} plan doesn't allow agents to create posts. Upgrade to Brand ($79/mo).",
            "current_plan": plan.name,
            "upgrade_url": "/pricing",
        })
    return org, plan


def get_plan_summary(db: Session, user_id: int) -> dict:
    """Returns plan info without raising."""
    try:
        org, plan = get_user_org_plan(db, user_id)
        from app.models.agent_profile import AgentProfile
        agent_count = db.query(AgentProfile).filter(
            AgentProfile.org_id == org.id,
            AgentProfile.created_by_user_id == user_id,
        ).count()
        return {
            "plan_id": plan.id,
            "plan_name": plan.name,
            "max_agents": plan.max_agents,
            "current_agents": agent_count,
            "agents_remaining": max(0, plan.max_agents - agent_count),
            "max_posts_month": plan.max_posts_month,
            "can_create_posts": plan.can_create_posts,
            "subscription_status": org.subscription_status,
        }
    except Exception:
        return {
            "plan_id": 1, "plan_name": "free", "max_agents": 0,
            "current_agents": 0, "agents_remaining": 0,
            "max_posts_month": 10, "can_create_posts": False,
            "subscription_status": "free",
        }
