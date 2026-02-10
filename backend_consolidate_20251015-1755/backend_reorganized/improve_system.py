#!/usr/bin/env python3
"""
SCRIPT DE MEJORA PARA FORGE SaaS
Este script arregla problemas de BOM y mejora la integración con agentes IA
"""

import os
import sys
import shutil
from pathlib import Path

def fix_bom_issues():
    """Arregla problemas de BOM en archivos Python"""
    print("🔧 ARREGLANDO PROBLEMAS DE BOM...")
    
    # Buscar archivos Python con posibles problemas de BOM
    python_files = list(Path('.').rglob('*.py'))
    
    for file_path in python_files:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Detectar y remover BOM
            if content.startswith(b'\xef\xbb\xbf'):
                print(f"🔄 Removiendo BOM de: {file_path}")
                with open(file_path, 'wb') as f:
                    f.write(content[3:])
                    
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")

def create_enhanced_main():
    """Crea la versión mejorada de main.py con integración IA"""
    print("🚀 CREANDO MAIN.PY MEJORADO...")
    
    enhanced_content = '''from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import time
import os
import json
from datetime import datetime
import importlib.util
import asyncio

app = FastAPI(title="Forge SaaS API - Enhanced with AI Agents")

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
    requirements: str
    user_id: str = "demo-user"

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    project_name: str
    requirements: str
    status: str
    technology_stack: Optional[Dict[str, Any]] = None
    generated_plan: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

class ProgressResponse(BaseModel):
    job_id: str
    percent: int
    message: str
    updated_at: str

# Sistema de Agentes IA
class AgentManager:
    def __init__(self):
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Carga los agentes de IA reales"""
        print("🤖 CARGANDO AGENTES DE IA...")
        
        agent_configs = [
            {
                "name": "intake",
                "file": "core/agents/intake_agent.py",
                "class_name": "IntakeAgent"
            },
            {
                "name": "planner", 
                "file": "core/agents/planning_agent.py",
                "class_name": "PlanningAgent"
            },
            {
                "name": "builder",
                "file": "core/agents/builder_agent.py",
                "class_name": "BuilderAgent"
            }
        ]
        
        for config in agent_configs:
            if os.path.exists(config["file"]):
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"agent_{config['name']}", 
                        config["file"]
                    )
                    agent_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(agent_module)
                    
                    # Buscar la clase específica
                    for attr_name in dir(agent_module):
                        attr = getattr(agent_module, attr_name)
                        if (isinstance(attr, type) and 
                            config["class_name"].lower() in attr_name.lower()):
                            self.agents[config["name"]] = attr()
                            print(f"   ✅ {config['name']}: {attr_name}")
                            break
                    else:
                        print(f"   ❌ No se encontró {config['class_name']}")
                        
                except Exception as e:
                    print(f"   ❌ Error cargando {config['name']}: {e}")
            else:
                print(f"   📄 {config['file']} no existe")
        
        print(f"🎯 Agentes cargados: {list(self.agents.keys())}")
    
    def has_agents(self):
        return len(self.agents) > 0
    
    async def analyze_with_ai(self, requirements: str) -> Dict[str, Any]:
        """Usa el agente de intake para análisis avanzado"""
        if 'intake' not in self.agents:
            return self._basic_analysis(requirements)
        
        try:
            intake_agent = self.agents['intake']
            if hasattr(intake_agent, 'analyze_requirements'):
                result = intake_agent.analyze_requirements(requirements)
                print("✅ Análisis IA completado")
                return result
            elif hasattr(intake_agent, 'analyze_complexity'):
                complexity = intake_agent.analyze_complexity(requirements)
                return {"complexity": complexity, "analysis": "basic"}
            else:
                return self._basic_analysis(requirements)
        except Exception as e:
            print(f"❌ Error en análisis IA: {e}")
            return self._basic_analysis(requirements)
    
    def _basic_analysis(self, requirements: str) -> Dict[str, Any]:
        """Análisis básico como fallback"""
        requirements_lower = requirements.lower()
        
        tech_stack = {
            "frontend": "React + TypeScript",
            "backend": "Python FastAPI", 
            "database": "PostgreSQL",
            "authentication": "JWT",
            "deployment": "Docker + Vercel"
        }
        
        if "mobile" in requirements_lower:
            tech_stack["frontend"] = "React Native"
        if "simple" in requirements_lower or "landing" in requirements_lower:
            tech_stack["frontend"] = "HTML + CSS + JavaScript"
            tech_stack["backend"] = "None"
        if "api" in requirements_lower and "mobile" not in requirements_lower:
            tech_stack["frontend"] = "None"
        
        return {
            "tech_stack": tech_stack,
            "complexity": "medium",
            "estimated_time": "2-3 semanas",
            "analysis_method": "basic"
        }
    
    async def plan_with_ai(self, project_spec: Dict) -> Dict[str, Any]:
        """Usa el agente de planificación para generar plan detallado"""
        if 'planner' not in self.agents:
            return self._basic_plan(project_spec)
        
        try:
            planner_agent = self.agents['planner']
            if hasattr(planner_agent, 'create_development_plan'):
                plan = planner_agent.create_development_plan(project_spec)
                print("✅ Planificación IA completada")
                return plan
            else:
                return self._basic_plan(project_spec)
        except Exception as e:
            print(f"❌ Error en planificación IA: {e}")
            return self._basic_plan(project_spec)
    
    def _basic_plan(self, project_spec: Dict) -> Dict[str, Any]:
        """Plan básico como fallback"""
        return {
            "steps": [
                "Configurar estructura del proyecto",
                "Implementar componentes base",
                "Crear lógica de negocio", 
                "Agregar estilos y diseño",
                "Escribir documentación",
                "Preparar para despliegue"
            ],
            "architecture": project_spec.get("tech_stack", {}),
            "estimated_time": "2-3 semanas",
            "complexity": "medium",
            "planning_method": "basic"
        }

# Inicializar el manager de agentes
agent_manager = AgentManager()

# Sistema de progreso
def update_progress(job_id: str, percent: int, message: str):
    progress_db[job_id] = {
        "job_id": job_id,
        "percent": percent,
        "message": message,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

# Rutas básicas
@app.get("/")
async def root():
    return {
        "message": "🚀 Forge SaaS API con IA funcionando", 
        "version": "2.0",
        "ai_agents_loaded": agent_manager.has_agents(),
        "available_agents": list(agent_manager.agents.keys())
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok", 
        "ai_capabilities": agent_manager.has_agents(),
        "agents": list(agent_manager.agents.keys())
    }

@app.get("/api/agents/status")
def agents_status():
    return {
        "total_agents": len(agent_manager.agents),
        "agents_loaded": list(agent_manager.agents.keys()),
        "can_use_ai": agent_manager.has_agents()
    }

@app.get("/api/projects")
def list_projects():
    projects = list(projects_db.values())
    return sorted(projects, key=lambda x: x["created_at"], reverse=True)

@app.post("/api/projects", status_code=201)
def create_project(request: ProjectRequest):
    project_id = str(uuid.uuid4())
    current_time = datetime.utcnow().isoformat() + "Z"
    
    project = {
        "id": project_id,
        "user_id": request.user_id,
        "project_name": request.project_name,
        "requirements": request.requirements,
        "status": "pending",
        "technology_stack": None,
        "generated_plan": None,
        "result": None,
        "created_at": current_time,
        "updated_at": current_time
    }
    
    projects_db[project_id] = project
    print(f"✅ Proyecto creado: {request.project_name}")
    
    return project

@app.get("/api/progress/{job_id}")
def get_progress(job_id: str):
    return progress_db.get(job_id, {
        "job_id": job_id,
        "percent": 0,
        "message": "Job not found",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    })

# Workers mejorados con IA
async def plan_worker_enhanced(job_id: str, project_id: str):
    try:
        update_progress(job_id, 10, "Iniciando análisis con IA...")
        
        project = projects_db.get(project_id)
        if not project:
            update_progress(job_id, 100, "Proyecto no encontrado")
            return
        
        update_progress(job_id, 25, "Analizando requerimientos con agentes de IA...")
        
        # USAR AGENTE DE IA PARA ANÁLISIS
        ai_analysis = await agent_manager.analyze_with_ai(project["requirements"])
        
        update_progress(job_id, 50, "Generando plan con IA...")
        
        # USAR AGENTE DE IA PARA PLANIFICACIÓN
        project_spec = {
            "name": project["project_name"],
            "requirements": project["requirements"],
            "tech_stack": ai_analysis.get("tech_stack", {}),
            "analysis": ai_analysis
        }
        
        ai_plan = await agent_manager.plan_with_ai(project_spec)
        
        update_progress(job_id, 80, "Guardando resultados de IA...")
        
        # Actualizar proyecto con resultados de IA
        project["status"] = "planned"
        project["technology_stack"] = ai_analysis.get("tech_stack", {})
        project["generated_plan"] = {
            **ai_plan,
            "ai_analysis": ai_analysis,
            "generated_with_ai": agent_manager.has_agents()
        }
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        ai_status = "con agentes de IA" if agent_manager.has_agents() else "básico"
        update_progress(job_id, 100, f"✅ Planificación completada {ai_status}")
        
    except Exception as e:
        update_progress(job_id, 100, f"❌ Error en planificación: {str(e)}")

@app.post("/api/projects/{project_id}/plan")
async def plan_project(project_id: str, background_tasks: BackgroundTasks):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    update_progress(job_id, 5, "En cola para planificación con IA")
    
    background_tasks.add_task(plan_worker_enhanced, job_id, project_id)
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Planificación con IA iniciada",
        "ai_agents_available": agent_manager.has_agents()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''

    # Guardar el archivo mejorado
    with open('app/main_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ main_enhanced.py creado exitosamente")

def backup_original_main():
    """Hace backup del main.py original"""
    if os.path.exists('app/main.py'):
        shutil.copy2('app/main.py', 'app/main.py.backup')
        print("✅ Backup de main.py creado")

def main():
    print("�� INICIANDO MEJORA DEL SISTEMA FORGE SaaS")
    print("=" * 50)
    
    # 1. Arreglar problemas de BOM
    fix_bom_issues()
    
    # 2. Hacer backup del original
    backup_original_main()
    
    # 3. Crear versión mejorada
    create_enhanced_main()
    
    print("\\n🎉 MEJORA COMPLETADA!")
    print("📁 Archivos creados/modificados:")
    print("   - app/main_enhanced.py (nueva versión con IA)")
    print("   - app/main.py.backup (backup del original)")
    print("\\n🚀 Para ejecutar: uvicorn app.main_enhanced:app --reload --host 0.0.0.0 --port 8001")

if __name__ == "__main__":
    main()
