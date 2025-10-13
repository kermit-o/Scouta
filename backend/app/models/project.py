from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Text, String, DateTime, Boolean, JSON, text

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, server_default=text("(uuid_generate_v4())::text"))
    user_id = Column(Text, nullable=True)
    project_name = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    status = Column(Text, nullable=False, server_default=text("'pending'::text"))

    # Compatibles con columnas jsonb en Postgres
    plan_json = Column(JSON, nullable=True)
    generated_plan = Column(JSON, nullable=True)
    technology_stack = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
