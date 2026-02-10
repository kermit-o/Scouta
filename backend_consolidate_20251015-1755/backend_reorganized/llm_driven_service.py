# -*- coding: utf-8 -*-
"""
LLM Driven Project Generator Service
"""

from typing import List, Dict, Any, Optional
import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Routers internos
from core.api.projects_bridge import router as projects_bridge_router
from core.api.projects_diag import router as projects_diag_router
from core.api.projects_plan_diag import router as projects_plan_router


# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(
    title="LLM Driven Project Generator",
    version="5.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Ajusta en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers de diagnóstico y puente
app.include_router(projects_plan_router)
app.include_router(projects_diag_router)
app.include_router(projects_bridge_router)


# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------
@app.get("/api/health")
def health_check() -> JSONResponse:
    """Simple health check endpoint for Forge LLM service."""
    return JSONResponse({"status": "healthy"})


# -----------------------------------------------------------------------------
# Esquemas
# -----------------------------------------------------------------------------
class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str = "web_app"
    features: List[str] = []
    technologies: List[str] = []


# -----------------------------------------------------------------------------
# Endpoint LLM-driven (supervisor + generación mínima)
# -----------------------------------------------------------------------------
@app.post("/api/llm/projects")
async def create_llm_driven_project(request: ProjectRequest):
    """
    1) Intenta analizar los requisitos con el LLMDrivenSupervisor (si disponible).
    2) Con el plan (o fallback) genera un proyecto FastAPI mínimo en generated_projects/.
    """
    try:
        # ----------------------
        # FASE 1: Análisis LLM
        # ----------------------
        try:
            from core.agents.llm_driven_supervisor import LLMDrivenSupervisor

            supervisor = LLMDrivenSupervisor()
            llm_plan = await supervisor.analyze_and_plan_project(request.model_dump())
            # Asegura flags mínimos
            llm_plan = llm_plan or {}
            llm_plan.setdefault("llm_used", True)
            llm_plan.setdefault("project_id", str(uuid.uuid4()))
            llm_plan.setdefault("project_name", request.name)
            llm_plan.setdefault("description", request.description)
        except Exception as e:
            # Fallback robusto sin LLM
            llm_plan = {
                "project_id": str(uuid.uuid4()),
                "project_name": request.name,
                "description": request.description,
                "llm_used": False,
                "execution_plan": {
                    "architecture": {"pattern": "fallback", "components": []},
                    "modules": [],
                    "endpoints": [],
                },
            }

        # ----------------------
        # FASE 2: Ejecución plan
        # ----------------------
        project_id = llm_plan.get("project_id", str(uuid.uuid4()))
        project_name = llm_plan.get("project_name", request.name)
        safe_name = "".join([c if c.isalnum() or c in ("-", "_") else "-" for c in project_name.strip()])
        project_path = f"generated_projects/llm-{safe_name}-{project_id[:8]}"
        os.makedirs(project_path, exist_ok=True)

        files_created = await create_basic_project(project_path, llm_plan, request)

        return {
            "status": "success",
            "system": "llm_driven_v5",
            "project_id": project_id,
            "project_name": project_name,
            "project_path": project_path,
            "files_created": files_created,
            "total_files": len(files_created),
            "llm_analysis_used": llm_plan.get("llm_used", False),
            "message": "Proyecto generado",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en ciclo LLM: {str(e)}") from e


# -----------------------------------------------------------------------------
# Helpers de generación mínima
# -----------------------------------------------------------------------------
async def create_basic_project(project_path: str, llm_plan: Dict[str, Any], request: ProjectRequest) -> List[str]:
    """
    Genera un esqueleto mínimo de proyecto FastAPI:
    - main.py
    - requirements.txt
    - README.md
    """
    files_created: List[str] = []

    # 1) main.py
    main_content = generate_main_file(llm_plan, request)
    main_path = os.path.join(project_path, "main.py")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)
    files_created.append(main_path)

    # 2) requirements.txt (alineado con artefactos previos)
    req_content = generate_requirements(llm_plan)
    req_path = os.path.join(project_path, "requirements.txt")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(req_content)
    files_created.append(req_path)

    # 3) README.md
    readme_content = generate_readme(llm_plan, request, files_created)
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    files_created.append(readme_path)

    return files_created


def generate_main_file(llm_plan: Dict[str, Any], request: ProjectRequest) -> str:
    project_name = llm_plan.get("project_name", request.name)
    description = llm_plan.get("description", request.description)

    return f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title={project_name!r},
    description={description!r},
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajusta en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{
        "message": "Bienvenido a {project_name}",
        "description": {description!r},
        "status": "active",
        "generated_by": "LLM Driven System v5.0"
    }}

@app.get("/api/health")
async def health_check():
    return {{"status": "healthy", "service": "LLM Driven API"}}

@app.get("/api/info")
async def project_info():
    return {{"name": {project_name!r}, "version": "1.0.0"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"""


def generate_requirements(_: Dict[str, Any]) -> str:
    # Pins compatibles con tus artefactos previos
    return """fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.12.4
"""


def generate_readme(llm_plan: Dict[str, Any], request: ProjectRequest, files_created: List[str]) -> str:
    project_name = llm_plan.get("project_name", request.name)
    description = llm_plan.get("description", request.description)
    llm_used = llm_plan.get("llm_used", False)
    llm_info = "Generado con análisis de IA" if llm_used else "Generado con plan básico"

    lines: List[str] = [
        f"# {project_name}",
        "",
        description,
        "",
        llm_info,
        "",
        "## Instalación y Ejecución",
        "",
        "```bash",
        "python -m venv .venv",
        "source .venv/bin/activate    # En Windows: .venv\\Scripts\\activate",
        "pip install -r requirements.txt",
        "python main.py",
        "```",
        "",
        "### Ejecutar con Uvicorn (opcional)",
        "",
        "```bash",
        "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
        "```",
        "",
        "## Endpoints",
        "",
        "- `GET /` — Información básica del proyecto",
        "- `GET /api/health` — Comprobación de salud",
        "- `GET /api/info` — Nombre y versión",
        "",
        "## Estructura generada",
        "",
        "- `main.py` — Servicio FastAPI mínimo",
        "- `requirements.txt` — Dependencias",
        "- `README.md` — Esta guía",
        "",
        "---",
        "Generado por **LLM Driven System v5.0**",
        "",
    ]
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Ejecutable local (opcional)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("llm_driven_service:app", host="0.0.0.0", port=8011, reload=True)
