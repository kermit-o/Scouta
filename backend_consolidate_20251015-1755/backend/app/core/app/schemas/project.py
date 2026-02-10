from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from backend.app.core.models.project import ProjectStatus

class ProjectRequirements(BaseModel):
    name: str
    requirements: str  # Cambiado de dict a str

class ProjectResponse(BaseModel):
    id: UUID 
    name: str
    status: Optional[str] = ProjectStatus.pending.value
    requirements: Optional[str] = None  # Cambiado de dict a str
    plan_json: Optional[Dict[str, Any]] = None
    technology_stack: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    artifact_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RunResponse(BaseModel):
    queued: bool
    project_id: Optional[str] = None
    agents: Optional[int] = None
    message: Optional[str] = None
