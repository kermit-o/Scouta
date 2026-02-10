from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.agent_action import AgentAction
from app.models.comment import Comment
from app.models.post import Post
from app.api.v1.schemas.agents import AgentActionOut

router = APIRouter(tags=["moderation"])

def _to_out(r: AgentAction) -> AgentActionOut:
    return AgentActionOut(
        id=r.id, org_id=r.org_id, agent_id=r.agent_id,
        target_type=r.target_type, target_id=r.target_id,
        action_type=r.action_type, status=r.status, content=r.content,
        policy_score=r.policy_score, policy_reason=r.policy_reason,
        created_at=r.created_at.isoformat(),
        published_at=r.published_at.isoformat() if r.published_at else None,
    )

@router.get("/orgs/{org_id}/moderation/queue", response_model=list[AgentActionOut])
def moderation_queue(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str = Query(default="needs_review"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AgentActionOut]:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    rows = (
        db.query(AgentAction)
        .filter(AgentAction.org_id == org_id, AgentAction.status == status)
        .order_by(desc(AgentAction.created_at))
        .limit(limit)
        .all()
    )
    return [_to_out(r) for r in rows]

@router.post("/orgs/{org_id}/moderation/{action_id}/approve", response_model=AgentActionOut)
def approve_action(
    org_id: int,
    action_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentActionOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    a = db.query(AgentAction).filter(AgentAction.org_id == org_id, AgentAction.id == action_id).one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Action not found")

    if a.status not in {"needs_review", "draft"}:
        raise HTTPException(status_code=409, detail=f"Cannot approve from status={a.status}")

    # Create comment if this is a comment/reply
    if a.action_type in {"comment", "reply"}:
        if a.target_type == "post":
            post = db.query(Post).filter(Post.org_id == org_id, Post.id == a.target_id).one_or_none()
            if not post:
                raise HTTPException(status_code=404, detail="Target post not found")

            c = Comment(
                org_id=org_id,
                post_id=post.id,
                parent_comment_id=None,
                author_type="agent",
                author_user_id=None,
                author_agent_id=a.agent_id,
                body=a.content,
                status="published",
            )
            db.add(c)

        elif a.target_type == "comment":
            parent = db.query(Comment).filter(Comment.org_id == org_id, Comment.id == a.target_id).one_or_none()
            if not parent:
                raise HTTPException(status_code=404, detail="Target comment not found")

            c = Comment(
                org_id=org_id,
                post_id=parent.post_id,
                parent_comment_id=parent.id,
                author_type="agent",
                author_user_id=None,
                author_agent_id=a.agent_id,
                body=a.content,
                status="published",
            )
            db.add(c)
    a.status = "published"
    a.published_at = datetime.now(timezone.utc)

    db.add(a)
    db.commit()
    db.refresh(a)

    return _to_out(a)

@router.post("/orgs/{org_id}/moderation/{action_id}/reject", response_model=AgentActionOut)
def reject_action(
    org_id: int,
    action_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentActionOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor"}, db=db, user=user)

    a = db.query(AgentAction).filter(AgentAction.org_id == org_id, AgentAction.id == action_id).one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Action not found")

    if a.status not in {"needs_review", "draft"}:
        raise HTTPException(status_code=409, detail=f"Cannot reject from status={a.status}")

    a.status = "blocked"
    db.add(a)
    db.commit()
    db.refresh(a)

    return _to_out(a)
