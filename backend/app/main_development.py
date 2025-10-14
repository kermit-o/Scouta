from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, ProgrammingError
import os, uuid, threading, time, logging, shutil, json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

# Usar SQLite para desarrollo
DATABASE_URL = "sqlite:///./forge_dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Project para SQLite
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    requirements = Column(Text, nullable=False)
    status = Column(String, default="pending")
    technology_stack = Column(JSON, nullable=True)
    generated_plan = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(redirect_slashes=False, title="Forge Backend - Development", 
              openapi_url="/api/openapi.json", docs_url="/api/docs")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejo de errores
@app.exception_handler(IntegrityError)
async def handle_integrity_error(request, exc: IntegrityError):
    return JSONResponse(status_code=422, content={"detail": "Database constraint error"})

@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# ---------- progreso en memoria ----------
_PROGRESS: Dict[str, Dict[str, Any]] = {}
_TTL = 60 * 30

def set_progress(job_id: str, percent: int, message: str):
    _PROGRESS[job_id] = {
        "job_id": job_id, 
        "percent": max(0, min(100, percent)), 
        "message": message, 
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

def get_progress(job_id: str):
    return _PROGRESS.get(job_id, {
        "job_id": job_id, 
        "percent": 0, 
        "message": "unknown job"
    })

def _cleanup_loop():
    while True:
        now = datetime.utcnow()
        for k, v in list(_PROGRESS.items()):
            try: 
                updated = datetime.fromisoformat(v["updated_at"].replace("Z", ""))
            except Exception: 
                updated = now
            if (now - updated) > timedelta(seconds=_TTL):
                _PROGRESS.pop(k, None)
        time.sleep(30)

threading.Thread(target=_cleanup_loop, daemon=True).start()

# ---------- rutas ----------
@app.get("/")
async def root():
    return {"message": "🚀 Forge SaaS API funcionando (Development Mode)", "version": "1.0"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    items = db.query(Project).filter(Project.is_deleted == False).order_by(Project.created_at.desc()).all()
    return jsonable_encoder(items)

@app.post("/api/projects", status_code=201)
def create_project(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    required = ["user_id", "project_name", "requirements"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        missing_str = ", ".join(missing)
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing_str}")
    
    project_id = str(uuid.uuid4())
    p = Project(
        id=project_id,
        user_id=payload["user_id"],
        project_name=payload["project_name"],
        requirements=payload["requirements"],
        status="pending",
        technology_stack=None,
        generated_plan=None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return jsonable_encoder(p)

@app.get("/api/progress/{job_id}")
def progress(job_id: str):
    return get_progress(job_id)

# ---- worker de planificación ----
def _plan_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Project created")
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            set_progress(job_id, 100, "Project not found")
            return
        
        set_progress(job_id, 25, "Analyzing requirements")
        time.sleep(1)
        
        # Análisis mejorado con IA simulada
        requirements = proj.requirements.lower()
        tech_stack = {
            "frontend": "React with TypeScript" if "web" in requirements else "Flutter",
            "backend": "Python FastAPI" if "api" in requirements else "Node.js Express",
            "database": "PostgreSQL",
            "authentication": "JWT",
            "deployment": "Docker"
        }
        
        set_progress(job_id, 45, "Drafting architecture plan")
        time.sleep(1)
        
        plan = {
            "steps": [
                "Setup project structure and dependencies",
                "Implement database models and migrations",
                "Create API endpoints and authentication",
                "Build frontend components and routing",
                "Add styling and responsive design",
                "Implement business logic and features",
                "Write tests and documentation",
                "Dockerize application for deployment"
            ],
            "architecture": tech_stack,
            "estimated_time": "2-4 weeks",
            "complexity": "Intermediate"
        }
        
        set_progress(job_id, 70, "Saving plan to database")
        proj.status = "planned"
        proj.technology_stack = tech_stack
        proj.generated_plan = plan
        proj.updated_at = datetime.utcnow()
        db.commit()
        
        set_progress(job_id, 100, "Project planning completed successfully")
    except Exception as e:
        logging.exception("Plan worker failed")
        set_progress(job_id, 100, f"Error: {str(e)}")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/plan")
def plan_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    set_progress(job_id, 5, "Queued for planning")
    threading.Thread(target=_plan_worker, args=(job_id, project_id), daemon=True).start()
    
    return {
        "job_id": job_id, 
        "project_id": project_id, 
        "started": True,
        "message": "AI planning process started"
    }

# ---- worker de generación de app ----
GEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated")

def _write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _generate_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Preparing workspace")
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            set_progress(job_id, 100, "Project not found")
            return
        
        base_dir = os.path.join(GEN_DIR, project_id)
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.makedirs(base_dir, exist_ok=True)

        # Generar estructura del proyecto basada en el plan
        set_progress(job_id, 30, "Generating project structure")
        
        tech_stack = proj.technology_stack or {}
        frontend = tech_stack.get("frontend", "React")
        
        if frontend == "React":
            # Generar proyecto React
            _write(os.path.join(base_dir, "package.json"), '''{
  "name": "''' + proj.project_name.lower().replace(' ', '-') + '''",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^4.4.5",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}''')

            _write(os.path.join(base_dir, "vite.config.js"), '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})''')

            _write(os.path.join(base_dir, "index.html"), '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>''' + proj.project_name + '''</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>''')

            os.makedirs(os.path.join(base_dir, "src"), exist_ok=True)
            _write(os.path.join(base_dir, "src", "main.jsx"), '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''')

            _write(os.path.join(base_dir, "src", "App.jsx"), '''import React from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 ''' + proj.project_name + '''</h1>
        <p><strong>Generated by Forge SaaS</strong></p>
        <div className="features">
          <h2>Project Requirements:</h2>
          <p>''' + proj.requirements + '''</p>
          <h3>Technology Stack:</h3>
          <ul>
            <li>Frontend: ''' + tech_stack.get('frontend', 'React') + '''</li>
            <li>Backend: ''' + tech_stack.get('backend', 'FastAPI') + '''</li>
            <li>Database: ''' + tech_stack.get('database', 'PostgreSQL') + '''</li>
          </ul>
        </div>
        <button 
          className="cta-button"
          onClick={() => alert('Hello from your generated app!')}
        >
          Test Your App
        </button>
      </header>
    </div>
  )
}

export default App''')

            _write(os.path.join(base_dir, "src", "App.css"), '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 40px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cta-button {
  background-color: #61dafb;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
}

.cta-button:hover {
  background-color: #21a0c4;
}

.features {
  max-width: 600px;
  margin: 20px 0;
}

.features ul {
  text-align: left;
  display: inline-block;
}''')

            _write(os.path.join(base_dir, "src", "index.css"), '''body {
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
}''')

        set_progress(job_id, 70, "Creating documentation")
        
        # README del proyecto
        _write(os.path.join(base_dir, "README.md"), '''# ''' + proj.project_name + '''

## Description
''' + proj.requirements + '''

## Generated by Forge SaaS

This project was automatically generated by Forge SaaS AI.

### Technology Stack
- Frontend: ''' + tech_stack.get('frontend', 'React') + '''
- Backend: ''' + tech_stack.get('backend', 'FastAPI') + '''
- Database: ''' + tech_stack.get('database', 'PostgreSQL') + '''
- Authentication: ''' + tech_stack.get('authentication', 'JWT') + '''

### Getting Started

1. Install dependencies:
\\`\\`\\`bash
npm install
\\`\\`\\`

2. Start development server:
\\`\\`\\`bash
npm run dev
\\`\\`\\`

3. Open http://localhost:3000 in your browser

### Project Structure
- `src/` - Source code
- `package.json` - Dependencies and scripts
- `vite.config.js` - Build configuration

---
*Generated on ''' + datetime.utcnow().isoformat() + '''*
''')

        set_progress(job_id, 85, "Packaging project")
        
        # Crear archivo ZIP
        zip_path = shutil.make_archive(base_dir, 'zip', base_dir)

        # Actualizar base de datos
        proj.status = "generated"
        proj.result = {
            "zip_path": zip_path,
            "zip_url": f"/api/projects/{project_id}/download",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "project_size": f"{os.path.getsize(zip_path)} bytes"
        }
        proj.updated_at = datetime.utcnow()
        db.commit()

        set_progress(job_id, 100, "Project generation completed!")
        
    except Exception as e:
        logging.exception("Generate worker failed")
        set_progress(job_id, 100, f"Error: {str(e)}")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/generate")
def generate_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if proj.status != "planned":
        raise HTTPException(status_code=400, detail="Project must be planned first")
    
    job_id = str(uuid.uuid4())
    set_progress(job_id, 5, "Queued for code generation")
    threading.Thread(target=_generate_worker, args=(job_id, project_id), daemon=True).start()
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Code generation started"
    }

@app.get("/api/projects/{project_id}/download")
def download_artifact(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj or not proj.result or not proj.result.get("zip_path"):
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    path = proj.result["zip_path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on disk")
    
    filename = f"{proj.project_name.replace(' ', '_')}.zip"
    return FileResponse(path, media_type="application/zip", filename=filename)

@app.get("/api/progress")
def progress_root():
    raise HTTPException(status_code=400, detail="Missing job_id. Use /api/progress/{job_id}.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOFcd /workspaces/Scouta/forge_saas/backend

# Primero, crear una versión del backend que use SQLite para desarrollo
cat > app/main_development.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, ProgrammingError
import os, uuid, threading, time, logging, shutil, json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

# Usar SQLite para desarrollo
DATABASE_URL = "sqlite:///./forge_dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Project para SQLite
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    requirements = Column(Text, nullable=False)
    status = Column(String, default="pending")
    technology_stack = Column(JSON, nullable=True)
    generated_plan = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(redirect_slashes=False, title="Forge Backend - Development", 
              openapi_url="/api/openapi.json", docs_url="/api/docs")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejo de errores
@app.exception_handler(IntegrityError)
async def handle_integrity_error(request, exc: IntegrityError):
    return JSONResponse(status_code=422, content={"detail": "Database constraint error"})

@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# ---------- progreso en memoria ----------
_PROGRESS: Dict[str, Dict[str, Any]] = {}
_TTL = 60 * 30

def set_progress(job_id: str, percent: int, message: str):
    _PROGRESS[job_id] = {
        "job_id": job_id, 
        "percent": max(0, min(100, percent)), 
        "message": message, 
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

def get_progress(job_id: str):
    return _PROGRESS.get(job_id, {
        "job_id": job_id, 
        "percent": 0, 
        "message": "unknown job"
    })

def _cleanup_loop():
    while True:
        now = datetime.utcnow()
        for k, v in list(_PROGRESS.items()):
            try: 
                updated = datetime.fromisoformat(v["updated_at"].replace("Z", ""))
            except Exception: 
                updated = now
            if (now - updated) > timedelta(seconds=_TTL):
                _PROGRESS.pop(k, None)
        time.sleep(30)

threading.Thread(target=_cleanup_loop, daemon=True).start()

# ---------- rutas ----------
@app.get("/")
async def root():
    return {"message": "🚀 Forge SaaS API funcionando (Development Mode)", "version": "1.0"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    items = db.query(Project).filter(Project.is_deleted == False).order_by(Project.created_at.desc()).all()
    return jsonable_encoder(items)

@app.post("/api/projects", status_code=201)
def create_project(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    required = ["user_id", "project_name", "requirements"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        missing_str = ", ".join(missing)
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing_str}")
    
    project_id = str(uuid.uuid4())
    p = Project(
        id=project_id,
        user_id=payload["user_id"],
        project_name=payload["project_name"],
        requirements=payload["requirements"],
        status="pending",
        technology_stack=None,
        generated_plan=None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return jsonable_encoder(p)

@app.get("/api/progress/{job_id}")
def progress(job_id: str):
    return get_progress(job_id)

# ---- worker de planificación ----
def _plan_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Project created")
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            set_progress(job_id, 100, "Project not found")
            return
        
        set_progress(job_id, 25, "Analyzing requirements")
        time.sleep(1)
        
        # Análisis mejorado con IA simulada
        requirements = proj.requirements.lower()
        tech_stack = {
            "frontend": "React with TypeScript" if "web" in requirements else "Flutter",
            "backend": "Python FastAPI" if "api" in requirements else "Node.js Express",
            "database": "PostgreSQL",
            "authentication": "JWT",
            "deployment": "Docker"
        }
        
        set_progress(job_id, 45, "Drafting architecture plan")
        time.sleep(1)
        
        plan = {
            "steps": [
                "Setup project structure and dependencies",
                "Implement database models and migrations",
                "Create API endpoints and authentication",
                "Build frontend components and routing",
                "Add styling and responsive design",
                "Implement business logic and features",
                "Write tests and documentation",
                "Dockerize application for deployment"
            ],
            "architecture": tech_stack,
            "estimated_time": "2-4 weeks",
            "complexity": "Intermediate"
        }
        
        set_progress(job_id, 70, "Saving plan to database")
        proj.status = "planned"
        proj.technology_stack = tech_stack
        proj.generated_plan = plan
        proj.updated_at = datetime.utcnow()
        db.commit()
        
        set_progress(job_id, 100, "Project planning completed successfully")
    except Exception as e:
        logging.exception("Plan worker failed")
        set_progress(job_id, 100, f"Error: {str(e)}")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/plan")
def plan_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    set_progress(job_id, 5, "Queued for planning")
    threading.Thread(target=_plan_worker, args=(job_id, project_id), daemon=True).start()
    
    return {
        "job_id": job_id, 
        "project_id": project_id, 
        "started": True,
        "message": "AI planning process started"
    }

# ---- worker de generación de app ----
GEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "generated")

def _write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _generate_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Preparing workspace")
        proj = db.query(Project).filter(Project.id == project_id).first()
        if not proj:
            set_progress(job_id, 100, "Project not found")
            return
        
        base_dir = os.path.join(GEN_DIR, project_id)
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.makedirs(base_dir, exist_ok=True)

        # Generar estructura del proyecto basada en el plan
        set_progress(job_id, 30, "Generating project structure")
        
        tech_stack = proj.technology_stack or {}
        frontend = tech_stack.get("frontend", "React")
        
        if frontend == "React":
            # Generar proyecto React
            _write(os.path.join(base_dir, "package.json"), '''{
  "name": "''' + proj.project_name.lower().replace(' ', '-') + '''",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^4.4.5",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}''')

            _write(os.path.join(base_dir, "vite.config.js"), '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})''')

            _write(os.path.join(base_dir, "index.html"), '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>''' + proj.project_name + '''</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>''')

            os.makedirs(os.path.join(base_dir, "src"), exist_ok=True)
            _write(os.path.join(base_dir, "src", "main.jsx"), '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''')

            _write(os.path.join(base_dir, "src", "App.jsx"), '''import React from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 ''' + proj.project_name + '''</h1>
        <p><strong>Generated by Forge SaaS</strong></p>
        <div className="features">
          <h2>Project Requirements:</h2>
          <p>''' + proj.requirements + '''</p>
          <h3>Technology Stack:</h3>
          <ul>
            <li>Frontend: ''' + tech_stack.get('frontend', 'React') + '''</li>
            <li>Backend: ''' + tech_stack.get('backend', 'FastAPI') + '''</li>
            <li>Database: ''' + tech_stack.get('database', 'PostgreSQL') + '''</li>
          </ul>
        </div>
        <button 
          className="cta-button"
          onClick={() => alert('Hello from your generated app!')}
        >
          Test Your App
        </button>
      </header>
    </div>
  )
}

export default App''')

            _write(os.path.join(base_dir, "src", "App.css"), '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 40px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.cta-button {
  background-color: #61dafb;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
}

.cta-button:hover {
  background-color: #21a0c4;
}

.features {
  max-width: 600px;
  margin: 20px 0;
}

.features ul {
  text-align: left;
  display: inline-block;
}''')

            _write(os.path.join(base_dir, "src", "index.css"), '''body {
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
}''')

        set_progress(job_id, 70, "Creating documentation")
        
        # README del proyecto
        _write(os.path.join(base_dir, "README.md"), '''# ''' + proj.project_name + '''

## Description
''' + proj.requirements + '''

## Generated by Forge SaaS

This project was automatically generated by Forge SaaS AI.

### Technology Stack
- Frontend: ''' + tech_stack.get('frontend', 'React') + '''
- Backend: ''' + tech_stack.get('backend', 'FastAPI') + '''
- Database: ''' + tech_stack.get('database', 'PostgreSQL') + '''
- Authentication: ''' + tech_stack.get('authentication', 'JWT') + '''

### Getting Started

1. Install dependencies:
\\`\\`\\`bash
npm install
\\`\\`\\`

2. Start development server:
\\`\\`\\`bash
npm run dev
\\`\\`\\`

3. Open http://localhost:3000 in your browser

### Project Structure
- `src/` - Source code
- `package.json` - Dependencies and scripts
- `vite.config.js` - Build configuration

---
*Generated on ''' + datetime.utcnow().isoformat() + '''*
''')

        set_progress(job_id, 85, "Packaging project")
        
        # Crear archivo ZIP
        zip_path = shutil.make_archive(base_dir, 'zip', base_dir)

        # Actualizar base de datos
        proj.status = "generated"
        proj.result = {
            "zip_path": zip_path,
            "zip_url": f"/api/projects/{project_id}/download",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "project_size": f"{os.path.getsize(zip_path)} bytes"
        }
        proj.updated_at = datetime.utcnow()
        db.commit()

        set_progress(job_id, 100, "Project generation completed!")
        
    except Exception as e:
        logging.exception("Generate worker failed")
        set_progress(job_id, 100, f"Error: {str(e)}")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/generate")
def generate_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if proj.status != "planned":
        raise HTTPException(status_code=400, detail="Project must be planned first")
    
    job_id = str(uuid.uuid4())
    set_progress(job_id, 5, "Queued for code generation")
    threading.Thread(target=_generate_worker, args=(job_id, project_id), daemon=True).start()
    
    return {
        "job_id": job_id,
        "project_id": project_id,
        "started": True,
        "message": "Code generation started"
    }

@app.get("/api/projects/{project_id}/download")
def download_artifact(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj or not proj.result or not proj.result.get("zip_path"):
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    path = proj.result["zip_path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on disk")
    
    filename = f"{proj.project_name.replace(' ', '_')}.zip"
    return FileResponse(path, media_type="application/zip", filename=filename)

@app.get("/api/progress")
def progress_root():
    raise HTTPException(status_code=400, detail="Missing job_id. Use /api/progress/{job_id}.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
