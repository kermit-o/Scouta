from fastapi import APIRouter, HTTPException
from pathlib import Path
from core import settings
import json

router = APIRouter(prefix="/api/projects/diagnostics", tags=["projects-diagnostics"])

@router.get("/latest-plan")
def latest_plan():
    wd = settings.WORKDIR_ROOT
    dirs = sorted([p for p in wd.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    for d in dirs:
        plan = d / "PLAN" / "plan.json"
        if plan.exists():
            return {
                "project_id": d.name,
                "manifest_path": str(plan),
                "plan": json.loads(plan.read_text(encoding="utf-8"))
            }
    raise HTTPException(404, "No plan.json found")
