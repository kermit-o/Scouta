from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.db import Base

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    artifact_type = Column(String, default="generated")
    kind = Column(String(30), nullable=False)
    path = Column(String(512), nullable=False)
    size = Column(Integer, default=0)
    sha256 = Column(String(64), default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    project = relationship("Project", backref="artifacts")

    def __repr__(self):
        return f"<Artifact {self.id} for project {self.project_id}>"
