import logging
from typing import Dict, Any
from core.agents.agent_base import AgentBase

logger = logging.getLogger(__name__)

class IntelligentIntakeAgent(AgentBase):
    """Intelligent intake agent - Versión mínima para compatibilidad"""
    
    def __init__(self):
        super().__init__("Intelligent Intake Agent")
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Versión mínima para compatibilidad"""
        return {
            "project_id": project_id,
            "status": "completed",
            "analysis": "Basic requirements analysis",
            "message": "Using minimal IntelligentIntakeAgent"
        }
