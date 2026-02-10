from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
from core.settings import WORKDIR_ROOT

class RealProjectBuilderFixed:
    """Builder estable basado en plan.structure. Sin I/O LLM."""
    def run(self, project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        workdir = WORKDIR_ROOT / project_id
        workdir.mkdir(parents=True, exist_ok=True)

        structure: List[Dict[str, Any]] = plan.get("structure") or []
        if structure:
            for item in structure:
                rel = item.get("path")
                if not rel:
                    continue
                target = workdir / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                content = item.get("content", "")
                if isinstance(content, (dict, list)):
                    import json
                    content = json.dumps(content, indent=2)
                target.write_text(content, encoding="utf-8")
        else:
            # Fallback mínimo para no romper el ciclo
            (workdir / "README.md").write_text("# Real Builder (fallback)\n", encoding="utf-8")
            (workdir / "src").mkdir(exist_ok=True)
            (workdir / "src" / "app.py").write_text("print('hello real builder')\n", encoding="utf-8")

        return {
            "status": "built",
            "workdir": str(workdir),
            "file_count": sum(1 for _ in workdir.rglob("*") if _.is_file())
        }

    # Por si algún caller intenta async
    async def run_async(self, project_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(project_id, plan)
