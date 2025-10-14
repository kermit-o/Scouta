#!/usr/bin/env python3
"""
Forge SaaS - Sistema de generación de proyectos via IA
Versión corregida de imports
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv 

load_dotenv()

# IMPORTS CORREGIDOS - usar la ruta correcta
try:
    from core.core.project_factory import ProjectRequirements, ProjectType
    print("✅ Imports de core.core funcionan")
except ImportError as e:
    print(f"❌ Error importando de core.core: {e}")
    # Fallback a backend
    try:
        from backend.app.project_factory import ProjectRequirements, ProjectType
        print("✅ Imports de backend funcionan")
    except ImportError as e2:
        print(f"❌ Error importando de backend: {e2}")
        # Definir clases básicas como último recurso
        from enum import Enum
        class ProjectType(Enum):
            WEB_APP = "web_app"
            MOBILE = "mobile" 
            API = "api"
            DESKTOP = "desktop"
        
        class ProjectRequirements(BaseModel):
            name: str
            description: str
            project_type: ProjectType

app = FastAPI(title="Forge SaaS API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🚀 Forge SaaS API funcionando", "version": "1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "forge-saas"}

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str

@app.post("/api/projects")
async def create_project(request: ProjectRequest):
    try:
        project_type = ProjectType(request.project_type)
        requirements = ProjectRequirements(
            name=request.name,
            description=request.description,
            project_type=project_type
        )
        return {
            "id": "proj_123",
            "name": requirements.name,
            "status": "created",
            "message": f"Proyecto {requirements.name} creado exitosamente"
        }
    except ValueError:
        available_types = [pt.value for pt in ProjectType]
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de proyecto inválido. Tipos disponibles: {available_types}"
        )

@app.get("/api/projects")
async def list_projects():
    return [
        {
            "id": "proj_123", 
            "name": "Mi Primer Proyecto",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
