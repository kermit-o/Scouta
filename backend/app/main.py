
# === PATCH: progress + plan endpoints y handlers ===
from fastapi import BackgroundTasks, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

# Handlers de errores (idempotentes)
@app.exception_handler(IntegrityError)
async def _handle_integrity_error(request, exc: IntegrityError):
    return JSONResponse(status_code=422, content={"detail": "Database constraint error", "hint": str(getattr(exc, "orig", exc))})

@app.exception_handler(ProgrammingError)
async def _handle_programming_error(request, exc: ProgrammingError):
    return JSONResponse(status_code=400, content={"detail": "Invalid database operation", "hint": str(getattr(exc, "orig", exc))})

@app.exception_handler(RequestValidationError)
async def _handle_request_validation_error(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Servicios
from .services.progress_service import get_tracker
from .services.planner_service import plan_project as _plan_project

# Progress (usar project_id real)
@app.get("/api/progress/{project_id}")
def _get_progress(project_id: str):
    return get_tracker().get(project_id)

# Planificar (acepta body opcional para evitar 422)
class PlanRequest(BaseModel):
    noop: Optional[bool] = False

# get_db ya existe en este módulo; lo reutilizamos
@app.post("/api/projects/{project_id}/plan", status_code=202)
def _plan_endpoint(
    project_id: str,
    tasks: BackgroundTasks,
    payload: Optional[PlanRequest] = Body(None),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id==project_id, Project.is_deleted==False).first()  # type: ignore[name-defined]
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = "processing"
    db.add(project); db.commit()

    tasks.add_task(_plan_project, db, project_id)
    return {"ok": True, "project_id": project_id}
# === END PATCH ===
