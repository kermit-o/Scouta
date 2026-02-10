"""
Configuración de base de datos
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from .config import settings

# Crear engine asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    poolclass=NullPool
)

# Crear sesión asíncrona
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Dependencia para obtener sesión de BD
async def get_db():
    """Obtener sesión de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
