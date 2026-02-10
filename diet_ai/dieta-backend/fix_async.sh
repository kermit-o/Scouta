#!/bin/bash

echo "🔧 Reparando problema async/psycopg2..."
echo "======================================="

cd api

echo "1. Actualizando requirements.txt para usar asyncpg..."
cat > requirements.txt << 'REQ'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
python-dotenv==1.0.0
REQ

echo "2. Corrigiendo config.py..."
cat > config.py << 'CONFIG'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://dietai:dietai123@postgres:5432/dietai"
    SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Diet AI API"
    VERSION: str = "2.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
CONFIG

echo "3. Verificando database.py..."
if [ -f database.py ]; then
    echo "✅ database.py existe"
    # Reemplazar psycopg2 por asyncpg en la URL si es necesario
    sed -i 's/postgresql:\/\//postgresql+asyncpg:\/\//g' database.py
    sed -i 's/psycopg2/asyncpg/g' database.py
else
    echo "📝 Creando database.py básico..."
    cat > database.py << 'DB'
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
DB
fi

cd ..

echo "4. Reconstruyendo API..."
docker-compose build api --no-cache

echo "5. Reiniciando..."
docker-compose up -d api

echo "6. Esperando 15 segundos..."
sleep 15

echo "7. Verificando..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ ¡API funcionando correctamente!"
    echo "🌐 URL: http://localhost:8000"
    echo "📚 Docs: http://localhost:8000/docs"
else
    echo "⚠️  Revisando logs..."
    docker-compose logs api --tail=20
fi
