"""
Conexión a base de datos PostgreSQL para DietAI
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Obtener URL de base de datos desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://dietai_user:dietai_pass@postgres:5432/dietai"
)

logger.info(f"Conectando a base de datos: {DATABASE_URL.split('@')[-1]}")

# Crear engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    echo=False  # Cambiar a True para debug SQL
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

@contextmanager
def get_db():
    """Context manager para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error en transacción de base de datos: {e}")
        raise
    finally:
        db.close()

def init_db():
    """Inicializar base de datos (crear tablas)"""
    from . import models  # Importar modelos aquí para evitar import circular
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Base de datos inicializada")
