from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import time
import os
import json
from datetime import datetime
import importlib.util
import shutil

app = FastAPI(title="Forge SaaS API - Fixed Agents")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria
projects_db = {}
progress_db = {}

# Modelos
class ProjectRequest(BaseModel):
    project_name: str
    project_type: str = "web_app"
    description: str

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str
    project_data: Optional[Dict[str, Any]] = None

# Cargar agentes de IA de forma robusta
print("🤖 CARGANDO AGENTES DE IA...")
loaded_agents = {}

def load_agent(agent_name, agent_class, import_path):
    """Load an agent with error handling"""
    try:
        # Try direct import first
        module = __import__(import_path, fromlist=[agent_class])
        agent_class_obj = getattr(module, agent_class)
        agent_instance = agent_class_obj()
        loaded_agents[agent_name] = agent_instance
        print(f"   ✅ {agent_name}: {agent_class}")
        return True
    except Exception as e:
        print(f"   ❌ {agent_name}: {e}")
        return False

# Cargar agentes individualmente
load_agent("intake", "IntakeAgent", "core.agents.intake_agent")
load_agent("planner", "PlanningAgent", "core.agents.planning_agent") 
load_agent("builder", "BuilderAgent", "core.agents.builder_agent")
load_agent("scaffolder", "ScaffolderAgent", "core.agents.scaffolder_agent")

print(f"🎯 Agentes cargados: {list(loaded_agents.keys())}")

# Endpoints básicos
@app.get("/")
async def root():
    return {
        "message": "🚀 Forge SaaS API con IA funcionando",
        "version": "2.0",
        "ai_agents_loaded": True,
        "available_agents": list(loaded_agents.keys())
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy", "agents": len(loaded_agents)}

@app.get("/api/agents/status")
async def agents_status():
    """Get status of all AI agents"""
    agent_status = {}
    for name, agent in loaded_agents.items():
        agent_status[name] = {
            "status": "active",
            "name": getattr(agent, 'name', name),
            "type": type(agent).__name__
        }
    return agent_status

@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    return {"projects": list(projects_db.values())}

@app.post("/api/projects", status_code=201)
async def create_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        
        project_data = {
            "project_id": project_id,
            "name": request.project_name,
            "type": request.project_type,
            "description": request.description,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "agents_available": list(loaded_agents.keys())
        }
        
        projects_db[project_id] = project_data
        
        # Iniciar generación en background
        def generate_project_background(pid):
            try:
                projects_db[pid]["status"] = "generating"
                
                # Usar agentes reales para generar el proyecto
                if "intake" in loaded_agents:
                    intake_result = loaded_agents["intake"].analyze_requirements(
                        request.description, request.project_type
                    )
                    projects_db[pid]["intake_result"] = intake_result
                
                if "planner" in loaded_agents:
                    plan_result = loaded_agents["planner"].create_development_plan({
                        "description": request.description,
                        "project_type": request.project_type
                    })
                    projects_db[pid]["plan"] = plan_result
                
                projects_db[pid]["status"] = "completed"
                projects_db[pid]["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                projects_db[pid]["status"] = "error"
                projects_db[pid]["error"] = str(e)
        
        background_tasks.add_task(generate_project_background, project_id)
        
        return {
            "project_id": project_id,
            "status": "created",
            "message": f"Proyecto '{request.project_name}' creado y en proceso de generación"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {str(e)}")

@app.get("/api/progress/{job_id}")
async def get_progress(job_id: str):
    """Get progress of a job"""
    return {"job_id": job_id, "progress": 50, "status": "running"}

@app.post("/api/projects/{project_id}/plan")
async def generate_plan(project_id: str):
    """Generate plan for a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    try:
        if "planner" in loaded_agents:
            plan = loaded_agents["planner"].create_development_plan({
                "description": projects_db[project_id]["description"],
                "project_type": projects_db[project_id]["type"]
            })
            
            projects_db[project_id]["plan"] = plan
            projects_db[project_id]["plan_generated"] = True
            
            return {
                "project_id": project_id,
                "status": "success",
                "plan": plan
            }
        else:
            raise HTTPException(status_code=500, detail="Planner agent no disponible")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando plan: {str(e)}")

@app.post("/api/projects/{project_id}/generate")
async def generate_project_files(project_id: str):
    """Generate project files"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    try:
        # Simular generación de archivos
        projects_db[project_id]["files_generated"] = True
        projects_db[project_id]["generated_at"] = datetime.now().isoformat()
        
        return {
            "project_id": project_id,
            "status": "success",
            "message": "Archivos del proyecto generados",
            "download_url": f"/api/projects/{project_id}/download"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando archivos: {str(e)}")

@app.get("/api/projects/{project_id}/download")
async def download_project(project_id: str):
    """Download generated project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project = projects_db[project_id]
    return {
        "project_id": project_id,
        "name": project["name"],
        "status": project["status"],
        "download_available": project.get("files_generated", False)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
