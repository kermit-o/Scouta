import logging
import uuid
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.core.app.services.real_generator import real_generator
from backend.app.core.app.agents.supervisor_simple import ProjectSupervisorSimple
from backend.app.core.app.services.payment_service import PaymentService, PlanType

logger = logging.getLogger(__name__)

class UIOrchestratorReal:
    """Orchestrates REAL project generation from UI to downloadable package"""
    
    def __init__(self):
        self.supervisor = ProjectSupervisorSimple()
        self.real_generator = real_generator
        self.payment_service = PaymentService()
        self.active_projects = {}
    
    def create_project(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project with REAL code generation"""
        
        project_name = user_data.get('project_name', 'Mi Proyecto')
        description = user_data.get('description', '')
        user_id = user_data.get('user_id', 'demo_user')
        
        if not description:
            return {
                "success": False,
                "error": "Por favor proporciona una descripción del proyecto"
            }
        
        # Create project spec from description
        project_spec = self._create_project_spec(description, project_name)
        project_id = str(uuid.uuid4())
        
        # Store project
        self.active_projects[project_id] = {
            "id": project_id,
            "name": project_name,
            "description": description,
            "spec": project_spec,
            "status": "generating",
            "created_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        return {
            "success": True,
            "project_id": project_id,
            "message": "Proyecto creado - Generando código real..."
        }
    
    def generate_real_project(self, project_id: str) -> Dict[str, Any]:
        """Generate REAL, functional code for the project"""
        
        if project_id not in self.active_projects:
            return {"success": False, "error": "Proyecto no encontrado"}
        
        project = self.active_projects[project_id]
        
        try:
            logger.info(f"Generando proyecto REAL {project_id}")
            
            # Generate complete project with REAL code
            generation_result = self.real_generator.generate_complete_project(project["spec"])
            
            if generation_result["success"]:
                # Create downloadable package
                zip_path = self.real_generator.create_downloadable_package(generation_result)
                
                # Update project
                project["status"] = "completed"
                project["generated_at"] = datetime.now().isoformat()
                project["generation_result"] = generation_result
                project["download_path"] = zip_path
                project["file_count"] = generation_result["file_count"]
                project["download_ready"] = True
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "status": "completed",
                    "file_count": generation_result["file_count"],
                    "download_ready": True,
                    "download_path": zip_path
                }
            else:
                project["status"] = "failed"
                project["error"] = generation_result.get("error", "Error desconocido")
                return {
                    "success": False,
                    "error": generation_result.get("error", "Error en generación")
                }
                
        except Exception as e:
            logger.error(f"Error generando proyecto REAL {project_id}: {e}")
            project["status"] = "failed"
            project["error"] = str(e)
            return {
                "success": False,
                "error": f"Error en generación: {str(e)}"
            }
    
    def _create_project_spec(self, description: str, project_name: str) -> Dict[str, Any]:
        """Create project specification from user description"""
        
        # Analyze description to determine entities and features
        # For now, create a basic spec - this would be enhanced with AI analysis
        entities = self._extract_entities_from_description(description)
        
        return {
            "name": project_name.lower().replace(" ", "_"),
            "description": description,
            "main_entities": entities,
            "type": "web_application",
            "features": ["rest_api", "database", "web_interface"]
        }
    
    def _extract_entities_from_description(self, description: str) -> List[Dict[str, Any]]:
        """Extract main entities from project description"""
        
        description_lower = description.lower()
        entities = []
        
        # Basic entity detection from common patterns
        if any(word in description_lower for word in ["usuario", "user", "cuenta"]):
            entities.append({
                "name": "User",
                "fields": [
                    {"name": "id", "type": "int", "primary_key": True},
                    {"name": "username", "type": "str", "unique": True},
                    {"name": "email", "type": "str", "unique": True},
                    {"name": "password_hash", "type": "str"},
                    {"name": "created_at", "type": "datetime"}
                ]
            })
        
        if any(word in description_lower for word in ["producto", "product", "item"]):
            entities.append({
                "name": "Product",
                "fields": [
                    {"name": "id", "type": "int", "primary_key": True},
                    {"name": "name", "type": "str"},
                    {"name": "description", "type": "str"},
                    {"name": "price", "type": "float"},
                    {"name": "created_at", "type": "datetime"}
                ]
            })
        
        if any(word in description_lower for word in ["orden", "order", "pedido"]):
            entities.append({
                "name": "Order",
                "fields": [
                    {"name": "id", "type": "int", "primary_key": True},
                    {"name": "user_id", "type": "int", "foreign_key": "User.id"},
                    {"name": "total_amount", "type": "float"},
                    {"name": "status", "type": "str"},
                    {"name": "created_at", "type": "datetime"}
                ]
            })
        
        if any(word in description_lower for word in ["categoria", "category"]):
            entities.append({
                "name": "Category",
                "fields": [
                    {"name": "id", "type": "int", "primary_key": True},
                    {"name": "name", "type": "str", "unique": True},
                    {"name": "description", "type": "str"}
                ]
            })
        
        # Default entities if none detected
        if not entities:
            entities = [
                {
                    "name": "Example",
                    "fields": [
                        {"name": "id", "type": "int", "primary_key": True},
                        {"name": "name", "type": "str"},
                        {"name": "description", "type": "str"},
                        {"name": "created_at", "type": "datetime"}
                    ]
                }
            ]
        
        return entities
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project status"""
        if project_id not in self.active_projects:
            return {"success": False, "error": "Proyecto no encontrado"}
        
        project = self.active_projects[project_id]
        return {
            "success": True,
            "project_id": project_id,
            "status": project.get("status", "unknown"),
            "name": project.get("name", ""),
            "file_count": project.get("file_count", 0),
            "download_ready": project.get("download_ready", False)
        }
    
    def get_project_download(self, project_id: str) -> Optional[str]:
        """Get download path for completed project"""
        project = self.active_projects.get(project_id)
        return project.get("download_path") if project and project.get("download_ready") else None

# Global instance
ui_orchestrator_real = UIOrchestratorReal()
