import logging
from datetime import datetime
from typing import Dict, Any

from core.agents.intake_agent import IntakeAgent
from core.agents.specification_agent import SpecificationAgent
from core.agents.planning_agent import PlanningAgent
from core.agents.builder_agent import BuilderAgent
from core.agents.documenter_agent import DocumenterAgent
from core.agents.tester_agent import TesterAgent

logger = logging.getLogger(__name__)

class ProjectSupervisorSimple:
    """Simplified supervisor without database dependencies"""
    
    def __init__(self):
        self.agent_sequence = [
            ("intake", "Requirements Analysis", IntakeAgent()),
            ("spec", "Specification", SpecificationAgent()),
            ("planning", "Architecture Planning", PlanningAgent()),
            ("builder", "Code Generation", BuilderAgent()),
            ("documenter", "Documentation", DocumenterAgent()),
            ("tester", "Testing", TesterAgent())
        ]
    
    def run_pipeline(self, project_id: str, requirements: dict) -> dict:
        """Execute agent pipeline without database"""
        logger.info(f"Starting pipeline for project {project_id}")
        
        results = {}
        current_requirements = requirements.copy()
        
        for agent_id, description, agent_instance in self.agent_sequence:
            try:
                logger.info(f"Running {agent_id} agent: {description}")
                
                # Execute agent
                agent_result = agent_instance.run(project_id, current_requirements)
                
                if agent_result.get("status") == "failed":
                    logger.error(f"Agent {agent_id} failed: {agent_result.get('error')}")
                    results[agent_id] = agent_result
                    break
                    
                # Store result and update requirements
                results[agent_id] = agent_result
                current_requirements.update(agent_result)
                
                logger.info(f"Completed {agent_id} agent successfully")
                
            except Exception as e:
                logger.error(f"Error in {agent_id} agent: {e}")
                results[agent_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                break
        
        return {
            "project_id": project_id,
            "pipeline_status": "completed" if len(results) == len(self.agent_sequence) else "failed",
            "results": results,
            "agents_completed": list(results.keys())
        }
