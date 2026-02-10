# backend/app/worker.py

from __future__ import annotations
import json, time
import logging
from datetime import datetime, timezone
from typing import Callable, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, text # Importante: Añadir 'text' para el bloqueo si usas SQL
from app.core.db import SessionLocal, engine
from app.core.models.job import Job
from app.core.models.agent_run import AgentRun
# Importar todos los agentes necesarios, ahora que están consolidados
from app.agents import intake_agent, specification_agent, scaffolder_agent, builder_agent, tester_agent, documenter_agent, supervisor_agent
import sys

# Configurar logging básico (necesario en un worker)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Funciones de base de datos de apoyo (Mantenidas aquí si no pueden moverse a app.db) ---
def get_engine():
    return engine

def get_session(engine_param=None):
    return SessionLocal()


# --- Definición de Agentes y Handlers ---
AGENTS: Dict[str, Callable[[Session, str], dict]] = {
    # Usamos los nombres de archivos renombrados y limpios de la refactorización
    "intake": intake_agent.run,
    "spec": specification_agent.run,
    "scaffold": scaffolder_agent.run,
    "build": builder_agent.run,
    "test": tester_agent.run,
    "document": documenter_agent.run,
    "supervisor": supervisor_agent.run, # Añadido el supervisor
}

def _finish_agent(db: Session, project_id: str, agent: str, ok: bool, logs: str, details: dict):
    """Registra el resultado final de la ejecución de un agente."""
    run = AgentRun(project_id=project_id, agent=agent, status="ok" if ok else "failed",
                   logs=(logs or "")[:100_000], details_json=json.dumps(details or {})[:200_000],
                   started_at=datetime.now(timezone.utc), ended_at=datetime.now(timezone.utc))
    db.add(run); db.commit()

def worker_loop(poll_seconds: float = 1.0):
    engine = get_engine()
    logger.info("Worker loop started. Polling interval: %s seconds", poll_seconds)

    while True:
        with get_session(engine) as db:
            # --- Tarea Crítica: Consulta con Bloqueo de Concurrencia ---
            # 'FOR UPDATE SKIP LOCKED' asegura que solo un worker tome este job
            # Esto asume que estás usando PostgreSQL (o una DB que lo soporta).
            try:
                job = db.execute(
                    select(Job)
                    .where(Job.state == "queued")
                    .order_by(Job.created_at.asc())
                    .limit(1)
                    .with_for_update(skip_locked=True) # <- ¡CLAVE para un SaaS concurrente!
                ).scalars().first()
            except Exception as e:
                logger.error("Error during DB selection/locking: %s", e)
                time.sleep(poll_seconds)
                continue
                
            if not job:
                db.rollback() # Asegurar que la transacción se cierre limpiamente
                time.sleep(poll_seconds) 
                continue
                
            # Job encontrado: Actualizar estado a RUNNING y commitear el bloqueo
            job.state, job.attempts = "running", job.attempts + 1
            job.started_at = datetime.now(timezone.utc)
            db.commit() 
            
            logger.info("Processing Job %s (Agent: %s, Project: %s)", job.id, job.agent, job.project_id)

            ok, logs, details = False, "", {}
            try:
                # El handler debe ser llamado con los argumentos correctos
                handler = AGENTS[job.agent]
                res = handler(db, str(job.project_id)) 
                
                # Asumiendo que el resultado del agente tiene 'ok', 'logs', 'details'
                ok = bool(res.get("ok")); logs = res.get("logs",""); details = res.get("details",{})
                
            except Exception as e:
                ok, logs, details = False, f"{type(e).__name__}: {e}", {}
                logger.error("Job %s FAILED: %s", job.id, logs, exc_info=True)
                
            # Finalización: Actualizar estado final del Job
            job.state = "done" if ok else "failed"
            job.ended_at = datetime.now(timezone.utc)
            if not ok: 
                job.last_error = (logs or "")[:4000]
                
            db.commit()
            
            # Registrar la ejecución del agente (AgentRun)
            _finish_agent(db, str(job.project_id), job.agent, ok, logs, details)
            
        # Pequeño sleep para no sobrecargar la DB si hay muchos jobs
        time.sleep(0.1) 
        pass

if __name__ == "__main__":
    # intervalo 0.5s, corre infinito en prod (Ctrl+C en dev)
    poll_interval = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    worker_loop(0.5)