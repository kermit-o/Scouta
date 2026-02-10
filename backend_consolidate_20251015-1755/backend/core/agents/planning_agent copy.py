from typing import Dict, Any, List
import logging
from core.agents.agent_base import AgentBase

logger = logging.getLogger(__name__)

class PlanningAgent(AgentBase):
    """Agent for creating project architecture and planning"""
    
    def __init__(self):
        super().__init__("Planning Agent")  # FIXED: Added name parameter
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create project architecture plan"""
        self.log_activity(f"Creating architecture plan for project {project_id}")
        
        # Get analysis from previous steps
        analysis = requirements.get('analysis', '')
        specifications = requirements.get('specifications', '')
        
        prompt = f"""
        Based on the project analysis and specifications, create a detailed architecture plan:
        
        ANALYSIS:
        {analysis}
        
        SPECIFICATIONS:
        {specifications}
        
        Create a comprehensive architecture plan including:
        1. System architecture diagram description
        2. Technology stack decisions
        3. Database design
        4. API structure
        5. Frontend architecture
        6. Deployment strategy
        """
        
        try:
            architecture_plan = self.generate_ai_response(
                prompt, 
                "You are a solutions architect specializing in software architecture planning."
            )
            
            return {
                "project_id": project_id,
                "status": "completed",
                "architecture_plan": architecture_plan,
                "technology_stack": {
                    "backend": "FastAPI",
                    "frontend": "React", 
                    "database": "PostgreSQL",
                    "deployment": "Docker"
                }
            }
        except Exception as e:
            logger.error(f"Planning agent error: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }

# Maintain the existing run function for compatibility
def run(project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility function for existing code"""
    agent = PlanningAgent()
    return agent.run(project_id, requirements)
