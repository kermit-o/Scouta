"""
Simple UI Orchestrator for API compatibility
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class UIOrchestrator:
    def __init__(self):
        self.name = "UIOrchestrator"
    
    def generate_project(self, user_input: str, project_type: str = "web_app") -> Dict[str, Any]:
        """Generate project from user input"""
        try:
            logger.info(f"Generating project: {user_input}")
            
            # Mock implementation
            return {
                "status": "success",
                "project_id": "mock-project-123",
                "message": f"Project generated from: {user_input}",
                "specification": {
                    "name": "Generated Project",
                    "type": project_type,
                    "description": user_input
                }
            }
        except Exception as e:
            logger.error(f"Error generating project: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global instance
ui_orchestrator = UIOrchestrator()
