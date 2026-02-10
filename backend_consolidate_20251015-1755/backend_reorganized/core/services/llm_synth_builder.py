from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.services.feature_contracts import (
    feature_required_paths,
    feature_gen_prompt,
    REQUIRED_FILES as _REQUIRED_FILES_COMPAT,
    GEN_PROMPTS as _GEN_PROMPTS_COMPAT,
)

class LLMSynthBuilder:
    """SINTETIZA un plan de proyecto (sin I/O de red) a partir de features y stack."""

    def __init__(self, stack: str = "fastapi_postgres_docker"):
        self.stack = stack

    def synthesize_plan(
        self,
        name: str,
        features: List[str],
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        variables = variables or {}
        # **Clave**: usar el contrato para expandir rutas requeridas
        required_paths: List[str] = feature_required_paths(features)

        # Construir estructura con dicts {path: "..."}
        structure = [{"path": p} for p in required_paths]

        plan: Dict[str, Any] = {
            "project_name": name,
            "stack": self.stack,
            "features": list(features),
            "variables": variables,
            "structure": structure,
        }
        return plan

def ensure_required_files(plan: Dict[str, Any], workdir: Path) -> List[str]:
    """
    Crea placeholders vacíos para todos los paths del plan.
    Útil para que el ZIP final siempre incluya la estructura mínima esperada.
    """
    created: List[str] = []
    for item in plan.get("structure", []):
        rel = item.get("path")
        if not rel:
            continue
        p = workdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            # Crear archivos vacíos solo si no existen
            p.write_text("", encoding="utf-8")
            created.append(str(p))
    return created

# API de conveniencia para otros módulos/tests
def synth_project(
    name: str,
    features: List[str],
    stack: str = "fastapi_postgres_docker",
    variables: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return LLMSynthBuilder(stack=stack).synthesize_plan(name=name, features=features, variables=variables)
