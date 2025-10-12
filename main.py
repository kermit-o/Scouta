from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

# Es CRÍTICO que la carga de variables de entorno se haga aquí (asumo que estaba antes)
from dotenv import load_dotenv 
load_dotenv() 

from core.project_factory import ProjectRequirements, ProjectType
from core.enhanced_project_factory import EnhancedProjectFactory
from config.settings import settings
# REMOVIDO: agents.deepseek_client, ya que se usa dentro del router

# Importar Routers
from core.app.routers import auth
# Asumo que existe un router projects.py
# from core.app.routers import projects 

# IMPORTACIÓN DEL NUEVO ROUTER DE ANÁLISIS
from core.app.routers.ai_analysis import router as ai_analysis_router 


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced factory
project_factory = EnhancedProjectFactory(openai_api_key=settings.OPENAI_API_KEY)

# Esquemas de Proyectos
# Estos esquemas pueden permanecer aquí o moverse a core/app/schemas/project.py
class CreateProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str
    features: List[str] = []
    technologies: List[str] = []
    database: str = "postgresql"
    auth_required: bool = True
    payment_integration: bool = False
    deployment_target: str = "vercel"

class ProjectResponse(BaseModel):
    success: bool
    project_id: str
    project_name: str
    project_path: Optional[str] = None
    project_type: str
    features_implemented: List[str] = []
    next_steps: List[str] = []
    error: Optional[str] = None
    generated_at: Optional[str] = None

# REMOVIDOS: AnalyzeIdeaRequest y AnalyzeIdeaResponse, ahora están en ai_analysis.py


# Configuración para servir la UI estática
UI_BUILD_PATH = "forge_ui/dist"

if os.path.exists(UI_BUILD_PATH):
    app.mount("/assets", StaticFiles(directory=f"{UI_BUILD_PATH}/assets"), name="assets")
    
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(UI_BUILD_PATH, "index.html"))
    
    @app.get("/{full_path:path}")
    async def serve_spa_routes(full_path: str):
        file_path = os.path.join(UI_BUILD_PATH, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(UI_BUILD_PATH, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "UI no construida"}

# ------------------------------------------------------------------
# MONTAJE DE ROUTERS MODULARIZADOS
# ------------------------------------------------------------------

# Router de Auth
app.include_router(auth.router, prefix="/api/v1/auth") 
# Router de Proyectos (Asumo que existe y se define en core/app/routers/projects.py)
# app.include_router(projects.router, prefix="/api/v1/projects") 

# INCLUIR EL ROUTER DE ANÁLISIS DE AI (Aquí se montan todos los endpoints /api/v1/ai/*)
app.include_router(ai_analysis_router, prefix="/api/v1/ai") 

# Endpoints de IA (REMOVIDOS DE AQUI Y MOVIDOS A ai_analysis.py)
# @app.post("/api/ai/analyze-idea", ...)
# @app.get("/api/ai/health", ...)


# Endpoints existentes de proyectos (Estos pueden permanecer o moverse a un projects router)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "forge_saas"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "forge_saas"}

@app.post("/api/projects/create", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """Endpoint principal para crear proyectos"""
    
    try:
        # Validar tipo de proyecto
        try:
            # Uso de ProjectType de core.project_factory
            project_type = ProjectType(request.project_type)
        except ValueError:
            available_types = [pt.value for pt in ProjectType]
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de proyecto no válido. Tipos disponibles: {available_types}"
            )
        
        # Crear requirements
        requirements = ProjectRequirements(
            name=request.name,
            description=request.description,
            project_type=project_type,
            features=request.features,
            technologies=request.technologies,
            database=request.database,
            auth_required=request.auth_required,
            payment_integration=request.payment_integration,
            deployment_target=request.deployment_target
        )
        
        # Generar proyecto
        # NOTA: En un futuro, aquí es donde usarías la salida de DeepSeek para inicializar al SupervisorAgent
        result = project_factory.create_project(requirements)
        
        # Convertir a response
        response = ProjectResponse(
            success=result.get("success", False),
            project_id=result.get("project_id", "unknown"),
            project_name=request.name,
            project_path=result.get("project_path"),
            project_type=request.project_type,
            features_implemented=result.get("features_implemented", []),
            next_steps=result.get("next_steps", []),
            error=result.get("error"),
            generated_at=result.get("generated_at")
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {str(e)}")

@app.get("/api/projects/types")
async def get_project_types():
    """Obtiene todos los tipos de proyecto disponibles"""
    # ... (código sin cambios)
    return {
        "project_types": [
            {
                "value": pt.value,
                "label": pt.name.replace("_", " ").title(),
                "description": f"Proyecto de {pt.name.replace('_', ' ').title()}"
            }
            for pt in ProjectType
        ]
    }

@app.get("/api/projects/technologies")
async def get_available_technologies():
    """Obtiene tecnologías disponibles por tipo de proyecto"""
    # ... (código sin cambios)
    return {
        "technologies": {
            "frontend": ["react", "vue", "angular", "svelte", "typescript", "javascript"],
            "backend": ["nodejs", "fastapi", "express", "python", "java", "go"],
            "styling": ["tailwind", "bootstrap", "material-ui", "css", "sass"],
            "database": ["postgresql", "mongodb", "sqlite", "mysql", "redis"],
            "deployment": ["vercel", "netlify", "heroku", "aws", "docker"]
        }
    }

@app.get("/api/projects/list")
async def list_generated_projects():
    """Lista todos los proyectos generados"""
    projects_dir = "generated_projects"
    if not os.path.exists(projects_dir):
        return {"projects": []}
    
    projects = []
    for item in os.listdir(projects_dir):
        item_path = os.path.join(projects_dir, item)
        if os.path.isdir(item_path):
            projects.append({
                "name": item,
                "path": item_path,
                "created_at": str(os.path.getctime(item_path)),
                "has_package_json": os.path.exists(os.path.join(item_path, "package.json"))
            })
    
    return {"projects": projects, "count": len(projects)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
# Agregar router de pagos - Sistema de suscripciones Stripe
