from __future__ import annotations
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, constr

class ProjectCreate(BaseModel):
    user_id: constr
    project_name: constr
    requirements: constr

class ProjectOut(BaseModel):
    id: str
    user_id: str
    project_name: str
    requirements: str
    status: str
    # Puede venir como None, dict, list o incluso str "null" según ORM/driver:
    technology_stack: Optional[Any] = None
    generated_plan: Optional[str] = None
    result: Optional[str] = None   # existe en BD y en el modelo -> lo exponemos
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True  # compatible v1; en v2 muestra warning pero funciona
