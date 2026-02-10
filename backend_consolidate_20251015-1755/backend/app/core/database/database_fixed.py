"""
Configuración de base de datos corregida
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Usar SQLite para desarrollo
SQLITE_PATH = "/tmp/forge_saas_main.db"
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

# Importar modelos y configurar relaciones
from .models import Base

# Importar y configurar relaciones
try:
    from .relationships import setup_relationships
    setup_relationships()
    print("✅ Relaciones configuradas en database.py")
except Exception as e:
    print(f"⚠️  Error configurando relaciones: {e}")

# Crear tablas
Base.metadata.create_all(engine)
print("✅ Base de datos principal configurada")
