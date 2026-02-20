from __future__ import annotations

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.post import Post
from app.models.agent_profile import AgentProfile
from app.models.agent_action import AgentAction
from app.services.comment_spawner import spawn_debate_for_post


router = APIRouter(tags=["debate"])


@router.post("/orgs/{org_id}/posts/{post_id}/spawn-debate")
def spawn_debate(
    org_id: int,
    post_id: int,
    agent_ids: str = Query(..., description="Comma-separated agent_profile IDs, e.g. 1,3,7"),
    rounds: int = Query(2, ge=1, le=10),
    publish: bool = Query(True),
    source: str = Query("debate"),
    db: Session = Depends(get_db),
):
    agent_ids_list = [int(x) for x in agent_ids.split(',') if x.strip().isdigit()]
    # Validate post exists
    post = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).first()
    if not post:
        return {"detail": "Post not found"}

    # Parse agents
    ids: List[int] = [int(x.strip()) for x in agent_ids.split(",") if x.strip().isdigit()]
    if not ids:
        return {"detail": "No valid agent_ids"}

    agents = (
        db.query(AgentProfile)
        .filter(AgentProfile.org_id == org_id, AgentProfile.id.in_(ids))
        .all()
    )
    if not agents:
        return {"detail": "No agents found"}

@router.patch("/orgs/{org_id}/posts/{post_id}/debate-status")
def set_debate_status(
    org_id: int,
    post_id: int,
    status: str = Query(..., pattern="^(none|open|closed)$"),
    db: Session = Depends(get_db),
):
    """Cambiar debate_status de un post: none | open | closed"""
    post = db.query(Post).filter(Post.org_id == org_id, Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not hasattr(post, "debate_status"):
        raise HTTPException(status_code=400, detail="debate_status not supported")
    post.debate_status = status
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"post_id": post_id, "debate_status": post.debate_status}


    try:
        out = spawn_debate_for_post(
            db=db,
            org_id=org_id,
            post_id=post_id,
            agent_ids=agents,
            rounds=rounds,
            publish=publish,
            source=source,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return out


@router.get("/orgs/{org_id}/admin/actions")
def list_agent_actions(
    org_id: int,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Lista agent_actions para el panel admin"""
    q = db.query(AgentAction).filter(AgentAction.org_id == org_id)
    if status:
        q = q.filter(AgentAction.status == status)
    rows = q.order_by(AgentAction.id.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "agent_id": a.agent_id,
            "target_type": a.target_type,
            "target_id": a.target_id,
            "action_type": a.action_type,
            "status": a.status,
            "content": (a.content or "")[:200],
            "policy_score": a.policy_score,
            "created_at": str(getattr(a, "created_at", "")),
        }
        for a in rows
    ]

@router.get("/orgs/{org_id}/admin/posts")
def list_admin_posts(
    org_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Lista posts con debate_status para el panel admin"""
    rows = (
        db.query(Post)
        .filter(Post.org_id == org_id)
        .order_by(Post.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "debate_status": getattr(p, "debate_status", "none"),
            "created_at": str(p.created_at) if p.created_at else "",
            "published_at": str(p.published_at) if p.published_at else None,
            "comment_count": db.query(AgentAction).filter(
                AgentAction.org_id == org_id,
                AgentAction.target_id == p.id,
                AgentAction.target_type == "post",
            ).count(),
        }
        for p in rows
    ]
