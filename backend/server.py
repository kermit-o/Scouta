from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="AppForge - Application Generator", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class ProjectIdea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "processing"  # processing, completed, failed
    progress: int = 0

class ProjectIdeaCreate(BaseModel):
    user_description: str

class FunctionalSpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    user_stories: List[str]
    acceptance_criteria: List[str]
    entities: List[str]
    key_actions: List[str]
    target_audience: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TechSpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    architecture: str
    recommended_stack: Dict[str, str]
    endpoints: List[Dict[str, Any]]
    database_schema: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectStructure(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    directory_tree: Dict[str, Any]
    files_to_generate: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GeneratedCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    file_path: str
    file_content: str
    file_type: str  # frontend, backend, config, documentation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectProgress(BaseModel):
    project_id: str
    current_stage: str
    progress_percentage: int
    stages_completed: List[str]
    current_task: str
    estimated_time_remaining: Optional[int] = None

# Initialize LLM Chat
def get_llm_chat(session_id: str, system_message: str = "You are an expert software architect and full-stack developer."):
    return LlmChat(
        api_key=os.environ['EMERGENT_LLM_KEY'],
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")

# Helper functions
async def update_project_progress(project_id: str, stage: str, progress: int, task: str):
    """Update project progress in database"""
    await db.projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "status": "processing" if progress < 100 else "completed",
                "progress": progress,
                "current_stage": stage,
                "current_task": task,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

async def extract_project_requirements(user_description: str, project_id: str):
    """Extract detailed requirements from user description using AI"""
    chat = get_llm_chat(f"requirements_{project_id}")
    
    prompt = f"""
    Analiza la siguiente idea de aplicación y extrae información detallada:

    IDEA DEL USUARIO: {user_description}

    Por favor, proporciona un análisis estructurado en formato JSON con:
    {{
        "objetivos": ["objetivo1", "objetivo2"],
        "publico_objetivo": "descripción del público",
        "entidades_principales": ["entidad1", "entidad2"],
        "acciones_clave": ["acción1", "acción2"],
        "restricciones": ["restricción1", "restricción2"],
        "integraciones_necesarias": ["integración1", "integración2"],
        "tipo_aplicacion": "web/mobile/desktop",
        "complejidad": "simple/media/alta"
    }}
    
    Responde SOLO con el JSON válido, sin explicaciones adicionales.
    """
    
    message = UserMessage(text=prompt)
    response = await chat.send_message(message)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "objetivos": ["Desarrollar aplicación según descripción del usuario"],
            "publico_objetivo": "Usuario general",
            "entidades_principales": ["Usuario"],
            "acciones_clave": ["Funcionalidad básica"],
            "restricciones": [],
            "integraciones_necesarias": [],
            "tipo_aplicacion": "web",
            "complejidad": "media"
        }

async def generate_functional_spec(requirements: Dict[str, Any], project_id: str):
    """Generate functional specification using AI"""
    chat = get_llm_chat(f"functional_{project_id}")
    
    prompt = f"""
    Basándote en estos requisitos, genera una especificación funcional detallada:

    REQUISITOS: {json.dumps(requirements, indent=2)}

    Por favor, proporciona en formato JSON:
    {{
        "user_stories": [
            "Como [tipo de usuario], quiero [funcionalidad] para [beneficio]"
        ],
        "acceptance_criteria": [
            "Criterio de aceptación específico y medible"
        ],
        "casos_uso_principales": [
            "Caso de uso detallado"
        ]
    }}
    
    Genera al menos 5 user stories y 10 criterios de aceptación específicos.
    Responde SOLO con el JSON válido.
    """
    
    message = UserMessage(text=prompt)
    response = await chat.send_message(message)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "user_stories": ["Como usuario, quiero usar la aplicación para resolver mi problema"],
            "acceptance_criteria": ["La aplicación debe funcionar correctamente"],
            "casos_uso_principales": ["Usuario utiliza funcionalidad principal"]
        }

async def generate_tech_spec(requirements: Dict[str, Any], functional_spec: Dict[str, Any], project_id: str):
    """Generate technical specification using AI"""
    chat = get_llm_chat(f"technical_{project_id}")
    
    prompt = f"""
    Genera una especificación técnica para esta aplicación:

    REQUISITOS: {json.dumps(requirements, indent=2)}
    ESPECIFICACIÓN FUNCIONAL: {json.dumps(functional_spec, indent=2)}

    Por favor, proporciona en formato JSON:
    {{
        "architecture": "Descripción de la arquitectura (ej: Cliente-Servidor, SPA, API REST)",
        "recommended_stack": {{
            "frontend": "React/Vue/Angular",
            "backend": "FastAPI/Express/Django",
            "database": "MongoDB/PostgreSQL/MySQL",
            "deployment": "Docker/Vercel/AWS"
        }},
        "endpoints": [
            {{
                "method": "GET/POST/PUT/DELETE",
                "path": "/api/endpoint",
                "description": "Descripción del endpoint",
                "request_body": {{}},
                "response": {{}}
            }}
        ],
        "database_schema": [
            {{
                "collection_name": "nombre_coleccion",
                "fields": {{
                    "field_name": "field_type"
                }}
            }}
        ],
        "dependencies": {{
            "frontend": ["react", "axios"],
            "backend": ["fastapi", "pymongo"]
        }}
    }}
    
    Responde SOLO con el JSON válido.
    """
    
    message = UserMessage(text=prompt)
    response = await chat.send_message(message)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "architecture": "Cliente-Servidor con API REST",
            "recommended_stack": {
                "frontend": "React",
                "backend": "FastAPI",
                "database": "MongoDB",
                "deployment": "Docker"
            },
            "endpoints": [],
            "database_schema": [],
            "dependencies": {
                "frontend": ["react", "axios"],
                "backend": ["fastapi", "pymongo"]
            }
        }

async def process_project_generation(project_idea: ProjectIdea):
    """Background task to process project generation"""
    try:
        project_id = project_idea.id
        
        # Stage 1: Requirements Analysis (20%)
        await update_project_progress(project_id, "requirements", 10, "Analizando requisitos...")
        requirements = await extract_project_requirements(project_idea.user_description, project_id)
        await update_project_progress(project_id, "requirements", 20, "Requisitos extraídos")
        
        # Stage 2: Functional Specification (40%)
        await update_project_progress(project_id, "functional_spec", 25, "Generando especificación funcional...")
        functional_spec = await generate_functional_spec(requirements, project_id)
        
        # Save functional spec to database
        func_spec_doc = FunctionalSpec(
            project_id=project_id,
            user_stories=functional_spec.get("user_stories", []),
            acceptance_criteria=functional_spec.get("acceptance_criteria", []),
            entities=requirements.get("entidades_principales", []),
            key_actions=requirements.get("acciones_clave", []),
            target_audience=requirements.get("publico_objetivo", "")
        )
        await db.functional_specs.insert_one(func_spec_doc.dict())
        await update_project_progress(project_id, "functional_spec", 40, "Especificación funcional completada")
        
        # Stage 3: Technical Specification (60%)
        await update_project_progress(project_id, "tech_spec", 45, "Generando especificación técnica...")
        tech_spec = await generate_tech_spec(requirements, functional_spec, project_id)
        
        # Save tech spec to database
        tech_spec_doc = TechSpec(
            project_id=project_id,
            architecture=tech_spec.get("architecture", ""),
            recommended_stack=tech_spec.get("recommended_stack", {}),
            endpoints=tech_spec.get("endpoints", []),
            database_schema=tech_spec.get("database_schema", []),
            dependencies=tech_spec.get("dependencies", {})
        )
        await db.tech_specs.insert_one(tech_spec_doc.dict())
        await update_project_progress(project_id, "tech_spec", 60, "Especificación técnica completada")
        
        # Stage 4: Project Structure (80%)
        await update_project_progress(project_id, "structure", 65, "Generando estructura del proyecto...")
        
        # Generate basic project structure
        directory_tree = {
            "frontend": {
                "src": {
                    "components": {},
                    "pages": {},
                    "hooks": {},
                    "utils": {},
                    "styles": {}
                },
                "public": {}
            },
            "backend": {
                "models": {},
                "routes": {},
                "services": {},
                "utils": {}
            },
            "docs": {}
        }
        
        structure_doc = ProjectStructure(
            project_id=project_id,
            directory_tree=directory_tree,
            files_to_generate=["README.md", "package.json", "requirements.txt"]
        )
        await db.project_structures.insert_one(structure_doc.dict())
        await update_project_progress(project_id, "structure", 80, "Estructura del proyecto creada")
        
        # Stage 5: Code Generation (100%)
        await update_project_progress(project_id, "code_generation", 85, "Generando código base...")
        
        # Generate some basic files
        readme_content = f"""# {project_idea.user_description[:50]}...

## Descripción
{project_idea.user_description}

## Stack Tecnológico
- Frontend: {tech_spec.get('recommended_stack', {}).get('frontend', 'React')}
- Backend: {tech_spec.get('recommended_stack', {}).get('backend', 'FastAPI')}
- Database: {tech_spec.get('recommended_stack', {}).get('database', 'MongoDB')}

## Instalación
```bash
# Frontend
cd frontend
npm install
npm start

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Características Principales
{chr(10).join([f'- {story}' for story in functional_spec.get('user_stories', [])])}
"""

        # Save generated code
        readme_doc = GeneratedCode(
            project_id=project_id,
            file_path="README.md",
            file_content=readme_content,
            file_type="documentation"
        )
        await db.generated_code.insert_one(readme_doc.dict())
        
        await update_project_progress(project_id, "completed", 100, "Proyecto generado exitosamente")
        
    except Exception as e:
        logger.error(f"Error processing project {project_id}: {str(e)}")
        await update_project_progress(project_id, "failed", 0, f"Error: {str(e)}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AppForge API - Generador de Aplicaciones", "version": "1.0.0"}

@api_router.post("/projects", response_model=ProjectIdea)
async def create_project(project_create: ProjectIdeaCreate, background_tasks: BackgroundTasks):
    """Create a new project from user idea"""
    project = ProjectIdea(**project_create.dict())
    
    # Save project to database
    await db.projects.insert_one(project.dict())
    
    # Start background processing
    background_tasks.add_task(process_project_generation, project)
    
    return project

@api_router.get("/projects/{project_id}", response_model=ProjectIdea)
async def get_project(project_id: str):
    """Get project by ID"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectIdea(**project)

@api_router.get("/projects", response_model=List[ProjectIdea])
async def get_projects():
    """Get all projects"""
    projects = await db.projects.find().to_list(1000)
    return [ProjectIdea(**project) for project in projects]

@api_router.get("/projects/{project_id}/progress")
async def get_project_progress(project_id: str):
    """Get project generation progress"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project_id,
        "status": project.get("status", "processing"),
        "progress": project.get("progress", 0),
        "current_stage": project.get("current_stage", "initializing"),
        "current_task": project.get("current_task", "Starting..."),
        "created_at": project.get("created_at"),
        "updated_at": project.get("updated_at")
    }

@api_router.get("/projects/{project_id}/functional-spec")
async def get_functional_spec(project_id: str):
    """Get functional specification for project"""
    spec = await db.functional_specs.find_one({"project_id": project_id})
    if not spec:
        raise HTTPException(status_code=404, detail="Functional specification not found")
    return FunctionalSpec(**spec)

@api_router.get("/projects/{project_id}/tech-spec")
async def get_tech_spec(project_id: str):
    """Get technical specification for project"""
    spec = await db.tech_specs.find_one({"project_id": project_id})
    if not spec:
        raise HTTPException(status_code=404, detail="Technical specification not found")
    return TechSpec(**spec)

@api_router.get("/projects/{project_id}/structure")
async def get_project_structure(project_id: str):
    """Get project structure"""
    structure = await db.project_structures.find_one({"project_id": project_id})
    if not structure:
        raise HTTPException(status_code=404, detail="Project structure not found")
    return ProjectStructure(**structure)

@api_router.get("/projects/{project_id}/code")
async def get_generated_code(project_id: str):
    """Get all generated code files for project"""
    code_files = await db.generated_code.find({"project_id": project_id}).to_list(1000)
    return [GeneratedCode(**code_file) for code_file in code_files]

@api_router.get("/projects/{project_id}/download")
async def download_project(project_id: str):
    """Download project as ZIP (placeholder)"""
    # This would generate and return a ZIP file
    return {"message": "Download functionality coming soon", "project_id": project_id}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()