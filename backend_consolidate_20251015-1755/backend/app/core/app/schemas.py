from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class RequirementsIn(BaseModel):
    requirements: dict

class ProjectOut(BaseModel):
    id: str
    name: str
    status: str
    requirements: Optional[dict] = None
    plan_json: Optional[dict] = None
    generated_plan: Optional[dict] = None
    technology_stack: Optional[dict] = None
    result: Optional[dict] = None
    artifact_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # (Pydantic v2) / orm_mode=True si usas v1
