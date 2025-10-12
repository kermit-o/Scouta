# app/models.py
import enum, uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProjectStatus(str, enum.Enum):
    pending = "pending"
    planning = "planning"
    planned  = "planned"
    building = "building"
    built    = "built"
    error    = "error"

class Project(Base):
    __tablename__ = "projects"
    # __table_args__ = {"schema": "forge"}  # <- Úsalo solo si quieres mantener el esquema "forge"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)

    requirements     = Column(JSONB, nullable=True)
    plan_json        = Column(JSONB, nullable=True)
    generated_plan   = Column(JSONB, nullable=True)   # resumen legible
    technology_stack = Column(JSONB, nullable=True)
    result           = Column(JSONB, nullable=True)   # artifact_url, paths, logs, etc.
    status           = Column(String, nullable=False, default=ProjectStatus.pending.value)
    artifact_path    = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
