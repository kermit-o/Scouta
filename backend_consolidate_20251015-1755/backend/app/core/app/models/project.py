"""Project model - Fixed version"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from backend.app.core.db import Base
from sqlalchemy.dialects.postgresql import JSON



# REEMPLAZAR el modelo actual por:
class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True} 
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    
    # ESPECIFICACIÓN TÉCNICA (no solo texto)
    specification = Column(JSON)  # {entities, features, stack, etc.}
    
    # CÓDIGO GENERADO (no solo metadatos)
    generated_code = Column(JSON)  # {frontend: {...}, backend: {...}}
    
    # ESTADO REAL del proyecto
    status = Column(String)  # "analyzing", "generating", "ready", "deployed"
    deployment_url = Column(String)  # URL donde está desplegado
    last_error = Column(Text)