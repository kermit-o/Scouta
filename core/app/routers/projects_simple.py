from fastapi import APIRouter, HTTPException
from typing import List
import uuid

router = APIRouter()

# Datos de ejemplo
sample_projects = [
    {"id": str(uuid.uuid4()), "name": "Proyecto Demo 1", "requirements": "Requerimientos demo 1", "status": "pending"},
    {"id": str(uuid.uuid4()), "name": "Proyecto Demo 2", "requirements": "Requerimientos demo 2", "status": "running"}
]

@router.get("/")
async def list_projects():
    return sample_projects

@router.post("/")
async def create_project(project_data: dict):
    new_project = {
        "id": str(uuid.uuid4()),
        "name": project_data.get("name", "Nuevo proyecto"),
        "requirements": project_data.get("requirements", ""),
        "status": "pending"
    }
    sample_projects.append(new_project)
    return new_project

@router.get("/{project_id}")
async def get_project(project_id: str):
    for project in sample_projects:
        if project["id"] == project_id:
            return project
    raise HTTPException(status_code=404, detail="Project not found")

@router.get("/health/check")
async def health_check():
    return {"status": "healthy", "service": "projects-api"}
