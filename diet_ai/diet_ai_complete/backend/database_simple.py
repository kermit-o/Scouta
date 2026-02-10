"""
Conexión simplificada a PostgreSQL para DietAI
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Configuración directa (sin variables de entorno complicadas)
DATABASE_URL = "postgresql://dietai_user:dietai_pass@postgres:5432/dietai"
logger.info(f"Conectando a: {DATABASE_URL}")

try:
    # Crear engine
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Crear SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("✅ Engine de base de datos creado")
    
    # Probar conexión inmediatamente
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        logger.info(f"✅ Conectado a: {version.split(',')[0]}")
        
except Exception as e:
    logger.error(f"❌ Error creando engine: {e}")
    engine = None
    SessionLocal = None

def get_db():
    """Obtener sesión de base de datos"""
    if SessionLocal is None:
        logger.error("SessionLocal no inicializado")
        return None
        
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Error obteniendo sesión: {e}")
        return None

def test_connection():
    """Probar conexión a la base de datos"""
    if engine is None:
        return False, "Engine no inicializado"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            return True, f"PostgreSQL {version.split(',')[0]}"
    except Exception as e:
        return False, str(e)

def execute_query(query, params=None):
    """Ejecutar consulta SQL"""
    if engine is None:
        return None
        
    try:
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            if result.returns_rows:
                return result.fetchall()
            else:
                return result.rowcount
    except Exception as e:
        logger.error(f"Error ejecutando query: {e}")
        return None

def get_db():
    """Obtener sesión de base de datos para dependencias FastAPI"""
    if SessionLocal is None:
        raise Exception("SessionLocal no inicializado")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
