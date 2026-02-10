from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.auto_scheduler import snapshot

router = APIRouter(tags=["admin"])

@router.get("/admin/auto/status")
def auto_status():
    return JSONResponse(snapshot())
