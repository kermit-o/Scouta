# -*- coding: utf-8 -*-
"""
LLM DRIVEN SERVICE
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="LLM Driven Project Generator",
    version="5.0"
)

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

@app.post("/api/llm/projects")
async def create_llm_driven_project(request: ProjectRequest):
    try:
        print(f"INICIANDO CICLO LLM PARA: {request.name}")
        
        # FASE 1: ANALISIS CON LLM SUPERVISOR
        try:
            from core.agents.llm_driven_supervisor import LLMDrivenSupervisor
            supervisor = LLMDrivenSupervisor()
            print("Fase 1: LLM analizando requisitos...")
            llm_plan = await supervisor.analyze_and_plan_project(request.model_dump())
            print(f"Analisis LLM completado - LLM usado: {llm_plan.get('llm_used', False)}")
            
        except Exception as e:
            print(f"Error en supervisor LLM: {e}")
            llm_plan = {
                "project_id": str(uuid.uuid4()),
                "project_name": request.name,
                "description": request.description,
                "llm_used": False,
                "execution_plan": {
                    "architecture": {"pattern": "fallback", "components": []},
                    "modules": [],
                    "endpoints": []
                }
            }
        
        # FASE 2: EJECUCION DEL PLAN
        project_id = llm_plan.get('project_id', str(uuid.uuid4()))
        project_name = llm_plan.get('project_name', request.name)
        safe_name = "".join([c if c.isalnum() or c in ("-", "_") else "-" for c in project_name.strip()])
        project_path = f"generated_projects/llm-{safe_name}-{project_id[:8]}"
        os.makedirs(project_path, exist_ok=True)
        
        print(f"Fase 2: Ejecutando plan en {project_path}...")
        
        # Crear proyecto basico
        files_created = await create_basic_project(project_path, llm_plan, request)
        
        return {
            "status": "success",
            "system": "llm_driven_v5",
            "project_id": project_id,
            "project_name": project_name,
            "project_path": project_path,
            "files_created": files_created,
            "total_files": len(files_created),
            "llm_analysis_used": llm_plan.get('llm_used', False),
            "message": "Proyecto generado con analisis LLM"
        }
            
    except Exception as e:
        print(f"Error en ciclo LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def create_basic_project(project_path: str, llm_plan: Dict[str, Any], request: ProjectRequest) -> List[str]:
    files_created = []
    
    try:
        # 1. MAIN.PY
        main_content = generate_main_file(llm_plan, request)
        main_path = os.path.join(project_path, "main.py")
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        files_created.append(main_path)
        
        # 2. REQUIREMENTS.TXT
        req_content = generate_requirements(llm_plan)
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(req_content)
        files_created.append(req_path)
        
        # 3. README.MD
        readme_content = generate_readme(llm_plan, request, files_created)
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append(readme_path)
        
        print(f"Proyecto creado con {len(files_created)} archivos")
        
    except Exception as e:
        print(f"Error creando proyecto: {e}")
    
    return files_created

def generate_main_file(llm_plan: Dict[str, Any], request: ProjectRequest) -> str:
    project_name = llm_plan.get('project_name', request.name)
    
    return f'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{project_name}",
    description="{request.description}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{
        "message": "Bienvenido a {project_name}",
        "description": "{request.description}",
        "status": "active",
        "generated_by": "LLM Driven System v5.0"
    }}

@app.get("/api/health")
async def health_check():
    return {{"status": "healthy", "service": "LLM Driven API"}}

@app.get("/api/info")
async def project_info():
    return {{"name": "{project_name}", "version": "1.0.0"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''

def generate_requirements(llm_plan: Dict[str, Any]) -> str:
    return """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
"""

def generate_readme(llm_plan: Dict[str, Any], request: ProjectRequest, files_created: List[str]) -> str:
    project_name = llm_plan.get('project_name', request.name)
    description = llm_plan.get('description', request.description)
    llm_used = llm_plan.get('llm_used', False)
    llm_info = "Generado con analisis de IA" if llm_used else "Generado con plan basico"

    lines: List[str] = [
        f"# {project_name}",
        "",
        description,
        "",
        llm_info,
        "",
        "## Instalacion y Ejecucion",
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

