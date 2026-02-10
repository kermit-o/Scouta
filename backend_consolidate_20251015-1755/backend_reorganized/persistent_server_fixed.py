#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
import os
import sqlite3
from datetime import datetime
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Forge SaaS - Servidor Persistente",
    description="Servidor con persistencia SQLite para generación de proyectos",
    version="2.0.0"
)

# Configuración
DB_PATH = "forge_saas.db"
PROJECTS_DIR = "generated_projects"

# Crear directorio de proyectos si no existe
os.makedirs(PROJECTS_DIR, exist_ok=True)

class ProjectCreate(BaseModel):
    project_name: str
    requirements: str
    user_id: Optional[str] = "default-user"

class Project(BaseModel):
    id: str
    user_id: str
    project_name: str
    requirements: str
    status: str = "pending"
    technology_stack: Optional[Dict[str, Any]] = None
    generated_plan: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

def init_db():
    """Inicializar base de datos SQLite"""
    logger.info(f"🗄️ Inicializando base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de proyectos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            project_name TEXT,
            requirements TEXT,
            status TEXT,
            technology_stack TEXT,
            generated_plan TEXT,
            result TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Tabla de jobs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            project_id TEXT,
            progress INTEGER,
            message TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de datos inicializada")

def get_current_time():
    return datetime.now().isoformat()

# Evento de startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("🚀 Servidor Forge SaaS iniciado")

@app.get("/")
async def root():
    return {
        "message": "Forge SaaS - Servidor Persistente", 
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy", 
        "service": "forge-saas",
        "persistence": "sqlite",
        "database": DB_PATH,
        "projects_dir": PROJECTS_DIR,
        "timestamp": get_current_time()
    }

@app.post("/api/projects", response_model=Project)
async def create_project(project_data: ProjectCreate):
    """Crear un nuevo proyecto"""
    logger.info(f"📝 Creando proyecto: {project_data.project_name}")
    
    project_id = str(uuid.uuid4())
    now = get_current_time()
    
    project = Project(
        id=project_id,
        user_id=project_data.user_id,
        project_name=project_data.project_name,
        requirements=project_data.requirements,
        status="pending",
        created_at=now,
        updated_at=now
    )
    
    # Guardar en SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO projects 
            (id, user_id, project_name, requirements, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project.id,
            project.user_id,
            project.project_name,
            project.requirements,
            project.status,
            project.created_at,
            project.updated_at
        ))
        
        conn.commit()
        logger.info(f"✅ Proyecto creado: {project_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creando proyecto: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {e}")
    finally:
        conn.close()
    
    return project

@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    """Obtener todos los proyectos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        projects = []
        for row in rows:
            project = Project(
                id=row[0],
                user_id=row[1],
                project_name=row[2],
                requirements=row[3],
                status=row[4],
                technology_stack=json.loads(row[5]) if row[5] else None,
                generated_plan=json.loads(row[6]) if row[6] else None,
                result=json.loads(row[7]) if row[7] else None,
                created_at=row[8],
                updated_at=row[9]
            )
            projects.append(project)
        
        logger.info(f"📊 Retornando {len(projects)} proyectos")
        return projects
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo proyectos: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting projects: {e}")
    finally:
        conn.close()

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Obtener un proyecto específico"""
    logger.info(f"🔍 Buscando proyecto: {project_id}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"❌ Proyecto no encontrado: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = Project(
            id=row[0],
            user_id=row[1],
            project_name=row[2],
            requirements=row[3],
            status=row[4],
            technology_stack=json.loads(row[5]) if row[5] else None,
            generated_plan=json.loads(row[6]) if row[6] else None,
            result=json.loads(row[7]) if row[7] else None,
            created_at=row[8],
            updated_at=row[9]
        )
        
        logger.info(f"✅ Proyecto encontrado: {project.project_name}")
        return project
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo proyecto: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting project: {e}")
    finally:
        conn.close()

@app.post("/api/projects/{project_id}/plan")
async def plan_project(project_id: str):
    """Planificar un proyecto"""
    logger.info(f"📋 Planificando proyecto: {project_id}")
    
    # Verificar que el proyecto existe
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, project_name FROM projects WHERE id = ?', (project_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            logger.warning(f"❌ Proyecto no encontrado para planificación: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_name = project_row[1]
        logger.info(f"📋 Planificando: {project_name}")
        
    except Exception as e:
        logger.error(f"❌ Error verificando proyecto: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking project: {e}")
    finally:
        conn.close()
    
    # Crear job de planificación
    job_id = str(uuid.uuid4())
    now = get_current_time()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (job_id, project_id, progress, message, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, project_id, 0, "Planificación iniciada", "running", now, now))
        
        conn.commit()
        logger.info(f"🎯 Job de planificación creado: {job_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creando job: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job: {e}")
    finally:
        conn.close()
    
    # Iniciar planificación asíncrona
    asyncio.create_task(simulate_planning(job_id, project_id))
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Planificación con IA iniciada",
        "ai_agents_available": True
    }

@app.post("/api/projects/{project_id}/generate")
async def generate_project(project_id: str):
    """Generar código para un proyecto"""
    logger.info(f"🏗️ Generando proyecto: {project_id}")
    
    # Verificar que el proyecto existe
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, project_name, status FROM projects WHERE id = ?', (project_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            logger.warning(f"❌ Proyecto no encontrado para generación: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_name, status = project_row[1], project_row[2]
        logger.info(f"🏗️ Generando: {project_name} (estado: {status})")
        
    except Exception as e:
        logger.error(f"❌ Error verificando proyecto: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking project: {e}")
    finally:
        conn.close()
    
    # Crear job de generación
    job_id = str(uuid.uuid4())
    now = get_current_time()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (job_id, project_id, progress, message, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, project_id, 0, "Generación de código iniciada", "running", now, now))
        
        conn.commit()
        logger.info(f"🎯 Job de generación creado: {job_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creando job: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job: {e}")
    finally:
        conn.close()
    
    # Iniciar generación asíncrona
    asyncio.create_task(simulate_generation(job_id, project_id))
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Generación de código iniciada"
    }

@app.get("/api/progress/{job_id}")
async def get_progress(job_id: str):
    """Obtener progreso de un job"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"❌ Job no encontrado: {job_id}")
            return {
                "job_id": job_id,
                "percent": 0,
                "message": "Job not found",
                "updated_at": get_current_time()
            }
        
        response = {
            "job_id": row[0],
            "percent": row[2],
            "message": row[3],
            "updated_at": row[6]
        }
        
        logger.debug(f"📊 Progreso del job {job_id}: {row[2]}%")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo progreso: {e}")
        return {
            "job_id": job_id,
            "percent": 0,
            "message": f"Error: {e}",
            "updated_at": get_current_time()
        }
    finally:
        conn.close()

async def simulate_planning(job_id: str, project_id: str):
    """Simular proceso de planificación"""
    logger.info(f"🧠 Iniciando simulación de planificación para job: {job_id}")
    
    steps = [
        (25, "Analizando requisitos del proyecto..."),
        (50, "Diseñando arquitectura de software..."),
        (75, "Seleccionando stack tecnológico..."),
        (100, "✅ Planificación completada!")
    ]
    
    for progress, message in steps:
        await asyncio.sleep(2)  # Simular trabajo
        
        # Actualizar progreso en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE jobs SET progress = ?, message = ?, updated_at = ? 
                WHERE job_id = ?
            ''', (progress, message, get_current_time(), job_id))
            conn.commit()
            logger.debug(f"📈 Job {job_id}: {progress}% - {message}")
        except Exception as e:
            logger.error(f"❌ Error actualizando progreso: {e}")
        finally:
            conn.close()
    
    # Actualizar proyecto como planificado
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE projects SET status = ?, updated_at = ? 
            WHERE id = ?
        ''', ("planned", get_current_time(), project_id))
        conn.commit()
        logger.info(f"✅ Proyecto {project_id} marcado como 'planned'")
    except Exception as e:
        logger.error(f"❌ Error actualizando proyecto: {e}")
    finally:
        conn.close()

async def simulate_generation(job_id: str, project_id: str):
    """Simular proceso de generación de código"""
    logger.info(f"💻 Iniciando simulación de generación para job: {job_id}")
    
    steps = [
        (10, "Preparando estructura del proyecto..."),
        (25, "Generando componentes React frontend..."),
        (45, "Creando API backend con Node.js..."),
        (65, "Configurando base de datos MongoDB..."),
        (85, "Aplicando estilos y diseño responsive..."),
        (100, "✅ Generación completada!")
    ]
    
    for progress, message in steps:
        await asyncio.sleep(3)  # Simular trabajo
        
        # Actualizar progreso
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE jobs SET progress = ?, message = ?, updated_at = ? 
                WHERE job_id = ?
            ''', (progress, message, get_current_time(), job_id))
            conn.commit()
            logger.debug(f"📈 Job {job_id}: {progress}% - {message}")
        except Exception as e:
            logger.error(f"❌ Error actualizando progreso: {e}")
        finally:
            conn.close()
    
    # Crear archivos de ejemplo
    project_dir = f"{PROJECTS_DIR}/{project_id}"
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        # Crear README.md
        with open(f"{project_dir}/README.md", "w") as f:
            f.write(f"""# Portal de Noticias Generado

## Descripción
Proyecto generado automáticamente por Forge SaaS.

## Características
- Frontend: React con TypeScript
- Backend: Node.js con Express
- Base de datos: MongoDB
- Autenticación: JWT

## Instalación
\`\`\`bash
npm install
npm run dev
\`\`\`

## Estructura
- `/src` - Código fuente
- `/public` - Archivos estáticos
- `/api` - Endpoints backend
""")
        
        # Crear package.json
        with open(f"{project_dir}/package.json", "w") as f:
            package_json = {
                "name": "portal-noticias",
                "version": "1.0.0",
                "description": "Portal de noticias generado automáticamente",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview",
                    "start": "node server/index.js"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "express": "^4.18.2",
                    "mongoose": "^7.5.0"
                },
                "devDependencies": {
                    "vite": "^4.4.5",
                    "@vitejs/plugin-react": "^4.0.3"
                }
            }
            json.dump(package_json, f, indent=2)
        
        # Crear estructura de directorios
        os.makedirs(f"{project_dir}/src/components", exist_ok=True)
        os.makedirs(f"{project_dir}/src/pages", exist_ok=True)
        os.makedirs(f"{project_dir}/server", exist_ok=True)
        os.makedirs(f"{project_dir}/public", exist_ok=True)
        
        # Crear App.jsx principal
        with open(f"{project_dir}/src/App.jsx", "w") as f:
            f.write("""import React from 'react'
import Header from './components/Header'
import NewsList from './components/NewsList'
import './App.css'

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <NewsList />
      </main>
    </div>
  )
}

export default App
""")
        
        # Crear archivo principal del servidor
        with open(f"{project_dir}/server/index.js", "w") as f:
            f.write("""const express = require('express')
const mongoose = require('mongoose')
const cors = require('cors')

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors())
app.use(express.json())

// Rutas
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'portal-noticias' })
})

app.get('/api/news', (req, res) => {
  res.json({ news: [] })
})

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor ejecutándose en puerto ${PORT}`)
})
""")
        
        # Crear Vite config
        with open(f"{project_dir}/vite.config.js", "w") as f:
            f.write("""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:3001'
    }
  }
})
""")
        
        logger.info(f"📁 Archivos generados en: {project_dir}")
        
    except Exception as e:
        logger.error(f"❌ Error generando archivos: {e}")
    
    # Actualizar proyecto como generado
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE projects SET status = ?, updated_at = ? 
            WHERE id = ?
        ''', ("generated", get_current_time(), project_id))
        conn.commit()
        logger.info(f"✅ Proyecto {project_id} marcado como 'generated'")
    except Exception as e:
        logger.error(f"❌ Error actualizando proyecto: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🚀 Iniciando Forge SaaS - Servidor Persistente v2.0.0")
    logger.info("📍 http://localhost:8001")
    logger.info("🗄️  Base de datos: forge_saas.db")
    logger.info("📁 Proyectos: generated_projects/")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001, 
        log_level="info",
        access_log=True
    )
