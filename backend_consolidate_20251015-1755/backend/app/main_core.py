"""
Forge SaaS - Sistema Principal (Refactorizado para Asincronía)

Integración del núcleo de generación de proyectos REALES.
Se simula la ejecución asíncrona del Supervisor de Agentes en segundo plano.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import os
import time
import threading # Usaremos threading para simular el trabajo en segundo plano
import logging
from backend.app.routers.ai_analysis import router as ai_analysis_router 
from backend.app.routers import auth
from backend.app.routers import projects 
from backend.app.routers import ui_api


# Importar el NÚCLEO del sistema y el Supervisor
from backend.app.core.requirement_analyzer import RequirementAnalyzer
# Importamos ProjectSupervisor en lugar de ProjectGenerator, ya que es el orquestador
from backend.app.agents.supervisor_agent import ProjectSupervisor 
# Necesitamos la DB para interactuar con el supervisor y actualizar el estado
# NOTA: En un entorno real se usaría un sistema de colas (Celery, Redis Queue, etc.)
# Aquí simulamos la persistencia simple para que el supervisor funcione. 
from backend.app.core.db.session import SessionLocal # Asumiendo que esto está disponible



# Configuración de Logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Forge SaaS API",
    description="Sistema de generación de aplicaciones REALES asistido por IA",
    version="2.0.0"
)

# MONTAJE DE ROUTERS
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(projects.router, prefix="/api/v1/projects") 
app.include_router(ui_api.router, prefix="/api/v1/ui")

# 2. INCLUIR EL ROUTER DE ANÁLISIS DE AI
app.include_router(ai_analysis_router, prefix="/api/v1/ai") 

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el núcleo del sistema (solo el analizador es síncrono en la API)
analyzer = RequirementAnalyzer()
# El generador directo ya no se usa aquí, el supervisor lo orquesta

# Modelos Pydantic
class ProjectRequest(BaseModel):
    requirements: str
    project_name: str | None = None

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    specification: Dict[str, Any] | None = None
    project: Dict[str, Any] | None = None
    error: str | None = None

# Almacenamiento en memoria (debe ser reemplazado por la DB para consistencia)
projects_store = {}

# --- Funciones de Orquestación Asíncrona (Simulación) ---

def run_project_pipeline_in_background(project_id: str, requirements: Dict[str, Any]):
    """Función de trabajo que ejecuta el Supervisor en un hilo separado."""
    logger.info(f"Worker: Starting background pipeline for {project_id}")
    supervisor = ProjectSupervisor()
    try:
        # Aquí se inicia la lógica de la secuencia de agentes (el proceso largo)
        supervisor.run_pipeline(project_id, requirements)
        # La función run_pipeline ya actualiza el estado del proyecto en la DB
        logger.info(f"Worker: Pipeline finished successfully for {project_id}")
    except Exception as e:
        logger.error(f"Worker: Pipeline failed for {project_id}. Error: {e}")
        # Lógica de manejo de errores si la pipeline falla totalmente
    finally:
        # Cerramos la sesión de DB
        supervisor.db.close()

# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "message": "🚀 Forge SaaS - Sistema de Generación de Aplicaciones REALES",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "POST /api/analyze - Analizar requerimientos",
            "generate": "POST /api/generate - Iniciar generación de proyecto (asíncrono)",
            "projects": "GET /api/projects - Listar proyectos generados",
            "project_status": "GET /api/projects/{id}/status - Obtener estado del pipeline" # Nuevo endpoint sugerido
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "forge-saas",
        "version": "2.0.0"
    }

@app.post("/api/analyze", response_model=ProjectResponse)
async def analyze_requirements(request: ProjectRequest):
    """
    Analiza requerimientos del usuario y devuelve especificación técnica.
    Este paso se mantiene síncrono para respuesta rápida.
    """
    try:
        logger.info(f"🔍 Analizando requerimientos: {request.requirements[:50]}...")
        
        # Analizar requerimientos
        specification = await analyzer.analyze(request.requirements)
        
        # Crear ID de proyecto
        project_id = str(uuid.uuid4())
        
        # Guardar en almacenamiento (NOTA: Esto debe usar la DB real en el futuro)
        projects_store[project_id] = {
            "id": project_id,
            "name": request.project_name or specification.get("name", "New Project"),
            "requirements": request.requirements,
            "specification": specification,
            "status": "analyzed",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return ProjectResponse(
            project_id=project_id,
            status="analyzed",
            specification=specification
        )
        
    except Exception as e:
        logger.error(f"❌ Error en análisis: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error analizando requerimientos: {str(e)}"
        )

@app.post("/api/generate", status_code=status.HTTP_202_ACCEPTED, response_model=ProjectResponse)
async def generate_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """
    Inicia la generación de un proyecto COMPLETO y FUNCIONAL de forma asíncrona.
    Devuelve 202 Accepted. El cliente debe consultar el estado.
    """
    try:
        # Paso 1: Analizar requerimientos (si no se analizó antes)
        # Aquí re-analizamos si el cliente llama directamente, o podríamos requerir un project_id.
        specification = await analyzer.analyze(request.requirements)
        
        project_id = str(uuid.uuid4())
        project_name = request.project_name or specification.get("name", "Generated Project")

        # Paso 2: Crear el registro inicial en el almacenamiento/DB
        initial_project_data = {
            "id": project_id,
            "name": project_name,
            "requirements": request.requirements,
            "specification": specification,
            "status": "processing", # Estado clave: processing
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        projects_store[project_id] = initial_project_data
        
        # Paso 3: Iniciar el pipeline de agentes en segundo plano
        # Usamos threading aquí para simular un proceso de cola de trabajo
        
        # Creamos un diccionario de requisitos para el supervisor (debe incluir la spec)
        supervisor_requirements = {
            "raw_requirements": request.requirements,
            "specification": specification
        }
        
        worker_thread = threading.Thread(
            target=run_project_pipeline_in_background,
            args=(project_id, supervisor_requirements)
        )
        worker_thread.start()
        
        logger.info(f"🚀 Generación de proyecto {project_id} iniciada en segundo plano.")
        
        return ProjectResponse(
            project_id=project_id,
            status="processing", # Informamos al cliente del estado
            specification=specification
        )
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar la generación: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al iniciar la generación del proyecto: {str(e)}"
        )

# --- Endpoints de Listado y Recuperación (simplificados) ---

@app.get("/api/projects")
async def list_projects():
    """Lista todos los proyectos generados/en proceso"""
    return {
        "projects": [
            {
                "id": p_id,
                "name": p.get("name", "Unnamed"),
                "status": p["status"],
                "type": p.get("specification", {}).get("project_type", "unknown"),
                "created_at": p.get("created_at", "N/A")
            }
            for p_id, p in projects_store.items()
        ]
    }

@app.get("/api/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """Obtiene el estado detallado del proyecto (incluyendo runs de agentes)"""
    if project_id not in projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Aquí es donde realmente se consulta la DB/ProjectSupervisor
    supervisor = ProjectSupervisor()
    try:
        agent_status = supervisor.get_agent_status(project_id)
        current_status = projects_store[project_id]["status"] # Estado general del proyecto
        
        # Unimos el estado general con el detalle del pipeline
        return {
            "id": project_id,
            "name": projects_store[project_id]["name"],
            "status": current_status,
            "pipeline_details": agent_status["agent_runs"]
        }
    finally:
        supervisor.db.close()


# Incluir rutas de la UI API si existen (asumiendo que ui_api_router está definido en otro lugar)
# from core.routers.ui_api import router as ui_api_router
# app.include_router(ui_api_router)

if __name__ == "__main__":
    import uvicorn
    # NOTA: En producción, usar `gunicorn` con `uvicorn.workers.UvicornWorker`
    # para asegurar que los BackgroundTasks funcionen correctamente o usar Celery.
    uvicorn.run(app, host="0.0.0.0", port=8000)
