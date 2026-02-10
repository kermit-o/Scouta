from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import shutil


from core.settings import WORKDIR_ROOT
from core.services.plan_manifest import validate_plan
from core.services.llm_synth_builder import LLMSynthBuilder




def _try_llm_synth(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prefer the LLM Synth Builder which writes full files with deterministic fallbacks.
    Works with either module-level build(...) or class LLMSynthBuilder().build(...).
    """
    try:
        from core.services import llm_synth_builder as synth
        # Module-level build(project_id, plan)
        if hasattr(synth, "build") and callable(getattr(synth, "build")):
            res = synth.build(project_id, plan)
            if isinstance(res, dict) and res.get("workdir"):
                return res
        # Class-based
        if hasattr(synth, "LLMSynthBuilder"):
            impl = synth.LLMSynthBuilder()
            if hasattr(impl, "build"):
                res = impl.build(project_id, plan)
                if isinstance(res, dict) and res.get("workdir"):
                    return res
    except Exception as e:
        return {"workdir": str(WORKDIR_ROOT / project_id), "builder_warnings": [f"llm_synth_error: {e}"]}
    return {"workdir": str(WORKDIR_ROOT / project_id), "builder_warnings": ["llm_synth_unavailable"]}

def _try_llm_synth_builder(project_id: str, plan: dict) -> dict:
    try:
        b = LLMSynthBuilder()
        return b.build(project_id, plan) or {}
    except Exception:
        return {}

# Preferimos el builder "real", si existe
def _try_real_builder(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    from core.agents.real_project_builder_fixed import RealProjectBuilderFixed as Impl
    # Algunos builders son async; si no, llama directo.
    impl = Impl()
    if hasattr(impl, "run_async"):
        import asyncio
        return asyncio.run(impl.run_async(project_id, plan))  # tipo dict esperado
    elif hasattr(impl, "run"):
        return impl.run(project_id, plan)
    # Fallback: contrato mínimo
    return {}

def _try_llm_builder(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    from core.agents.llm_builder_agent import LLMBuilderAgent as Impl
    impl = Impl()
    if hasattr(impl, "run"):
        return impl.run(project_id, plan)
    return {}

def _ensure_workdir(project_id: str, build_res: Dict[str, Any]) -> str:
    """Asegura WORKDIR_ROOT/<project_id>; si sólo tenemos project_path legacy, lo sincroniza."""
    workdir = WORKDIR_ROOT / project_id
    workdir.mkdir(parents=True, exist_ok=True)

    # Si builder devolvió 'workdir', úsalo
    if isinstance(build_res, dict):
        wd = build_res.get("workdir")
        if wd:
            return str(Path(wd))

        # Si hay 'project_path', lo copiamos al workdir para packager
        legacy = build_res.get("project_path")
        if legacy and Path(legacy).exists():
            src = Path(legacy)
            # copiar contenidos (no el directorio raíz) al workdir
            for item in src.iterdir():
                dst = workdir / item.name
                if item.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)
            return str(workdir)

    # Si no hay nada, creamos mínimo scaffold para no romper el ciclo
    (workdir / "README.md").write_text("# Builder Fallback\nThis project was created as a fallback.\n", encoding="utf-8")
    (workdir / "src").mkdir(exist_ok=True)
    (workdir / "src" / "app.py").write_text("print('hello from fallback builder')\n", encoding="utf-8")
    return str(workdir)

def build(project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    stack = plan.get("stack") or "fastapi_postgres_docker"
    workdir = Path("workdir") / project_id
    workdir.mkdir(parents=True, exist_ok=True)
    # Priority: 1) LLM Synth Builder, 2) RealProjectBuilderFixed, 3) LLM Builder Agent
    res = _try_llm_synth(project_id, plan)
    if res and isinstance(res, Dict) and res.get('workdir'):
        return res
    
    if stack == "fastapi_pg_ecommerce":
        _copy_blueprint("fastapi_pg_ecommerce", workdir)
        return {
            "project_id": project_id,
            "workdir": str(workdir),
            "strategy": "blueprint_only",
            "stack": stack,
        } 

    # Si existe manifest en WORKDIR/<id>/PLAN/plan.json, úsalo como fuente de verdad
    try:
        from pathlib import Path as _P
        import json as _J
        m = WORKDIR_ROOT / project_id / 'PLAN' / 'plan.json'
        if m.exists():
            plan = _J.loads(m.read_text(encoding='utf-8'))
    except Exception:
        pass
    """Facade unificada: intenta real builder, luego LLM, y siempre garantiza 'workdir'."""
    build_res: Dict[str, Any] = {}
    errors = []

    # 1) LLM Synth (prioridad)
    try:
        tmp = _try_llm_synth_builder(project_id, plan) or {}
        if tmp: build_res = tmp
    except Exception as e:
        errors.append(f"llm_synth_error: {e}")

    # 2) Intento real
    try:
        build_res = _try_real_builder(project_id, plan) or {}
    except Exception as e:
        errors.append(f"real_builder_error: {e}")


    # 2) Intento LLM si vacío/falló
    if not build_res:
        try:
            build_res = _try_llm_builder(project_id, plan) or {}
        except Exception as e:
            errors.append(f"llm_builder_error: {e}")

    # 3) Asegurar workdir usable por Packager
    wd = _ensure_workdir(project_id, build_res)
    # Devuelve unión NO destructiva
    out = dict(build_res)
    out["workdir"] = wd
    if errors:
        out["builder_warnings"] = errors
    return out

BLUEPRINT_ROOT = Path(__file__).resolve().parents[1] / "blueprints"



def _copy_blueprint(stack: str, workdir: Path) -> None:
    """Copy a local blueprint skeleton into workdir."""
    src = BLUEPRINT_ROOT / stack
    if not src.exists():
        raise RuntimeError(f"Blueprint for stack '{stack}' not found at {src}")

    # directorios y ficheros que queremos clonar
    names = (
        "backend",
        "alembic",
        "alembic.ini",
        "Dockerfile",
        "docker-compose.yml",
    )

    for name in names:
        src_path = src / name
        if src_path.is_dir():
            dst_path = workdir / name
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        elif src_path.is_file():
            dst_path = workdir / name
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
