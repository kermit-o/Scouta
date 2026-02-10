from __future__ import annotations

import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from core.services.orchestrator_facade import persist_plan_manifest, build_only
from core.services.feature_contracts import enforce_feature_contract

router = APIRouter(prefix="/api", tags=["projects"])


# ==== Modelos de entrada ====
class ProjectRequirements(BaseModel):
    stack: str
    features: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(BaseModel):
    name: str
    requirements: ProjectRequirements


# ==== Endpoint principal ====
@router.post("/projects")
def create_project(req: ProjectCreate, background: BackgroundTasks) -> Dict[str, Any]:
    project_id = str(uuid.uuid4())

    # Plan base mínimo (se puede extender más adelante)
    plan: Dict[str, Any] = {
        "project_name": req.name,
        "stack": req.requirements.stack,
        "features": list(req.requirements.features or []),
        "variables": dict(req.requirements.variables or {}),
        "structure": [
            {"path": "backend/app/requirements.txt"},
            {"path": "backend/app/routers/health.py"},
            {"path": "README.md"},
            {"path": "backend/app/main.py"},
        ],
    }

    # ✅ Aplicar enforcement UNA VEZ el dict está completo
    plan = enforce_feature_contract(plan)

    # Persistir y lanzar build en background
    persisted = persist_plan_manifest(project_id, plan)
    background.add_task(build_only, project_id, persisted["plan"])

    return {
        "accepted": True,
        "status": "queued",
        "project_id": project_id,
        "manifest_path": persisted["manifest_path"],
        "warnings": None,
    }
