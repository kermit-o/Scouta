from typing import Any, Dict
from uuid import uuid4

__all__ = ["SupervisorSimple"]

class SupervisorSimple:
    """Minimal concrete supervisor used by /analyze-idea.
    It does NOT depend on abstract bases. Replace later with real orchestration."""
    def create_and_start_project(self, raw_idea: str, analysis_plan: Dict[str, Any]) -> str:
        # TODO: persist to DB and enqueue a background job to build artifacts.
        # For now, return a generated project_id so the API can respond 200.
        return str(uuid4())
