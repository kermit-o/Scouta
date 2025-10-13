
from starlette.requests import Request
import os, uuid, threading, time, logging, shutil, json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, ProgrammingError

from app.models.project import Base, Project

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://forge:forge@postgres:5432/forge")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(redirect_slashes=False, title="Forge Backend", openapi_url="/api/openapi.json", docs_url="/api/docs")



# PATCH 2025-09-20: progress guard
@app.middleware("http")
async def _progress_guard(request: Request, call_next):
    p = request.url.path
    # /api/progress o /api/progress/
    if p.rstrip("/") == "/api/progress":
        return JSONResponse(status_code=400, content={"detail": "Missing job_id"})
    # /api/progress/<id> con valores nulos/comunes
    if p.startswith("/api/progress/"):
        last = p.split("/")[-1].lower()
        if last in {"null", "none", "undefined", ""}:
            return JSONResponse(status_code=400, content={"detail": "Invalid job_id"})
    return await call_next(request)
origins = [
    os.getenv("CORS_ORIGIN", "*"),
    "http://localhost",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://ui:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)

@app.exception_handler(IntegrityError)
async def handle_integrity_error(request, exc: IntegrityError):
    return JSONResponse(status_code=422, content={"detail": "Database constraint error","hint": str(getattr(exc, "orig", exc))})

@app.exception_handler(ProgrammingError)
async def handle_programming_error(request, exc: ProgrammingError):
    return JSONResponse(status_code=400, content={"detail": "Invalid database operation","hint": str(getattr(exc, "orig", exc))})

@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# ---------- progreso en memoria ----------
_PROGRESS: Dict[str, Dict[str, Any]] = {}
_TTL = 60 * 30
def set_progress(job_id: str, percent: int, message: str):
    _PROGRESS[job_id] = {"job_id": job_id, "percent": max(0, min(100, percent)), "message": message, "updated_at": datetime.utcnow().isoformat()+"Z"}
def get_progress(job_id: str):
    return _PROGRESS.get(job_id, {"job_id": job_id, "percent": 0, "message": "unknown job"})
def _cleanup_loop():
    while True:
        now = datetime.utcnow()
        for k, v in list(_PROGRESS.items()):
            try: updated = datetime.fromisoformat(v["updated_at"].replace("Z",""))
            except Exception: updated = now
            if (now - updated) > timedelta(seconds=_TTL):
                _PROGRESS.pop(k, None)
        time.sleep(30)
threading.Thread(target=_cleanup_loop, daemon=True).start()

# ---------- rutas ----------
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
    p = Project(
        user_id=payload["user_id"],
        project_name=payload["project_name"],
        requirements=payload["requirements"],
        status="pending",
        technology_stack=None,
        generated_plan=None,
    )
    db.add(p); db.flush(); db.refresh(p); db.commit()
    return jsonable_encoder(p)

@app.get("/api/progress/{job_id}")
def progress(job_id: str):
    return get_progress(job_id)

# ---- worker de planificación (igual que tenías, con leves ajustes) ----
def _plan_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Project created")
        proj = db.get(Project, project_id)
        if not proj:
            set_progress(job_id, 100, "Project not found"); return
        set_progress(job_id, 25, "Analyzing requirements"); time.sleep(0.3)
        tech = {"frontend":"Flutter","backend":"Python + Flask","db":"PostgreSQL","realtime":"Socket.IO + Redis","auth":"JWT"}
        set_progress(job_id, 45, "Drafting plan"); time.sleep(0.3)
        plan = {"steps":[
            "Create Flask app skeleton","Add SQLAlchemy models: User, Room, Task","JWT auth endpoints",
            "CRUD /rooms /tasks","Socket.IO notifications","Flutter login + dashboard","Dockerfiles & README","Basic tests"
        ],"notes":"Auto-generated draft plan"}
        set_progress(job_id, 70, "Saving plan")
        proj.status = "planned"; proj.technology_stack = tech; proj.generated_plan = plan; proj.updated_at = datetime.utcnow()
        db.add(proj); db.commit()
        set_progress(job_id, 100, "Done")
    except Exception:
        logging.exception("Plan worker failed"); set_progress(job_id, 100, "error: worker failed")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/plan")
def plan_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.get(Project, project_id)
    if not proj: raise HTTPException(status_code=404, detail="Project not found")
    job_id = str(uuid.uuid4()); set_progress(job_id, 5, "Queued")
    threading.Thread(target=_plan_worker, args=(job_id, project_id), daemon=True).start()
    return {"job_id": job_id, "project_id": project_id, "started": True}

# ---- worker de generación de app ----
GEN_DIR = os.getenv("GEN_DIR", "/app/generated")

def _write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

def _generate_worker(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        set_progress(job_id, 10, "Preparing workspace")
        proj = db.get(Project, project_id)
        if not proj:
            set_progress(job_id, 100, "Project not found"); return
        base = os.path.join(GEN_DIR, project_id); 
        if os.path.exists(base): shutil.rmtree(base)
        os.makedirs(base, exist_ok=True)

        # Backend Flask mínimo
        set_progress(job_id, 30, "Scaffolding backend")
        be_dir = os.path.join(base, "backend"); os.makedirs(be_dir, exist_ok=True)
        _write(os.path.join(be_dir, "requirements.txt"), "Flask==3.0.0\nFlask-Cors==4.0.0\nSQLAlchemy==2.0.29\npsycopg2-binary==2.9.9\npython-dotenv==1.0.1\n")
        _write(os.path.join(be_dir, "app.py"), """import os
from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    @app.get(/health)
    def health(): return jsonify(status=ok)
    return app

if __name__ == __main__:
    app = create_app()
    app.run(host=0.0.0.0, port=int(os.getenv(PORT, 5000)))
""")
        _write(os.path.join(be_dir, "Dockerfile"), """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
""")

        # Frontend placeholder (Flutter instrucc.)
        set_progress(job_id, 50, "Preparing frontend placeholder")
        fe_dir = os.path.join(base, "frontend"); os.makedirs(fe_dir, exist_ok=True)
        _write(os.path.join(fe_dir, "README.md"), "# Flutter app\n\nRun `flutter create .` aquí y añade login + dashboard.\n")

        # README raíz
        _write(os.path.join(base, "README.md"), f"# {proj.project_name}\n\nBackend Flask + placeholder Flutter.\n\nGenerado por Forge a {datetime.utcnow().isoformat()}Z.\n")

        set_progress(job_id, 70, "Packaging")
        zip_path = shutil.make_archive(base, "zip", base)  # devuelve /app/generated/<id>.zip

        # Guarda resultado en DB
        proj.status = "generated"
        proj.result = {"zip_path": zip_path, "zip_url": f"/api/projects/{project_id}/download", "generated_at": datetime.utcnow().isoformat()+"Z"}
        proj.updated_at = datetime.utcnow()
        db.add(proj); db.commit()

        set_progress(job_id, 100, "Artifact ready")
    except Exception:
        logging.exception("Generate worker failed")
        set_progress(job_id, 100, "error: generator failed")
    finally:
        db.close()

@app.post("/api/projects/{project_id}/generate")
def generate_project(project_id: str, _: Optional[Dict[str, Any]] = Body(default=None), db: Session = Depends(get_db)):
    proj = db.get(Project, project_id)
    if not proj: raise HTTPException(status_code=404, detail="Project not found")
    job_id = str(uuid.uuid4()); set_progress(job_id, 5, "Queued")
    threading.Thread(target=_generate_worker, args=(job_id, project_id), daemon=True).start()
    return {"job_id": job_id, "project_id": project_id, "started": True}

@app.get("/api/projects/{project_id}/download")
def download_artifact(project_id: str, db: Session = Depends(get_db)):
    proj = db.get(Project, project_id)
    if not proj or not proj.result or not proj.result.get("zip_path"):
        raise HTTPException(status_code=404, detail="Artifact not found")
    path = proj.result["zip_path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on disk")
    filename = os.path.basename(path)
    return FileResponse(path, media_type="application/zip", filename=filename)



# Guard friendly: /api/progress sin job_id
@app.get("/api/progress")
def progress_root():
    raise HTTPException(
        status_code=400,
        detail="Missing job_id. Use /api/progress/{job_id}."
    )
