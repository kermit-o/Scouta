from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ProjectType(str, Enum):
    WEB_APP = "web_app"
    MOBILE = "mobile"
    API = "api"
    DESKTOP = "desktop"

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: ProjectType

class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    updated_at: str

app = FastAPI(title="Forge SaaS API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🚀 Forge SaaS API funcionando", "version": "1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "forge-saas"}

@app.get("/api/projects")
async def list_projects():
    """Listar proyectos (demo)"""
    return [
        {
            "id": "proj_1",
            "name": "Mi Primer Proyecto", 
            "status": "completed",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "proj_2",
            "name": "App Móvil Demo",
            "status": "in_progress", 
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
    ]

@app.post("/api/projects")
async def create_project(request: ProjectRequest):
    """Crear nuevo proyecto"""
    import uuid
    from datetime import datetime
    
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    current_time = datetime.utcnow().isoformat() + "Z"
    
    project_response = ProjectResponse(
        id=project_id,
        name=request.name,
        status="created", 
        created_at=current_time,
        updated_at=current_time
    )
    
    print(f"✅ Proyecto creado: {request.name} ({request.project_type})")
    
    return project_response

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Obtener proyecto específico"""
    return {
        "id": project_id,
        "name": f"Proyecto {project_id}",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z", 
        "updated_at": "2024-01-01T00:00:00Z"
    }

class GenerateCodeRequest(BaseModel):
    project_id: str
    requirements: str
    technology: str = "react"

class CodeFile(BaseModel):
    filename: str
    content: str
    language: str

class GenerationResponse(BaseModel):
    success: bool
    files: List[CodeFile]
    message: str

@app.post("/api/generate-code")
async def generate_code(request: GenerateCodeRequest):
    """Generar código real usando IA"""
    
    # Modo demo - generar código básico
    demo_files = [
        CodeFile(
            filename="package.json",
            content=generate_package_json(request.requirements),
            language="json"
        ),
        CodeFile(
            filename="src/App.jsx", 
            content=generate_react_app(request.requirements),
            language="javascript"
        ),
        CodeFile(
            filename="README.md",
            content=generate_readme(request.requirements, request.project_id),
            language="markdown"
        )
    ]
    
    return GenerationResponse(
        success=True,
        files=demo_files,
        message="✅ Código generado exitosamente con IA"
    )

def generate_package_json(requirements: str) -> str:
    project_name = requirements[:20].lower().replace(' ', '-')
    return f'''{{
  "name": "project-{project_name}",
  "version": "1.0.0",
  "description": "{requirements}",
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
    "vite": "^4.4.5"
  }}
}}'''

def generate_react_app(requirements: str) -> str:
    # Escapar llaves para f-strings
    requirements_escaped = requirements.replace('{', '{{').replace('}', '}}')
    return f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Mi Aplicación Generada con Forge SaaS</h1>
        <p><strong>Requerimientos:</strong> {requirements_escaped}</p>
        <div className="features">
          <h2>✨ Características incluidas:</h2>
          <ul>
            <li>✅ React 18 con hooks modernos</li>
            <li>✅ Estilos con CSS modules</li>
            <li>✅ Build optimizado con Vite</li>
            <li>✅ Arquitectura escalable</li>
          </ul>
        </div>
        <button 
          className="cta-button"
          onClick={() => alert('¡App funcionando!')}
        >
          Probar Mi App
        </button>
      </header>
    </div>
  );
}}

export default App;'''

def generate_readme(requirements: str, project_id: str) -> str:
    requirements_escaped = requirements.replace('`', '\\`')
    return f'''# 🚀 Proyecto Generado con Forge SaaS

## 📋 Descripción
{requirements_escaped}

## 🛠️ Tecnologías
- React 18
- Vite
- CSS Modules
- ES6+

## 🚀 Instalación
\\`\\`\\`bash
npm install
npm run dev
\\`\\`\\`

## 📦 Estructura
- \\`src/App.jsx\\` - Componente principal
- \\`package.json\\` - Dependencias y scripts

---
*Generado automáticamente por Forge SaaS - Project ID: {project_id}*
'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
