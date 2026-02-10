"""
Simple Supervisor - Lightweight project supervisor
"""
import sys
import os
from typing import Dict, Any
import uuid
from datetime import datetime

from core.agents.agent_base import AgentBase

# Import services with fallbacks
try:
    from services.database_service import db_service
except ImportError:
    # Create simple mock
    db_service = type('MockDB', (), {
        'save_project': lambda self, data: data.get('project_id'),
        'get_project': lambda self, pid: None,
        'update_project_status': lambda self, pid, status, **kwargs: None
    })()

class SimpleSupervisor(AgentBase):
    """Simplified supervisor for basic project generation"""
    
    def __init__(self):
        super().__init__("SimpleSupervisor")
        self.agents = {}
        
        # Load available agents
        try:
            from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
            self.agents['intake'] = EnhancedIntakeAgent()
            print("   ✅ EnhancedIntakeAgent loaded")
        except Exception as e:
            print(f"   ❌ EnhancedIntakeAgent: {e}")
        
        try:
            from core.agents.planning_agent import PlanningAgent
            self.agents['planning'] = PlanningAgent()
            print("   ✅ PlanningAgent loaded")
        except Exception as e:
            print(f"   ❌ PlanningAgent: {e}")
        
        try:
            from core.agents.scaffolder_agent import ScaffolderAgent
            self.agents['scaffolding'] = ScaffolderAgent()
            print("   ✅ ScaffolderAgent loaded")
        except Exception as e:
            print(f"   ❌ ScaffolderAgent: {e}")
    
    def create_project_plan(self, requirements: str) -> Dict[str, Any]:
        """Create a simple project plan without CrewAI"""
        try:
            project_id = str(uuid.uuid4())
            self.log(f"Creating project plan: {project_id}")
            
            result = {
                "project_id": project_id,
                "status": "success",
                "requirements": requirements,
                "timestamp": datetime.now().isoformat(),
                "agents_used": list(self.agents.keys()),
                "plan": {
                    "steps": [
                        {"step": 1, "action": "Requirements Analysis", "status": "pending"},
                        {"step": 2, "action": "Project Setup", "status": "pending"},
                        {"step": 3, "action": "Development", "status": "pending"},
                        {"step": 4, "action": "Testing", "status": "pending"},
                        {"step": 5, "action": "Deployment", "status": "pending"}
                    ]
                }
            }
            
            # Use available agents
            if 'intake' in self.agents:
                intake_result = self.agents['intake'].analyze_requirements(requirements, "web_app")
                result['intake_analysis'] = intake_result
            
            if 'planning' in self.agents:
                plan_result = self.agents['planning'].create_development_plan({
                    "description": requirements,
                    "project_type": "web_app"
                })
                result['development_plan'] = plan_result
            
            # Save to database
            db_service.save_project(result)
            
            self.log(f"Project plan created: {project_id}")
            return result
            
        except Exception as e:
            self.log(f"Error creating project plan: {e}")
            return {
                "project_id": str(uuid.uuid4()),
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
