from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class PlanFile(BaseModel):
    path: str
    template: Optional[str] = None
    content: Optional[str] = None

class PlanJson(BaseModel):
    project_name: Optional[str] = None
    stack: Optional[str] = None
    structure: Optional[List[PlanFile]] = None
    dependencies: Optional[List[Dict[str, Any]]] = None
    variables: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"
