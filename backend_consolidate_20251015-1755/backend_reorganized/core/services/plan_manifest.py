from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import json

from core.settings import WORKDIR_ROOT

REQUIRED_BASELINE = {
    "backend/app/main.py",
    "backend/app/routers/health.py",
    "backend/app/requirements.txt",
    "README.md",
}

def ensure_rich_structure(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Enriquece plan.structure si es pobre o inexistente."""
    stack = plan.get("stack")
    structure = plan.get("structure") or []

    # Si no hay structure pero el stack es nuestro ecommerce, inyectamos una lista mínima
    if not structure and stack == "fastapi_pg_ecommerce":
        plan["structure"] = [
            {"path": "backend/app/main.py"},
            {"path": "backend/app/routers/products.py"},
            {"path": "backend/app/routers/orders.py"},
            {"path": "backend/app/models.py"},
            {"path": "backend/app/schemas.py"},
            {"path": "alembic.ini"},
            {"path": "alembic/env.py"},
            {"path": "alembic/versions/0001_init.py"},
        ]
        return plan
    if not isinstance(structure, list) or len(structure) < 4:
        # baseline mínima
        baseline = [{"path": p} for p in REQUIRED_BASELINE]
        paths = {x.get("path") for x in structure if isinstance(x, dict)}
        for it in baseline:
            pth = it["path"]
            if pth not in paths:
                structure.append({"path": pth})
        plan["structure"] = structure
    return plan

def validate_plan(plan: Dict[str, Any]) -> List[str]:
    """Valida estructura: rutas mínimas, duplicados, campos clave."""
    errs: List[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a dict"]
    name = plan.get("project_name") or plan.get("name")
    if not name:
        errs.append("project_name missing")
    st = plan.get("structure")
    if not isinstance(st, list) or not st:
        errs.append("structure missing or empty")
    else:
        seen = set()
        for it in st:
            p = it.get("path") if isinstance(it, dict) else None
            if not p:
                errs.append("structure item without path")
                continue
            if p in seen:
                errs.append(f"duplicate path: {p}")
            seen.add(p)
        for req in REQUIRED_BASELINE:
            if req not in seen:
                errs.append(f"required missing: {req}")
    return errs

def write_plan_manifest(project_id: str, plan: Dict[str, Any]) -> str:
    """Guarda plan.json en WORKDIR/<id>/PLAN/plan.json y devuelve la ruta."""
    wd = WORKDIR_ROOT / project_id
    target = wd / "PLAN"
    target.mkdir(parents=True, exist_ok=True)
    out = target / "plan.json"
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(out)
