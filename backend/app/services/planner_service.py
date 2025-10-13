from time import sleep
from sqlalchemy.orm import Session
from .progress_service import get_tracker
from ..models.project import Project

def _infer_stack(req: str):
    req_l = (req or "").lower()
    stack = {"frontend": [], "backend": [], "database": []}
    if "flutter" in req_l: stack["frontend"].append("Flutter")
    if "fastapi" in req_l: stack["backend"].append("Python/FastAPI")
    if "flask" in req_l and "Python/FastAPI" not in stack["backend"]: stack["backend"].append("Python/Flask")
    if "postgres" in req_l or "postgresql" in req_l: stack["database"].append("PostgreSQL")
    if not any(stack.values()):
        stack["backend"].append("Python/FastAPI")
        stack["database"].append("PostgreSQL")
    return stack

def plan_project(db: Session, project_id: str):
    tracker = get_tracker()
    tracker.start(project_id, "Validating input")

    proj = db.query(Project).filter(Project.id==project_id, Project.is_deleted==False).first()
    if not proj:
        tracker.update(project_id, 100, "project not found")
        tracker.complete(project_id, "not found")
        return

    steps = [
        ("Validating", 10),
        ("Extracting stack", 30),
        ("Drafting plan", 55),
        ("Generating structure", 70),
        ("Preparing docs", 85),
        ("Finalizing", 100),
    ]

    tech = _infer_stack(proj.requirements or "")
    plan = {
        "entities": ["users", "rooms", "tasks"],
        "endpoints": ["/health", "/rooms", "/tasks"],
        "notes": "MVP skeleton. Expand with auth + sockets in next iteration."
    }

    for msg, pct in steps:
        sleep(0.3)  # simula trabajo
        tracker.update(project_id, pct, msg)

    proj.status = "planned"
    proj.technology_stack = tech
    proj.generated_plan = plan
    db.add(proj)
    db.commit()

    tracker.complete(project_id, "planned")
