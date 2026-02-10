from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.api.v1.schemas.agents import AgentActionOut
from app.services.action_spawner import spawn_actions_for_post


def safe_limit(limiter_obj, rule: str):
    """No-op rate limit decorator if limiter backend doesn't support .limit()."""
    try:
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        limiter = Limiter(key_func=get_remote_address)
    except Exception:
        limiter = None

    try:
        fn = getattr(limiter_obj, "limit", None)
        if callable(fn):
            return fn(rule)
    except Exception:
        pass
    def _decorator(f):
        return f
    return _decorator

router = APIRouter(tags=["spawn"])

@router.post("/orgs/{org_id}/posts/{post_id}/spawn-actions", response_model=list[AgentActionOut])
def spawn_actions(
    org_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    n: int = Query(default=3, ge=1, le=20),
    force: bool = Query(default=False),
) -> list[AgentActionOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    try:
        created = spawn_actions_for_post(db, org_id=org_id, post_id=post_id, max_n=n, force=force)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return [
        AgentActionOut(
            id=a.id, org_id=a.org_id, agent_id=a.agent_id,
            target_type=a.target_type, target_id=a.target_id,
            action_type=a.action_type, status=a.status, content=a.content,
            policy_score=a.policy_score, policy_reason=a.policy_reason,
            created_at=a.created_at.isoformat(),
            published_at=a.published_at.isoformat() if a.published_at else None,
        )
        for a in created
    ]