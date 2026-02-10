# backend/app/models/__init__.py (CORREGIDO)

# Importamos la Base declarativa que define el ORM.
# Es crucial que Alembic la encuentre.
from backend.app.db.session import Base # <-- NUEVA LÍNEA CLAVE

# Importamos todos los modelos para que estén registrados en Base.metadata
from .project import Project
from .job import Job
from .agent_run import AgentRun
from .artifact import Artifact
from backend.app.db.session import Base 

# Re-exportar Base y los modelos (CRÍTICO para que Alembic funcione)
# Sus modelos Project, Job, etc. deben estar importados aquí también:
from .project import Project 

# Hacemos que la Base y todos los modelos estén accesibles cuando se importa el módulo 'app.models'
__all__ = ["Base", "Project", "Job", "AgentRun", "Artifact"]

