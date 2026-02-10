from typing import Dict, Any
from uuid import UUID
from core.agents.dual_pipeline_supervisor import DualPipelineSupervisor

def plan_and_generate(project_id: str) -> Dict[str, Any]:
    """Unified facade to run the Dual Pipeline Supervisor without breaking legacy calls."""
    sup = DualPipelineSupervisor()
    return sup.run_dual_pipeline(UUID(project_id))
