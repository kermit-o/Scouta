from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import time
import os
import json
from datetime import datetime

app = FastAPI(title="Forge SaaS API - Simple")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria (para desarrollo)
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

# Rutas básicas
@app.get("/")
async def root():
    return {"message": "🚀 Forge SaaS API funcionando", "version": "1.0"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

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

# Sistema de progreso
def update_progress(job_id: str, percent: int, message: str):
    progress_db[job_id] = {
        "job_id": job_id,
        "percent": percent,
        "message": message,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/progress/{job_id}")
def get_progress(job_id: str):
    return progress_db.get(job_id, {
        "job_id": job_id,
        "percent": 0,
        "message": "Job not found",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    })

# Workers de IA
def plan_worker(job_id: str, project_id: str):
    try:
        update_progress(job_id, 10, "Iniciando análisis de requerimientos")
        time.sleep(1)
        
        project = projects_db.get(project_id)
        if not project:
            update_progress(job_id, 100, "Proyecto no encontrado")
            return
        
        update_progress(job_id, 25, "Analizando requerimientos con IA")
        time.sleep(2)
        
        # Análisis inteligente de requerimientos
        requirements = project["requirements"].lower()
        
        # Determinar stack tecnológico basado en requerimientos
        if "mobile" in requirements or "app" in requirements:
            frontend = "React Native"
        elif "web" in requirements or "sitio" in requirements:
            frontend = "React + TypeScript"
        else:
            frontend = "React"
            
        if "api" in requirements or "backend" in requirements:
            backend = "Python FastAPI"
        else:
            backend = "Node.js Express"
            
        tech_stack = {
            "frontend": frontend,
            "backend": backend,
            "database": "PostgreSQL",
            "authentication": "JWT",
            "deployment": "Docker + Vercel"
        }
        
        update_progress(job_id, 50, "Generando arquitectura del proyecto")
        time.sleep(2)
        
        # Plan generado por IA
        plan = {
            "steps": [
                "Configurar estructura del proyecto y dependencias",
                "Implementar modelos de base de datos",
                "Crear endpoints de API y autenticación",
                "Desarrollar componentes frontend",
                "Implementar lógica de negocio",
                "Agregar estilos y diseño responsive",
                "Escribir tests y documentación",
                "Preparar para despliegue"
            ],
            "architecture": tech_stack,
            "estimated_time": "2-3 semanas",
            "complexity": "Intermedia"
        }
        
        update_progress(job_id, 80, "Guardando plan en base de datos")
        time.sleep(1)
        
        # Actualizar proyecto
        project["status"] = "planned"
        project["technology_stack"] = tech_stack
        project["generated_plan"] = plan
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        update_progress(job_id, 100, "✅ Planificación completada exitosamente")
        
    except Exception as e:
        update_progress(job_id, 100, f"❌ Error en planificación: {str(e)}")

@app.post("/api/projects/{project_id}/plan")
def plan_project(project_id: str, background_tasks: BackgroundTasks):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    update_progress(job_id, 5, "En cola para planificación")
    
    background_tasks.add_task(plan_worker, job_id, project_id)
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Planificación con IA iniciada"
    }

# Generación de código
def generate_worker(job_id: str, project_id: str):
    try:
        update_progress(job_id, 10, "Preparando entorno de generación")
        time.sleep(1)
        
        project = projects_db.get(project_id)
        if not project:
            update_progress(job_id, 100, "Proyecto no encontrado")
            return
        
        tech_stack = project.get("technology_stack", {})
        frontend = tech_stack.get("frontend", "React")
        
        update_progress(job_id, 30, f"Generando proyecto {frontend}")
        time.sleep(2)
        
        # Generar estructura del proyecto
        project_structure = {
            "package.json": generate_package_json(project),
            "src/App.jsx": generate_react_app(project),
            "src/main.jsx": generate_main_jsx(),
            "src/index.css": generate_index_css(),
            "vite.config.js": generate_vite_config(),
            "index.html": generate_index_html(project),
            "README.md": generate_readme(project)
        }
        
        update_progress(job_id, 70, "Empaquetando proyecto")
        time.sleep(1)
        
        # Simular archivo ZIP (en producción sería real)
        zip_info = {
            "filename": f"{project['project_name'].replace(' ', '_')}.zip",
            "size": "~2.5 MB",
            "file_count": len(project_structure),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        update_progress(job_id, 90, "Finalizando generación")
        time.sleep(1)
        
        # Actualizar proyecto
        project["status"] = "generated"
        project["result"] = {
            "project_structure": project_structure,
            "download_info": zip_info,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        update_progress(job_id, 100, "✅ Proyecto generado exitosamente")
        
    except Exception as e:
        update_progress(job_id, 100, f"❌ Error en generación: {str(e)}")

def generate_package_json(project):
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

def generate_react_app(project):
    return f'''import React from 'react'
import './App.css'

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 {project['project_name']}</h1>
        <p><strong>Generado por Forge SaaS</strong></p>
        
        <div className="project-info">
          <h2>📋 Descripción del Proyecto</h2>
          <p>{project['requirements']}</p>
          
          <h3>🛠️ Stack Tecnológico</h3>
          <div className="tech-stack">
            <div className="tech-item">
              <strong>Frontend:</strong> {project.get('technology_stack', {{}}).get('frontend', 'React')}
            </div>
            <div className="tech-item">
              <strong>Backend:</strong> {project.get('technology_stack', {{}}).get('backend', 'FastAPI')}
            </div>
            <div className="tech-item">
              <strong>Database:</strong> {project.get('technology_stack', {{}}).get('database', 'PostgreSQL')}
            </div>
          </div>
          
          <button 
            className="demo-button"
            onClick={{ () => alert('¡Tu aplicación generada funciona correctamente! 🎉') }}
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

def generate_main_jsx():
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

def generate_index_css():
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
'''

def generate_vite_config():
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

def generate_index_html(project):
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

def generate_readme(project):
    tech_stack = project.get('technology_stack', {})
    return f'''# {project['project_name']}

## Descripción
{project['requirements']}

## Generado por Forge SaaS

Este proyecto fue generado automáticamente por Forge SaaS utilizando inteligencia artificial.

### Stack Tecnológico
- **Frontend**: {tech_stack.get('frontend', 'React')}
- **Backend**: {tech_stack.get('backend', 'FastAPI')}  
- **Base de Datos**: {tech_stack.get('database', 'PostgreSQL')}
- **Autenticación**: {tech_stack.get('authentication', 'JWT')}
- **Despliegue**: {tech_stack.get('deployment', 'Docker + Vercel')}

### Comenzar

1. Instalar dependencias:
\\`\\`\\`bash
npm install
\\`\\`\\`

2. Ejecutar en desarrollo:
\\`\\`\\`bash
npm run dev
\\`\\`\\`

3. Abrir http://localhost:3000 en el navegador

### Estructura del Proyecto
- \\`src/\\` - Código fuente
- \\`package.json\\` - Dependencias y scripts
- \\`vite.config.js\\` - Configuración de build

---
*Generado el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
'''

@app.post("/api/projects/{project_id}/generate")
def generate_project(project_id: str, background_tasks: BackgroundTasks):
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["status"] != "planned":
        raise HTTPException(status_code=400, detail="Project must be planned first")
    
    job_id = str(uuid.uuid4())
    update_progress(job_id, 5, "En cola para generación de código")
    
    background_tasks.add_task(generate_worker, job_id, project_id)
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Generación de código iniciada"
    }

@app.get("/api/projects/{project_id}/download")
def download_project(project_id: str):
    project = projects_db.get(project_id)
    if not project or not project.get("result"):
        raise HTTPException(status_code=404, detail="Project not found or not generated")
    
    # En una implementación real, aquí servirías el archivo ZIP
    # Por ahora devolvemos la estructura como JSON
    return {
        "project_id": project_id,
        "project_name": project["project_name"],
        "structure": project["result"]["project_structure"],
        "download_info": project["result"]["download_info"],
        "message": "En producción, este endpoint serviría un archivo ZIP descargable"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
