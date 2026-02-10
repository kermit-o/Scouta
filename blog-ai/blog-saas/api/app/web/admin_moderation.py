from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.core.deps import get_db
from app.core.security import decode_token
from app.services.moderation_service import list_moderation_queue, approve_action, reject_action

# Templates are shared at blog-saas/templates (one level above api/)
TEMPLATES_DIR = "/workspaces/Scouta/blog-ai/blog-saas/templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["admin"])


def _get_token(request: Request, token: Optional[str]) -> str:
    # Priority: query token -> cookie token
    if token:
        return token.strip()
    c = request.cookies.get("admin_token")
    return (c or "").strip()


def _require_token(token: str) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token. Add ?token=YOUR_JWT")
    try:
        return decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/admin/orgs/{org_id}/moderation", response_class=HTMLResponse)
def admin_moderation_queue(
    request: Request,
    org_id: int,
    token: Optional[str] = None,
    db=Depends(get_db),
):
    jwt = _get_token(request, token)
    _require_token(jwt)

    items = list_moderation_queue(db, org_id=org_id, limit=200)

    resp = templates.TemplateResponse(
        "admin_moderation.html",
        {
            "request": request,
            "org_id": org_id,
            "items": items,
            "has_token": bool(jwt),
        },
    )

    # If token came via query, persist in cookie for forms
    if token:
        resp.set_cookie("admin_token", jwt, httponly=True, samesite="lax")
    return resp


@router.post("/admin/orgs/{org_id}/moderation/{action_id}/approve")
def admin_approve(
    request: Request,
    org_id: int,
    action_id: int,
    token: Optional[str] = Form(default=None),
    db=Depends(get_db),
):
    jwt = _get_token(request, token)
    _require_token(jwt)

    approve_action(db, org_id=org_id, action_id=action_id)
    return RedirectResponse(url=f"/admin/orgs/{org_id}/moderation", status_code=303)


@router.post("/admin/orgs/{org_id}/moderation/{action_id}/reject")
def admin_reject(
    request: Request,
    org_id: int,
    action_id: int,
    reason: str = Form(default="rejected_by_admin"),
    token: Optional[str] = Form(default=None),
    db=Depends(get_db),
):
    jwt = _get_token(request, token)
    _require_token(jwt)

    reject_action(db, org_id=org_id, action_id=action_id, reason=reason)
    return RedirectResponse(url=f"/admin/orgs/{org_id}/moderation", status_code=303)
