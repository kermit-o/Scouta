# backend/app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. Obtener la URL de la base de datos desde la variable de entorno
# La URL por defecto es para el entorno de Docker/Postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://forge:forge@localhost:5432/forge"
) 

# Si estamos en el entorno del contenedor, 'postgres' se resolverá a la IP del servicio.
# Si estamos en la máquina local (ejecutando worker en la máquina host), usamos 'localhost'.

# 2. Configuración del Engine
# echo=True es útil para debugging de SQL, pero lo quitamos en producción
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

# 3. Configuración de SessionLocal
# SessionLocal es nuestra fábrica de sesiones. 
# bind=engine la asocia a nuestra conexión.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 4. Base Declarativa
# Todos nuestros modelos de SQLAlchemy (ORM) heredarán de esta clase.
Base = declarative_base()


# 5. Función de utilidad para obtener la sesión de DB (usada por las rutas/servicios)
# Usamos un generador para que FastAPI la use como dependencia (Dependency Injection)
def get_db():
    """Obtiene una sesión de base de datos y la cierra al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# backend/app/db/session.py (Fragmento con la corrección)

# ... (Definiciones de engine, SessionLocal, Base) ...


def init_db():
    """Initialize the database with all models."""
    # Import models here to ensure they are registered with SQLAlchemy
    # CORRECCIÓN: Quitamos el prefijo 'backend.'
    from app.models.agent_run import AgentRun
    from app.models.artifact import Artifact
    # Add other models as needed
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

# ... (resto de la función init_db_simple)


# Alternative simple version if models cause issues
def init_db_simple():
    """Simple database initialization."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
