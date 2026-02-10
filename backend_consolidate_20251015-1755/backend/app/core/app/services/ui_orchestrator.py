import logging
import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.core.app.agents.supervisor_simple import ProjectSupervisorSimple
from backend.app.core.app.services.download_service import DownloadService
from backend.app.core.app.services.payment_service import PaymentService, PlanType

logger = logging.getLogger(__name__)

class UIOrchestrator:
    """Orchestrates the complete flow from UI to AI generation to download"""
    
    def __init__(self):
        self.supervisor = ProjectSupervisorSimple()
        self.download_service = DownloadService()
        self.payment_service = PaymentService()
        self.active_projects = {}  # In-memory storage for demo
    
    def create_project(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method: from UI form to generated project"""
        
        # Extract user input
        project_name = user_data.get('project_name', 'Mi Proyecto')
        description = user_data.get('description', '')
        project_type = user_data.get('type', 'web_application')
        user_id = user_data.get('user_id', 'demo_user')
        
        # Validate input
        if not description:
            return {
                "success": False,
                "error": "Por favor proporciona una descripción del proyecto"
            }
        
        # Check user limits (for demo, using FREE plan)
        if not self.payment_service.check_project_limit(PlanType.FREE, self._get_user_project_count(user_id)):
            return {
                "success": False,
                "error": "Límite de proyectos alcanzado. Actualiza tu plan."
            }
        
        # Generate project ID
        project_id = str(uuid.uuid4())
        
        # Prepare requirements for AI
        requirements = {
            "name": project_name,
            "description": description,
            "type": project_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store project in memory
        self.active_projects[project_id] = {
            "id": project_id,
            "name": project_name,
            "status": "generating",
            "created_at": datetime.now().isoformat(),
            "requirements": requirements
        }
        
        return {
            "success": True,
            "project_id": project_id,
            "message": "Proyecto en proceso de generación"
        }
    
    def generate_project_ai(self, project_id: str) -> Dict[str, Any]:
        """Execute AI generation pipeline for a project"""
        
        if project_id not in self.active_projects:
            return {
                "success": False,
                "error": "Proyecto no encontrado"
            }
        
        project = self.active_projects[project_id]
        requirements = project["requirements"]
        
        try:
            logger.info(f"Generando proyecto {project_id} con AI")
            
            # Execute AI pipeline
            result = self.supervisor.run_pipeline(project_id, requirements)
            
            # Update project status
            project["status"] = result["pipeline_status"]
            project["generated_at"] = datetime.now().isoformat()
            project["ai_result"] = result
            
            if result["pipeline_status"] == "completed":
                project["download_ready"] = True
                
                # Generate downloadable package
                download_path = self.download_service.create_project_package(
                    project_data=project,
                    project_id=project_id
                )
                project["download_path"] = download_path
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "status": "completed",
                    "agents_completed": result["agents_completed"],
                    "download_ready": True
                }
            else:
                return {
                    "success": False,
                    "project_id": project_id,
                    "status": "failed",
                    "error": "La generación AI falló",
                    "agents_completed": result["agents_completed"]
                }
                
        except Exception as e:
            logger.error(f"Error generando proyecto {project_id}: {e}")
            project["status"] = "failed"
            project["error"] = str(e)
            
            return {
                "success": False,
                "project_id": project_id,
                "error": f"Error en generación: {str(e)}"
            }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get current status of a project"""
        
        if project_id not in self.active_projects:
            return {
                "success": False,
                "error": "Proyecto no encontrado"
            }
        
        project = self.active_projects[project_id]
        
        return {
            "success": True,
            "project_id": project_id,
            "status": project.get("status", "unknown"),
            "name": project.get("name", ""),
            "created_at": project.get("created_at", ""),
            "download_ready": project.get("download_ready", False),
            "agents_completed": project.get("ai_result", {}).get("agents_completed", [])
        }
    
    def get_project_download(self, project_id: str) -> Optional[str]:
        """Get download path for completed project"""
        
        project = self.active_projects.get(project_id)
        if not project or not project.get("download_ready"):
            return None
        
        return project.get("download_path")
    
    def _get_user_project_count(self, user_id: str) -> int:
        """Get number of projects created by user this month (demo)"""
        current_month = datetime.now().strftime("%Y-%m")
        count = 0
        
        for project in self.active_projects.values():
            if project.get("user_id") == user_id:
                created_month = project.get("created_at", "")[:7]  # YYYY-MM
                if created_month == current_month:
                    count += 1
        
        return count
    
    def list_user_projects(self, user_id: str) -> list:
        """List all projects for a user"""
        user_projects = []
        
        for project_id, project in self.active_projects.items():
            if project.get("user_id") == user_id:
                user_projects.append({
                    "id": project_id,
                    "name": project.get("name", ""),
                    "status": project.get("status", ""),
                    "created_at": project.get("created_at", ""),
                    "download_ready": project.get("download_ready", False)
                })
        
        return sorted(user_projects, key=lambda x: x["created_at"], reverse=True)

# Global instance for easy access
ui_orchestrator = UIOrchestrator()
