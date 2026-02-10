"""
Configuración de base de datos para suscripciones
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite para desarrollo
SQLITE_PATH = "/tmp/forge_saas_subscriptions.db"
DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
