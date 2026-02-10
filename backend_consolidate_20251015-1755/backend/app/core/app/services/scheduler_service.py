# backend/app/services/scheduler_service.py

from __future__ import annotations
from sqlalchemy.orm import Session
from backend.app.core.db import SessionLocal, engine
from backend.app.core.models.job import Job
from backend.app.core.app.agents.supervisor import run as supervisor_run # Necesario si se llama directamente

# Funciones de base de datos de apoyo
def get_engine():
    return engine

def get_session(engine_param=None):
    return SessionLocal()

# Definición del pipeline de agentes (solo la lista, la ejecución va al worker)
PIPELINE = ["intake", "spec", "scaffold", "build", "test", "document"]

def enqueue_pipeline(db: Session, project_id: str) -> None:
    """
    Crea todos los jobs para un proyecto en el estado 'queued'.
    """
    for a in PIPELINE:
        # Nota: Asegúrate que el campo 'state' en tu modelo Job use la cadena 'queued'
        db.add(Job(project_id=project_id, agent=a, state="queued"))
    db.commit()

# --- Supervisor Enqueue (Refactorizado para ser asíncrono) ---

def enqueue_supervisor_job(project_id: str, requirements: str) -> str:
    """
    Crea un único job para el supervisor en la cola.
    El worker.py se encargará de ejecutarlo.
    """
    db = get_session()
    try:
        # Puedes crear un Job tipo 'supervisor' aquí. 
        # Añadir 'requirements' como dato en el Job (si el modelo lo soporta)
        db.add(Job(project_id=project_id, agent="supervisor", state="queued", requirements_text=requirements))
        db.commit()
        return project_id
    finally:
        db.close()
        
# ELIMINAR todo lo demás: AGENTS, _finish_agent, worker_loop y el bloque if __name__ == "__main__":
# La ejecución síncrona de supervisor se elimina para evitar timeouts de la API.