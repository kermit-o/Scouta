from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import time
from datetime import datetime
import json

app = FastAPI(
    title="Forge SaaS API - FINAL WORKING VERSION",
    description="API completa para generación automática de proyectos de software",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento mejorado
projects_db = {}

class ProjectRequest(BaseModel):
    project_name: str
    project_type: str = "web_app"
    description: str

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str
    project_data: Optional[Dict[str, Any]] = None

print("🚀 INICIANDO FORGE SAAS - VERSIÓN FINAL")
print("🤖 CARGANDO AGENTE DE PLANIFICACIÓN...")

# Cargar el PlanningAgent standalone
try:
    from core.agents.planning_agent import PlanningAgent
    planner = PlanningAgent()
    AGENT_LOADED = True
    AGENT_NAME = "PlanningAgent"
    print(f"✅ {AGENT_NAME} cargado exitosamente")
except Exception as e:
    print(f"❌ Error cargando PlanningAgent: {e}")
    AGENT_LOADED = False
    AGENT_NAME = "NoAgent"
    planner = None

@app.get("/")
async def root():
    return {
        "message": "🚀 Forge SaaS API - Sistema Operativo",
        "version": "2.0.0",
        "planner_loaded": AGENT_LOADED,
        "planner_name": AGENT_NAME,
        "status": "operational",
        "endpoints_available": [
            "POST /api/projects - Crear proyecto",
            "POST /api/projects/{id}/plan - Generar plan",
            "GET /api/projects/{id} - Consultar proyecto", 
            "GET /api/projects - Listar proyectos"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "planner_loaded": AGENT_LOADED,
        "timestamp": datetime.now().isoformat(),
        "projects_count": len(projects_db)
    }

@app.get("/api/agents/status")
async def agents_status():
    """Estado de los agentes de IA"""
    return {
        "planner": {
            "loaded": AGENT_LOADED,
            "name": AGENT_NAME,
            "status": "active" if AGENT_LOADED else "unavailable",
            "capabilities": ["project_planning", "tech_stack_recommendation", "development_steps"] if AGENT_LOADED else []
        }
    }

@app.post("/api/projects", status_code=201)
async def create_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Crear un nuevo proyecto y generar plan automáticamente"""
    try:
        project_id = str(uuid.uuid4())
        
        project_data = {
            "project_id": project_id,
            "name": request.project_name,
            "type": request.project_type,
            "description": request.description,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "planner_available": AGENT_LOADED,
            "planner_name": AGENT_NAME
        }
        
        projects_db[project_id] = project_data
        
        # Función para generación en background
        def generate_project_background(pid):
            try:
                projects_db[pid]["status"] = "generating"
                projects_db[pid]["generation_started"] = datetime.now().isoformat()
                
                # Usar el planner si está disponible
                if AGENT_LOADED and planner:
                    plan_result = planner.create_development_plan({
                        "description": request.description,
                        "project_type": request.project_type
                    })
                    projects_db[pid]["plan"] = plan_result
                    projects_db[pid]["plan_generated"] = True
                    projects_db[pid]["plan_status"] = plan_result.get("status", "unknown")
                
                projects_db[pid]["status"] = "completed"
                projects_db[pid]["completed_at"] = datetime.now().isoformat()
                projects_db[pid]["generation_ended"] = datetime.now().isoformat()
                
            except Exception as e:
                projects_db[pid]["status"] = "error"
                projects_db[pid]["error"] = str(e)
                projects_db[pid]["error_at"] = datetime.now().isoformat()
        
        # Iniciar generación en background
        background_tasks.add_task(generate_project_background, project_id)
        
        return ProjectResponse(
            project_id=project_id,
            status="created",
            message=f"Proyecto '{request.project_name}' creado exitosamente. Generación de plan en proceso.",
            project_data=project_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {str(e)}")

@app.post("/api/projects/{project_id}/plan")
async def generate_plan(project_id: str):
    """Generar plan de desarrollo para un proyecto específico"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if not AGENT_LOADED:
        raise HTTPException(status_code=503, detail="Agente de planificación no disponible")
    
    try:
        project = projects_db[project_id]
        
        # Generar plan usando el agente
        plan_result = planner.create_development_plan({
            "description": project["description"],
            "project_type": project["type"]
        })
        
        # Actualizar proyecto con el nuevo plan
        projects_db[project_id]["plan"] = plan_result
        projects_db[project_id]["plan_generated"] = True
        projects_db[project_id]["plan_updated"] = datetime.now().isoformat()
        projects_db[project_id]["plan_status"] = plan_result.get("status", "unknown")
        
        return {
            "project_id": project_id,
            "status": "success",
            "plan": plan_result,
            "message": "Plan de desarrollo generado exitosamente",
            "timestamp": datetime.now().isoformat()
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando plan: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Obtener información detallada de un proyecto"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project = projects_db[project_id]
    
    # Enriquecer respuesta con información del plan
    response_data = {**project}
    
    if "plan" in project:
        plan = project["plan"]
        response_data["plan_summary"] = {
            "status": plan.get("status"),
            "project_type": plan.get("project_type"),
            "summary": plan.get("summary"),
            "estimated_time": plan.get("estimated_time"),
            "has_architecture": "architecture" in plan.get("plan", {}),
            "has_tech_stack": "tech_stack" in plan.get("plan", {}),
            "development_phases": len(plan.get("plan", {}).get("development_steps", [])),
            "project_components": len(plan.get("plan", {}).get("project_structure", []))
        }
    
    return response_data

@app.get("/api/projects")
async def list_projects():
    """Listar todos los proyectos"""
    projects_list = list(projects_db.values())
    
    # Estadísticas
    stats = {
        "total": len(projects_list),
        "by_status": {},
        "with_plans": 0,
        "successful_plans": 0
    }
    
    for project in projects_list:
        status = project.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        if project.get("plan_generated", False):
            stats["with_plans"] += 1
            
        if project.get("plan_status") == "success":
            stats["successful_plans"] += 1
    
    return {
        "projects": projects_list,
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/projects/{project_id}/plan/details")
async def get_plan_details(project_id: str):
    """Obtener detalles específicos del plan de desarrollo"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project = projects_db[project_id]
    
    if "plan" not in project:
        raise HTTPException(status_code=404, detail="Plan no generado para este proyecto")
    
    plan_data = project["plan"].get("plan", {})
    
    return {
        "project_id": project_id,
        "project_name": project.get("name"),
        "plan_status": project["plan"].get("status"),
        "plan_details": {
            "project_structure": plan_data.get("project_structure", []),
            "tech_stack": plan_data.get("tech_stack", {}),
            "development_steps": plan_data.get("development_steps", []),
            "architecture": plan_data.get("architecture", {}),
            "file_structure": plan_data.get("file_structure", {}),
            "dependencies": plan_data.get("dependencies", {})
        },
        "summary": project["plan"].get("summary"),
        "estimated_time": project["plan"].get("estimated_time")
    }

if __name__ == "__main__":
    import uvicorn
    print("🎯 Forge SaaS API - LISTA PARA USAR")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
