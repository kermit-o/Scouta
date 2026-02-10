# app/main_enhanced.py
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
from backend.app.api import ai_analysis


app = FastAPI(title="Forge SaaS API - Enhanced with AI Agents")
app.include_router(ai_analysis.router, prefix="/api/ai") 
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
        
        # Análisis simple de requerimientos
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
    
    async def build_with_ai(self, project_dir: str, project_spec: Dict, plan: Dict) -> Dict[str, Any]:
        """Usa el agente constructor para generar código real"""
        if 'builder' not in self.agents:
            return await self._basic_build(project_dir, project_spec)
        
        try:
            builder_agent = self.agents['builder']
            build_context = {
                "project_dir": project_dir,
                "project_spec": project_spec,
                "plan": plan
            }
            
            if hasattr(builder_agent, 'build_project'):
                result = builder_agent.build_project(build_context)
                print("✅ Construcción IA completada")
                return result
            elif hasattr(builder_agent, 'generate_project'):
                result = builder_agent.generate_project(build_context)
                print("✅ Generación IA completada")
                return result
            else:
                return await self._basic_build(project_dir, project_spec)
        except Exception as e:
            print(f"❌ Error en construcción IA: {e}")
            return await self._basic_build(project_dir, project_spec)
    
    async def _basic_build(self, project_dir: str, project_spec: Dict) -> Dict[str, Any]:
        """Construcción básica como fallback - USA TU CÓDIGO ACTUAL"""
        os.makedirs(project_dir, exist_ok=True)
        
        # Generar estructura básica usando tus funciones existentes
        project_structure = {
            "package.json": self._generate_package_json(project_spec),
            "src/App.jsx": self._generate_react_app(project_spec),
            "src/main.jsx": self._generate_main_jsx(),
            "src/index.css": self._generate_index_css(),
            "vite.config.js": self._generate_vite_config(),
            "index.html": self._generate_index_html(project_spec),
            "README.md": self._generate_readme(project_spec)
        }
        
        # Crear archivos
        for file_path, content in project_structure.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            "status": "basic_build_completed",
            "files_created": list(project_structure.keys()),
            "project_structure": project_structure,
            "build_method": "basic"
        }
    
    # Tus funciones de generación existentes (adaptadas)
    def _generate_package_json(self, project):
        return f'''{{
  "name": "{project['project_name'].lower().replace(' ', '-')}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "vite": "^4.4.5",
    "@vitejs/plugin-react": "^4.0.0"
  }}
}}'''

    def _generate_react_app(self, project):
        return f'''import React from 'react'
import './App.css'

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 {project['project_name']}</h1>
        <p><strong>Generado por Forge SaaS con IA</strong></p>
        
        <div className="project-info">
          <h2>📋 Descripción del Proyecto</h2>
          <p>{project['requirements']}</p>
          
          <h3>🛠️ Stack Tecnológico</h3>
          <div className="tech-stack">
            <div className="tech-item">
              <strong>Frontend:</strong> {project.get('tech_stack', {{}}).get('frontend', 'React')}
            </div>
            <div className="tech-item">
              <strong>Backend:</strong> {project.get('tech_stack', {{}}).get('backend', 'FastAPI')}
            </div>
            <div className="tech-item">
              <strong>Database:</strong> {project.get('tech_stack', {{}}).get('database', 'PostgreSQL')}
            </div>
          </div>
          
          <div className="ai-info">
            <h4>🤖 Generado con Agentes de IA</h4>
            <p>Este proyecto fue analizado y generado utilizando inteligencia artificial avanzada.</p>
          </div>
          
          <button 
            className="demo-button"
            onClick={{ () => alert('¡Tu aplicación generada con IA funciona correctamente! 🎉') }}
          >
            Probar Aplicación
          </button>
        </div>
      </header>
    </div>
  )
}}

export default App
'''

    def _generate_main_jsx(self):
        return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''

    def _generate_index_css(self):
        return '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
}

.tech-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.tech-item {
  background: rgba(255,255,255,0.1);
  padding: 10px;
  border-radius: 5px;
}

.demo-button {
  background: #61dafb;
  color: #282c34;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
}

.demo-button:hover {
  background: #21a0c4;
}

.ai-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px;
  border-radius: 10px;
  margin: 20px 0;
}
'''

    def _generate_vite_config(self):
        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})
'''

    def _generate_index_html(self, project):
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project['project_name']}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'''

    def _generate_readme(self, project):
        tech_stack = project.get('tech_stack', {})
        return f'''# {project['project_name']}

## Descripción
{project['requirements']}

## 🚀 Generado por Forge SaaS con IA

Este proyecto fue generado automáticamente utilizando agentes de inteligencia artificial.

### 🛠️ Stack Tecnológico
- **Frontend**: {tech_stack.get('frontend', 'React')}
- **Backend**: {tech_stack.get('backend', 'FastAPI')}  
- **Base de Datos**: {tech_stack.get('database', 'PostgreSQL')}
- **Autenticación**: {tech_stack.get('authentication', 'JWT')}
- **Despliegue**: {tech_stack.get('deployment', 'Docker + Vercel')}

### 🤖 Agentes de IA Utilizados
- **Análisis de Requerimientos**: Intake Agent
- **Planificación**: Planning Agent  
- **Generación de Código**: Builder Agent

### 🏃‍♂️ Comenzar

1. Instalar dependencias:
\\`\\`\\`bash
npm install
\\`\\`\\`

2. Ejecutar en desarrollo:
\\`\\`\\`bash
npm run dev
\\`\\`\\`

3. Abrir http://localhost:3000 en el navegador

---
*Generado el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC con IA*
'''

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

async def generate_worker_enhanced(job_id: str, project_id: str):
    try:
        update_progress(job_id, 10, "Preparando generación con IA...")
        
        project = projects_db.get(project_id)
        if not project:
            update_progress(job_id, 100, "Proyecto no encontrado")
            return
        
        # Crear directorio del proyecto
        project_dir = f"generated_projects/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        
        update_progress(job_id, 30, "Generando código con agentes de IA...")
        
        # USAR AGENTE DE IA PARA CONSTRUCCIÓN
        project_spec = {
            "project_name": project["project_name"],
            "requirements": project["requirements"],
            "tech_stack": project.get("technology_stack", {}),
            "plan": project.get("generated_plan", {})
        }
        
        build_result = await agent_manager.build_with_ai(project_dir, project_spec, project.get("generated_plan", {}))
        
        update_progress(job_id, 80, "Empaquetando proyecto...")
        
        # Información del proyecto generado
        zip_info = {
            "filename": f"{project['project_name'].replace(' ', '_')}.zip",
            "size": "~2.5 MB", 
            "file_count": build_result.get("files_created", []),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "build_method": build_result.get("build_method", "unknown")
        }
        
        update_progress(job_id, 95, "Finalizando...")
        
        # Actualizar proyecto
        project["status"] = "generated"
        project["result"] = {
            "project_structure": build_result.get("project_structure", {}),
            "download_info": zip_info,
            "build_result": build_result,
            "generated_with_ai": agent_manager.has_agents(),
            "project_dir": project_dir
        }
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        ai_status = "con IA" if agent_manager.has_agents() else "básica"
        update_progress(job_id, 100, f"✅ Generación completada {ai_status}")
        
    except Exception as e:
        update_progress(job_id, 100, f"❌ Error en generación: {str(e)}")

# Endpoints mejorados
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

@app.post("/api/projects/{project_id}/generate")
async def generate_project(project_id: str, background_tasks: BackgroundTasks):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["status"] != "planned":
        raise HTTPException(status_code=400, detail="Project must be planned first")
    
    job_id = str(uuid.uuid4())
    update_progress(job_id, 5, "En cola para generación con IA")
    
    background_tasks.add_task(generate_worker_enhanced, job_id, project_id)
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Generación de código con IA iniciada",
        "ai_agents_available": agent_manager.has_agents()
    }

@app.get("/api/projects/{project_id}/download")
def download_project(project_id: str):
    project = projects_db.get(project_id)
    if not project or not project.get("result"):
        raise HTTPException(status_code=404, detail="Project not found or not generated")
    
    result = project["result"]
    return {
        "project_id": project_id,
        "project_name": project["project_name"],
        "structure": result.get("project_structure", {}),
        "download_info": result.get("download_info", {}),
        "generated_with_ai": result.get("generated_with_ai", False),
        "build_method": result.get("build_result", {}).get("build_method", "unknown"),
        "project_dir": result.get("project_dir", ""),
        "message": "Proyecto generado exitosamente"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)