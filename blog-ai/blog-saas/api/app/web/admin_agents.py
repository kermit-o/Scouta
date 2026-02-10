from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.core.deps import get_db
from app.models.agent_profile import AgentProfile

router = APIRouter(tags=["admin"])

@router.patch("/admin/orgs/{org_id}/agents/{agent_id}/shadow-ban")
def set_shadow_ban(
    org_id: int,
    agent_id: int,
    value: bool = Query(...),
    db = Depends(get_db),
):
    a = (
        db.query(AgentProfile)
        .filter(AgentProfile.org_id == org_id)
        .filter(AgentProfile.id == agent_id)
        .one_or_none()
    )
    if not a:
        return JSONResponse({"detail": "Agent not found"}, status_code=404)

    if not hasattr(a, "is_shadow_banned"):
        return JSONResponse({"detail": "DB not migrated (missing is_shadow_banned)"}, status_code=409)

    a.is_shadow_banned = bool(value)
    db.commit()
    return {"ok": True, "agent_id": agent_id, "is_shadow_banned": a.is_shadow_banned}
