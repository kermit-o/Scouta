"""
Forge SaaS - Project Supervisor Agent

Orquesta la secuencia completa de agentes y maneja la persistencia del estado
y los resultados en la base de datos (DB).
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import json # <--- AGREGADO: Necesario para json.dumps

from sqlalchemy.orm import Session
from sqlalchemy import text # Usado solo si se necesita SQL crudo

# Importar modelos (Asegúrate de que estas rutas son correctas en tu proyecto)
from backend.app.core.database.models import Project
from backend.app.core.database.models import Job # Asumiendo que esta tabla existe y está relacionada
from backend.app.core.database.models import AgentRun
from backend.app.core.db.session import SessionLocal # Asumiendo que esta es la forma de obtener una sesión

# Importar todos los agentes como CLASES (Asegúrate de que estas rutas son correctas)
from backend.app.core.app.agents.intake_agent import IntakeAgent
from backend.app.core.app.agents.specification_agent import SpecificationAgent
from backend.app.core.app.agents.data_design_agent import DataDesignAgent
from backend.app.core.app.agents.planning_agent import PlanningAgent
from backend.app.core.app.agents.builder_agent import BuilderAgent
from backend.app.core.app.agents.documenter_agent import DocumenterAgent
from backend.app.core.app.agents.tester_agent import TesterAgent
from backend.app.core.app.agents.agent_base import AgentBase # Asumiendo una clase base

# --- NUEVOS AGENTES IMPORTADOS ---
from backend.app.core.app.agents.mockup_agent import MockupAgent
from backend.app.core.app.agents.security_agent import SecurityAgent
# ---------------------------------

logger = logging.getLogger(__name__)

# Definimos el máximo de ciclos de corrección para prevenir bucles infinitos
MAX_CORRECTION_CYCLES = 3

class ProjectSupervisor:
    """Orchestrates the complete project generation pipeline"""
    
    def __init__(self, db: Optional[Session] = None):
        """Inicializa el supervisor, aceptando una sesión de DB inyectada."""
        self.db = db if db else SessionLocal()
        
        # Definición de la secuencia de agentes (ID, Descripción, Instancia)
        self.agent_sequence = [
            ("intake", "Requirements Analysis", IntakeAgent()),
            ("spec", "Specification Drafting", SpecificationAgent()),
            ("data_design", "Database Design", DataDesignAgent()), 
            ("planning", "Architecture Planning", PlanningAgent()),
            
            # --- PAUSA PARA REVISIÓN DE UX ---
            ("mockup", "Frontend Mockup Generation (UX Review)", MockupAgent()),
            # --------------------------------------
            
            ("builder", "Code Generation", BuilderAgent()),
            ("tester", "Functional Testing", TesterAgent()), 
            ("security", "Security Audit (SAST)", SecurityAgent()), # Nuevo paso de auditoría
            ("documenter", "Documentation", DocumenterAgent()),
        ]
    
    def run_pipeline(self, project_id: uuid.UUID) -> dict:
        """
        Ejecuta el pipeline completo de agentes para un proyecto.
        Implementa el ciclo de corrección (Builder -> Tester -> Security) hasta 3 veces.
        """
        logger.info(f"Starting pipeline for project {project_id}")
        
        # Obtener el proyecto inicial
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found in DB.")
            return {"project_id": project_id, "pipeline_status": "failed"}

        # current_requirements será el objeto de trabajo que pasa entre agentes
        current_requirements = project.specification
        current_requirements["raw_requirements"] = project.requirements
        
        pipeline_successful = True
        needs_rebuild = False
        correction_cycle = 0

        # Determinar desde dónde empezar (para reanudación o corrección)
        start_agent_index = 0
        if project.status == "MOCKUP_APPROVED" or "CORRECTION" in project.status:
             # Si se aprobó el mockup o se requiere corrección, empezar desde el Builder
            start_agent_index = next((i for i, (aid, *_) in enumerate(self.agent_sequence) if aid == "builder"), 0)


        # --- Bucle de Corrección (Se ejecutará al menos una vez) ---
        while correction_cycle < MAX_CORRECTION_CYCLES:
            
            if not pipeline_successful:
                break

            needs_rebuild = False # Reiniciamos la bandera para este ciclo
            
            # Ejecutar el pipeline de agentes
            for i in range(start_agent_index, len(self.agent_sequence)):
                agent_id, description, agent_instance = self.agent_sequence[i]

                try:
                    # Lógica de Pausa UX (se salta si ya está en fases de construcción/prueba)
                    if project.status == "UX_REVIEW_PENDING" and agent_id != "mockup":
                        logger.info("Pipeline paused for UX review. Skipping agent execution.")
                        continue
                    
                    # Si estamos en un ciclo de corrección, el documenter se salta hasta el final exitoso
                    if correction_cycle > 0 and agent_id == "documenter":
                        logger.info("Skipping Documenter during correction cycle.")
                        continue

                    logger.info(f"Running {agent_id} agent (Cycle {correction_cycle + 1}): {description}")
                    
                    # 1. Crear registro de AgentRun
                    agent_run = AgentRun(
                        job_id=project.job_id, 
                        agent_name=agent_id,
                        status="running",
                        started_at=datetime.utcnow(),
                    )
                    self.db.add(agent_run)
                    self.db.commit()
                    
                    # 2. Ejecutar el agente
                    start_time = datetime.utcnow()
                    agent_result = agent_instance.run(project_id, current_requirements) 
                    end_time = datetime.utcnow()
                    
                    # 3. Actualizar AgentRun (Métricas y Estado)
                    duration = (end_time - start_time).total_seconds()
                    agent_run.status = agent_result.get("status", "completed")
                    agent_run.completed_at = end_time
                    agent_run.duration_seconds = duration
                    agent_run.token_count_in = agent_result.get("token_count_in", 0)
                    agent_run.token_count_out = agent_result.get("token_count_out", 0)
                    agent_run.prompt_sent = agent_result.get("prompt_sent", "N/A")
                    agent_run.response_raw = json.dumps(agent_result)
                    
                    
                    if agent_run.status == "failed" or "error" in agent_run.status:
                        # Si un agente falla, todo el pipeline falla
                        pipeline_successful = False
                        break 
                    else:
                        agent_run.logs = f"Agent completed successfully in {duration:.2f}s"
                        
                    # 4. Procesamiento de Resultados y Lógica de Corrección
                    
                    if agent_id == "mockup" and agent_run.status == "mockup_generated":
                        project.status = "UX_REVIEW_PENDING" 
                        pipeline_successful = True
                        break # Pausar el pipeline

                    elif agent_id == "data_design":
                        db_schema = agent_result.get("db_schema") 
                        if db_schema:
                            project.specification["database_schema"] = db_schema

                    elif agent_id == "builder":
                        current_requirements["generated_code"] = agent_result.get("generated_code")
                        project.zip_file_path = agent_result.get("zip_path")
                        project.generated_code = agent_result.get("generated_code")

                    elif agent_id == "tester":
                        report = agent_result.get("validation_report", {})
                        if report.get("critical_failures", 0) > 0:
                            logger.warning("Tester found critical functional issues. Requiring code correction.")
                            current_requirements["validation_report"] = report
                            needs_rebuild = True
                            break # Iniciar nuevo ciclo de corrección

                    elif agent_id == "security":
                        report = agent_result.get("security_report", {})
                        if report.get("critical_vulnerabilities", 0) > 0:
                            logger.warning("Security Agent found critical vulnerabilities. Requiring code correction.")
                            current_requirements["security_report"] = report
                            needs_rebuild = True
                            break # Iniciar nuevo ciclo de corrección
                    
                    # 5. Commit de AgentRun y cambios en Project
                    self.db.add(project)
                    self.db.add(agent_run)
                    self.db.commit()
                    
                    # 6. Actualizar requisitos para el siguiente agente
                    current_requirements.update(agent_result) 
                    
                except Exception as e:
                    logger.error(f"FATAL Error in {agent_id} agent: {e}")
                    pipeline_successful = False
                    
                    if 'agent_run' in locals():
                        agent_run.status = "failed"
                        agent_run.completed_at = datetime.utcnow()
                        agent_run.logs = f"Agent error: {str(e)}"
                        self.db.commit()
                    break # Salir del bucle for

            # --- Lógica para el Bucle While (Corrección) ---
            if needs_rebuild and correction_cycle < MAX_CORRECTION_CYCLES:
                correction_cycle += 1
                # Volver a Builder para el siguiente ciclo
                start_agent_index = next((i for i, (aid, *_) in enumerate(self.agent_sequence) if aid == "builder"), 0)
                project.status = f"CODE_CORRECTION_CYCLE_{correction_cycle}_IN_PROGRESS"
                self.db.add(project)
                self.db.commit()
                logger.info(f"Starting correction cycle {correction_cycle + 1}. Status: {project.status}")
                # Continúa el bucle while
            else:
                # Si no se necesita reconstrucción O si el pipeline falló críticamente O si está en pausa UX
                break # Salir del bucle while
        
        # 7. Actualizar estado final del proyecto (Solo si no está en pausa/corrección)
        if not needs_rebuild and project.status not in ["UX_REVIEW_PENDING"]:
            final_status = "COMPLETED" if pipeline_successful and correction_cycle < MAX_CORRECTION_CYCLES else "FAILED"
            project.status = final_status
            project.completed_at = datetime.utcnow()
            self.db.add(project)
            self.db.commit()
        
        return {
            "project_id": project_id,
            "pipeline_status": project.status,
            "agents_completed": "Check AgentRun table for full list"
        }

    def resume_pipeline(self, project_id: uuid.UUID) -> dict:
        """
        Reanuda la ejecución del pipeline después de una pausa por revisión de UX.
        Cambia el estado de UX_REVIEW_PENDING a MOCKUP_APPROVED.
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found for resumption.")
            return {"project_id": project_id, "status": "failed", "message": "Project not found."}

        if project.status == "UX_REVIEW_PENDING":
            project.status = "MOCKUP_APPROVED" # Nuevo estado para indicar la aprobación
            project.updated_at = datetime.utcnow()
            self.db.add(project)
            self.db.commit()
            logger.info(f"Project {project_id} UX review approved. Status changed to MOCKUP_APPROVED.")
            
            # En un sistema real, el sistema de colas reanudaría el run_pipeline
            return {
                "project_id": project_id,
                "status": "resumed",
                "message": "UX approved. Pipeline is ready to resume (starting with Builder Agent)."
            }
        else:
            logger.warning(f"Project {project_id} is not in UX_REVIEW_PENDING status. Current status: {project.status}")
            return {
                "project_id": project_id,
                "status": "no_change",
                "message": f"Pipeline not resumed. Current status: {project.status}"
            }
    
    def get_agent_status(self, project_id: uuid.UUID) -> dict:
        """Get current status of all agents for a project (Usado por el endpoint de polling)"""
        # Obtener el Job ID asociado al Project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.job_id:
             return {"project_id": project_id, "agent_runs": []}

        # Obtener todas las ejecuciones de agentes para ese Job
        agent_runs = self.db.query(AgentRun).filter(
            AgentRun.job_id == project.job_id
        ).order_by(AgentRun.started_at).all()
        
        # Recuperar el último Mockup HTML para mostrarlo si el proyecto está en pausa
        mockup_html = None
        current_project_status = project.status

        for run in agent_runs:
            if run.agent_name == "mockup" and run.status == "mockup_generated":
                # Asumimos que response_raw es el HTML para el mockup
                mockup_html = run.response_raw 

        return {
            "project_id": project_id,
            "project_status": current_project_status,
            "mockup_html": mockup_html, # Retornamos el HTML para el frontend
            "agent_runs": [
                {
                    "agent": run.agent_name,
                    "status": run.status,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "ended_at": run.completed_at.isoformat() if run.completed_at else None,
                    "duration": run.duration_seconds
                }
                for run in agent_runs
            ]
        }
        
    def create_and_start_project(self, raw_idea: str, analysis_plan: Dict[str, Any]) -> uuid.UUID:
        """
        Crea un nuevo proyecto en la DB, guarda el plan de DeepSeek como especificación inicial, 
        y encola/inicia la ejecución del pipeline (de forma síncrona).
        """
        
        # 1. Crear Job ID (Necesario antes que el Project)
        new_job_id = uuid.uuid4()
        new_job = Job(id=new_job_id, status="PENDING", created_at=datetime.utcnow())
        self.db.add(new_job)
        self.db.commit()
        
        # 2. Crear Project (ProjectID) y cargar la especificación inicial (Plan de DeepSeek)
        new_project_id = uuid.uuid4()
        
        # Usamos el plan de DeepSeek como la especificación inicial del proyecto
        new_project = Project(
            id=new_project_id,
            job_id=new_job_id,
            requirements=raw_idea,              # Guardamos la idea original
            status="ANALYSIS_COMPLETED",        # Nuevo estado que indica que el análisis AI finalizó
            specification=analysis_plan,        # ¡DeepSeek Plan guardado aquí!
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
            # Otros campos: name, user_id, etc., pueden necesitar ser poblados
        )
        self.db.add(new_project)
        self.db.commit()

        logger.info(f"Project {new_project_id} created with DeepSeek plan loaded.")

        # 3. Iniciar la Ejecución del Pipeline (Asumimos que esto ocurre en un worker)
        
        # self.run_pipeline(new_project_id) # Esta línea se llamaría si fuera un worker síncrono

        return new_project_id
