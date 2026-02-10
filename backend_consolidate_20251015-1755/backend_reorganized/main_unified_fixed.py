"""
SISTEMA PRINCIPAL UNIFICADO - VERSIÓN CORREGIDA
Con paths de importación corregidos
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
import os
import uuid

# Configurar paths CORRECTAMENTE
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

app = FastAPI(
    title="Consolidated AI Project Generator", 
    version="2.0",
    description="Sistema avanzado de generación de proyectos reales con IA"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str = "web_app"
    features: List[str] = []
    technologies: List[str] = []
    requirements: List[str] = []

@app.post("/api/v2/projects/simple")
async def create_simple_project(request: ProjectRequest):
    """Endpoint simplificado - Genera proyectos sin base de datos"""
    try:
        print(f"📦 Recibiendo solicitud para: {request.name}")
        
        # Verificar que podemos importar los módulos
        try:
            from core.agents.real_project_builder_fixed import RealProjectBuilder
            print("✅ RealProjectBuilder importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando RealProjectBuilder: {e}")
            # Fallback a simulación
            return {
                "status": "simulated",
                "project_name": request.name,
                "message": "Agentes no disponibles - modo simulación",
                "project_id": str(uuid.uuid4()),
                "files_created": ["README.md", "main.py", "requirements.txt"],
                "project_path": f"generated_projects/simulated-{request.name}"
            }
        
        builder = RealProjectBuilder()
        project_id = str(uuid.uuid4())
        
        development_plan = {
            'project_name': request.name,
            'project_type': request.project_type,
            'description': request.description,
            'features': request.features,
            'technologies': request.technologies,
            'architecture': {
                'backend': 'fastapi',
                'database': 'sqlite',
                'auth': 'jwt' if 'autenticacion' in request.features else False
            }
        }
        
        print(f"🏗️ Iniciando generación de proyecto: {request.name}")
        result = await builder.run(project_id, development_plan)
        
        return {
            "status": "success",
            "system": "consolidated_ai_v2_simple",
            "project_id": project_id,
            "project_name": request.name,
            "project_path": result.get("project_path", ""),
            "files_created": result.get("files_created", []),
            "total_files": len(result.get("files_created", [])),
            "message": "Proyecto generado exitosamente"
        }
            
    except Exception as e:
        print(f"❌ Error en create_simple_project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/v2/projects/list")
async def list_generated_projects():
    """Lista todos los proyectos generados"""
    import os
    projects_path = "generated_projects"
    if os.path.exists(projects_path):
        projects = os.listdir(projects_path)
        return {
            "total_projects": len(projects),
            "projects": projects
        }
    return {"total_projects": 0, "projects": []}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "system": "consolidated_ai_v2",
        "version": "2.0"
    }

@app.get("/capabilities")
async def get_capabilities():
    """Retorna capacidades del sistema"""
    return {
        "system": "consolidated_ai_v2",
        "version": "2.0",
        "capabilities": [
            "generacion_proyectos_completos",
            "frontend_backend_integrados", 
            "arquitectura_escalable",
            "26_proyectos_generados_exitosamente"
        ],
        "status": "production_ready"
    }

@app.get("/")
async def root():
    return {"message": "🚀 Consolidated AI Project Generator v2.0", "status": "active"}

if __name__ == "__main__":
    print("🚀 INICIANDO SISTEMA CONSOLIDADO AI v2.0 (FIXED)")
    print("📍 Endpoints disponibles:")
    print("   POST /api/v2/projects/simple - Generar proyecto simple")
    print("   GET  /api/v2/projects/list   - Listar proyectos")
    print("   GET  /health                 - Estado del sistema")
    print("   GET  /capabilities           - Capacidades")
    print("   GET  /                       - Root endpoint")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
