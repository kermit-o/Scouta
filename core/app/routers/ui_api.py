from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
from typing import Dict, Any
import uuid
import os

from core.services.ui_orchestrator import ui_orchestrator

router = APIRouter(prefix="/api/ui", tags=["UI API"])
logger = logging.getLogger(__name__)

@router.post("/projects")
async def create_project(project_data: Dict[str, Any]):
    """Create a new project from UI"""
    try:
        result = ui_orchestrator.create_project(project_data)
        
        if result["success"]:
            # Start background generation
            project_id = result["project_id"]
            
            return {
                "success": True,
                "project_id": project_id,
                "message": "Proyecto creado exitosamente"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
            
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/generate")
async def generate_project(project_id: str, background_tasks: BackgroundTasks):
    """Generate project with AI"""
    try:
        # This would typically be a background task
        result = ui_orchestrator.generate_project_ai(project_id)
        
        if result["success"]:
            return {
                "success": True,
                "project_id": project_id,
                "status": result["status"],
                "agents_completed": result.get("agents_completed", [])
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Error en generación"))
            
    except Exception as e:
        logger.error(f"Error generating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """Get project generation status"""
    try:
        result = ui_orchestrator.get_project_status(project_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Proyecto no encontrado"))
            
    except Exception as e:
        logger.error(f"Error getting status for {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/download")
async def download_project(project_id: str):
    """Download generated project"""
    try:
        download_path = ui_orchestrator.get_project_download(project_id)
        
        if download_path and os.path.exists(download_path):
            return FileResponse(
                path=download_path,
                filename=f"project_{project_id}.zip",
                media_type='application/zip'
            )
        else:
            raise HTTPException(status_code=404, detail="Proyecto no disponible para descarga")
            
    except Exception as e:
        logger.error(f"Error downloading project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/projects")
async def list_user_projects(user_id: str):
    """List all projects for a user"""
    try:
        projects = ui_orchestrator.list_user_projects(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        logger.error(f"Error listing projects for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
