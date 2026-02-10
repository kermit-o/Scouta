"""Job model - Finalized for concurrent Worker Loop."""
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from backend.app.core.db import Base

class JobState:
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    # Opcional, pero útil: CANCELED = "canceled" 

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True} 
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False) # Usar UUID si projects.id es UUID
    agent = Column(String(50), nullable=False)
    
    # --- Campos de Estado y Métricas ---
    state = Column(String(20), nullable=False, default=JobState.QUEUED)
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text)
    
    # Nuevo: Para medir el tiempo de ejecución exacto de la IA
    started_at = Column(DateTime(timezone=True), nullable=True) # Se llena cuando state pasa a RUNNING
    ended_at = Column(DateTime(timezone=True), nullable=True)   # Se llena cuando state pasa a DONE/FAILED

    # Nuevo: Para Jobs complejos como el Supervisor
    requirements_text = Column(Text, nullable=True)

    # Campos de Timestamps de Sistema
    run_after = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))