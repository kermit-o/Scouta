from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.db import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    agent = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # ok/failed/running
    logs = Column(Text)
    details_json = Column(Text)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True))
    project = relationship("Project", backref="agent_runs")
