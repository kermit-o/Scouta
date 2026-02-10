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

# Importar routers de API
from api.v1 import ai_analysis, auth, billing, payments, projects, ui_api

app = FastAPI(title="Forge SaaS API - Enhanced with AI Agents")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de API
app.include_router(ai_analysis.router, prefix="/api/v1/ai-analysis", tags=["AI Analysis"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(ui_api.router, prefix="/api/v1/ui-api", tags=["UI API"])

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

# Cargar agentes de IA
print("🤖 CARGANDO AGENTES DE IA...")
loaded_agents = {}

try:
    from core.agents.intake_agent import IntakeAgent
    loaded_agents["intake"] = IntakeAgent()
    print("   ✅ intake: IntakeAgent")
except Exception as e:
    print(f"   ❌ Error cargando intake: {e}")

try:
    from core.agents.planning_agent import PlanningAgent
    loaded_agents["planner"] = PlanningAgent()
    print("   ✅ planner: PlanningAgent")
except Exception as e:
    print(f"   ❌ Error cargando planner: {e}")

try:
    from core.agents.builder_agent import BuilderAgent
    loaded_agents["builder"] = BuilderAgent()
    print("   ✅ builder: BuilderAgent")
except Exception as e:
    print(f"   ❌ Error cargando builder: {e}")

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

@app.get("/health")
async def health():
    return {"status": "healthy", "agents": len(loaded_agents)}

# Endpoint simple de generación de proyectos (backward compatibility)
@app.post("/api/generate-project")
async def generate_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    try:
        project_id = str(uuid.uuid4())
        
        # Simular generación de proyecto
        project_data = {
            "project_id": project_id,
            "name": request.project_name,
            "type": request.project_type,
            "description": request.description,
            "status": "generating",
            "created_at": datetime.now().isoformat()
        }
        
        projects_db[project_id] = project_data
        
        # Simular proceso en background
        def simulate_generation(pid):
            time.sleep(2)
            projects_db[pid]["status"] = "completed"
            projects_db[pid]["completed_at"] = datetime.now().isoformat()
        
        background_tasks.add_task(simulate_generation, project_id)
        
        return ProjectResponse(
            project_id=project_id,
            status="started",
            message=f"Generación de proyecto '{request.project_name}' iniciada",
            project_data=project_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando proyecto: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return projects_db[project_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
