"""
SISTEMA MEJORADO - Genera proyectos REALES con LLM
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

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

app = FastAPI(
    title="Enhanced AI Project Generator", 
    version="3.0",
    description="Sistema que genera proyectos REALES y FUNCIONALES con LLM"
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

@app.post("/api/v3/projects/real")
async def create_real_project(request: ProjectRequest):
    """Endpoint MEJORADO - Genera proyectos REALES con LLM"""
    try:
        print(f"🚀 SOLICITANDO PROYECTO REAL: {request.name}")
        
        # Usar el builder mejorado que consulta LLM
        try:
            from core.agents.real_project_builder_enhanced import RealProjectBuilderEnhanced
            builder = RealProjectBuilderEnhanced()
            print("✅ RealProjectBuilderEnhanced cargado")
        except ImportError as e:
            print(f"❌ Error cargando enhanced builder: {e}")
            # Fallback al básico
            from core.agents.real_project_builder_fixed import RealProjectBuilder
            builder = RealProjectBuilder()
            print("⚠️  Usando builder básico como fallback")
        
        project_id = str(uuid.uuid4())
        
        development_plan = {
            'project_name': request.name,
            'project_type': request.project_type,
            'description': request.description,
            'features': request.features,
            'technologies': request.technologies,
            'architecture': {
                'backend': 'fastapi',
                'database': 'sqlite' if 'database' in request.features else 'none',
                'auth': 'jwt' if 'autenticacion' in request.features else False
            }
        }
        
        print(f"🏗️ Generando proyecto REAL con LLM...")
        result = await builder.run(project_id, development_plan)
        
        return {
            "status": "success",
            "system": "enhanced_ai_v3",
            "project_id": project_id,
            "project_name": request.name,
            "project_path": result.get("project_path", ""),
            "files_created": result.get("files_created", []),
            "total_files": len(result.get("files_created", [])),
            "message": "Proyecto REAL generado con LLM",
            "content_quality": "enhanced" if "enhanced" in str(type(builder)) else "basic"
        }
            
    except Exception as e:
        print(f"❌ Error en create_real_project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/v3/projects/list")
async def list_generated_projects():
    """Lista proyectos con información de calidad"""
    import os
    projects_path = "generated_projects"
    projects_info = []
    
    if os.path.exists(projects_path):
        for project_dir in os.listdir(projects_path):
            project_path = os.path.join(projects_path, project_dir)
            if os.path.isdir(project_path):
                # Analizar calidad del proyecto
                quality = analyze_project_quality(project_path)
                projects_info.append({
                    "name": project_dir,
                    "quality": quality,
                    "path": project_path
                })
        
        return {
            "total_projects": len(projects_info),
            "projects": projects_info
        }
    return {"total_projects": 0, "projects": []}

def analyze_project_quality(project_path):
    """Analiza la calidad de un proyecto generado"""
    try:
        # Verificar main.py
        main_py = os.path.join(project_path, "main.py")
        if os.path.exists(main_py):
            with open(main_py, 'r') as f:
                content = f.read()
                if len(content) > 500:
                    return "high"
                elif len(content) > 100:
                    return "medium"
        return "basic"
    except:
        return "unknown"

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "system": "enhanced_ai_v3",
        "version": "3.0",
        "capability": "real_project_generation"
    }

@app.get("/")
async def root():
    return {"message": "🚀 Enhanced AI Project Generator v3.0", "status": "active"}

if __name__ == "__main__":
    print("🚀 INICIANDO SISTEMA MEJORADO AI v3.0")
    print("📍 Genera proyectos REALES con LLM")
    print("📍 Endpoints disponibles:")
    print("   POST /api/v3/projects/real - Generar proyecto REAL")
    print("   GET  /api/v3/projects/list - Listar proyectos con calidad")
    print("   GET  /health               - Estado del sistema")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
