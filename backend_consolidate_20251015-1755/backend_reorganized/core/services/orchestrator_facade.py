# core/services/orchestrator_facade.py
from __future__ import annotations

from typing import Dict, Any
from uuid import uuid4
from pathlib import Path

from core.services.builder_facade import build as build_with_facade
from core.agents.packager_agent import PackagerAgent

from core.services.plan_manifest import (
    ensure_rich_structure,
    validate_plan,
    write_plan_manifest,
)

# --- Enforcement del contrato + plantillas de fallback
from core.services.feature_contracts import (
    enforce_feature_contract,
    feature_required_paths,
)
from core.services import scaffold_templates as T


def _try_intake(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza los requisitos usando el agente de intake si está disponible."""
    try:
        from core.agents.llm_intake_agent import LLMIntakeAgent

        agent = LLMIntakeAgent()
        if hasattr(agent, "analyze_requirements"):
            return agent.analyze_requirements(requirements) or requirements
        if hasattr(agent, "normalize_for_planning"):
            return agent.normalize_for_planning(requirements) or requirements
    except Exception:
        pass
    return requirements


def _try_planning(intake_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Obtiene un plan del agente de planificación; si falla, devuelve fallback."""
    fallback = {
        "project_name": intake_payload.get("name") or "Forge Project",
        "stack": intake_payload.get("stack_hint") or "fastapi_postgres_docker",
        # sin structure: lo delegamos al Synth/ensure_rich_structure
        "variables": {"python_version": "3.12", "require_rich_structure": True},
        "features": intake_payload.get("features")
        or ["FastAPI", "health", "users_crud"],  # mínima sensata
    }
    try:
        from core.agents.llm_planning_agent import LLMPlanningAgent

        planner = LLMPlanningAgent()
        if hasattr(planner, "produce_plan_json"):
            plan = planner.produce_plan_json(intake_payload) or fallback
            return plan
        if hasattr(planner, "plan_project"):
            plan = planner.plan_project(intake_payload) or fallback
            return plan
    except Exception:
        pass
    return fallback


def plan_and_generate(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada principal para planificar, construir y empaquetar.
    - Intake LLM opcional
    - Planning LLM opcional (con fallback)
    - Enforcement de contrato (estructura requerida por features)
    - Validación + persistencia de plan.json
    - Build + materialización de fallbacks (si faltan archivos)
    - Packaging (ZIP)
    """
    normalized = _try_intake(requirements)
    plan = _try_planning(normalized)

    # Enriquecer estructura (rich), y ENFORCE por features
    plan = ensure_rich_structure(plan)
    plan = enforce_feature_contract(plan)

    # Validación
    errors = validate_plan(plan)
    if errors:
        plan.setdefault("meta", {})["plan_warnings"] = errors

    # Se necesita project_id antes de persistir
    project_id = str(uuid4())

    # Persistir plan.json
    manifest_path = write_plan_manifest(project_id, plan)
    plan.setdefault("meta", {})["manifest_path"] = manifest_path

    # Si el planner dejó structure demasiado corta, fuerza rich en Synth
    st = plan.get("structure")
    if isinstance(st, list) and len(st) < 4:
        plan.pop("structure", None)
        plan.setdefault("variables", {})["require_rich_structure"] = True

    # Build real (crea workdir)
    build_res = build_with_facade(project_id, plan)

    # Materializar fallbacks en disco si faltan
    _materialize_scaffold(build_res["workdir"], plan)

    # Paquete ZIP
    pkg = PackagerAgent().run(project_id, {"workdir": build_res["workdir"]})

    return {
        "project_id": project_id,
        "plan_stack": plan.get("stack"),
        "workdir": build_res["workdir"],
        "artifact": pkg.get("zip_path"),
        "status": pkg.get("status", "unknown"),
    }


def persist_plan_manifest(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece, valida y guarda plan.json en WORKDIR/<id>/PLAN/.
    Devuelve {plan, manifest_path, warnings?}.
    (No materializa archivos aquí; eso ocurre en build/materialization.)
    """
    plan = ensure_rich_structure(plan)
    plan = enforce_feature_contract(plan)

    warnings = validate_plan(plan)
    try:
        manifest_path = write_plan_manifest(project_id, plan)
    except Exception as e:
        manifest_path = None
        warnings = (warnings or []) + [f"manifest_write_error: {e}"]
    return {"plan": plan, "manifest_path": manifest_path, "warnings": warnings or None}


def _materialize_scaffold(workdir: str, plan: Dict[str, Any]) -> None:
    """
    Crea en disco los archivos mínimos de contrato si no existen,
    usando plantillas en core/services/scaffold_templates.py
    """
    root = Path(workdir)
    req_paths = feature_required_paths(plan.get("features", []) or [])
    for rel in req_paths:
        dst = root / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = _template_for(rel)
        if content is not None:
            dst.write_text(content, encoding="utf-8")

    # Bootstrap opcional de SQLite (crea fichero si se usa demo)
    _maybe_bootstrap_sqlite(root)


def _template_for(path: str) -> str | None:
    """Mapea rutas a plantillas de texto."""
    mapping = {
        "backend/app/routers/users.py": T.USERS_ROUTER,
        "backend/app/schemas.py": T.SCHEMAS,
        "backend/app/models.py": T.MODELS,
        "backend/app/db.py": T.DB,
        "backend/app/routers/health.py": T.HEALTH,
        "backend/app/main.py": T.MAIN,
        "backend/app/requirements.txt": T.REQ,
        "alembic.ini": T.ALEMBIC_INI,
        "alembic/env.py": T.ALEMBIC_ENV,
        "alembic/versions/0001_init.py": T.ALEMBIC_0001,
        "Dockerfile": T.DOCKERFILE,
        "docker-compose.yml": T.COMPOSE,
    }
    return mapping.get(path)


def _maybe_bootstrap_sqlite(root: Path) -> None:
    """Crea un fichero SQLite vacío si se usa el fallback de demo."""
    try:
        import sqlite3

        app_db = root / "backend" / "app" / "app.db"
        if not app_db.exists():
            sqlite3.connect(app_db.as_posix()).close()
    except Exception as e:
        print(f"[WARN] sqlite bootstrap skipped: {e}")


def _smoke_check(workdir: str) -> None:
    """Compila recursivamente y comprueba ficheros clave mínimos."""
    import compileall

    ok = compileall.compile_dir(workdir, force=True, quiet=1, maxlevels=10)
    if not ok:
        raise RuntimeError("Smoke check failed: compile errors")

    need = [
        "backend/app/main.py",
        "backend/app/routers/health.py",
        "backend/app/requirements.txt",
    ]
    for rel in need:
        if not Path(workdir, rel).exists():
            raise RuntimeError(f"Smoke check: missing {rel}")


def build_only(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Solo build + package usando el plan dado."""
    # Asegura contrato antes de build
    plan = ensure_rich_structure(plan)
    plan = enforce_feature_contract(plan)

    build_res = build_with_facade(project_id, plan)
    _materialize_scaffold(build_res["workdir"], plan)

    pkg = PackagerAgent().run(project_id, {"workdir": build_res["workdir"]})
    return {"build": build_res, "package": pkg}
