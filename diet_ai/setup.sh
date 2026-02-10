#!/usr/bin/env bash
# ============================================
# SETUP RÁPIDO SIN INTERACCIÓN
# ============================================

set -e

echo "🚀 Creando Dieta Backend en Codespaces..."

# Nombre fijo (sin prompt)
PROJECT_NAME="dieta-backend"

echo "Proyecto: $PROJECT_NAME"
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 1. Archivos básicos
echo "📁 Creando archivos base..."

cat > .env.example << 'ENVEOF'
# Database
DATABASE_URL=postgresql://admin:admin123@localhost:5432/dieta
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=sk-your-openai-key
DEEPSEEK_API_KEY=sk-your-deepseek-key

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ENVEOF

cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dieta
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://admin:admin123@postgres:5432/dieta
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY:-sk-default}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-sk-default}

volumes:
  postgres_data:
DOCKEREOF

# 2. Crear API
mkdir -p api
cd api

cat > requirements.txt << 'REQEOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
python-dotenv==1.0.0
REQEOF

cat > Dockerfile << 'DOCKFILEEOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKFILEEOF

cat > main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dieta API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Dieta API running in Codespaces", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "dieta-api"}

@app.get("/test")
async def test():
    return {"test": "OK", "environment": "codespaces"}
MAINEOF

cd ..

# 3. Crear scripts útiles
cat > start.sh << 'STARTEOF'
#!/bin/bash
echo "🚀 Starting Dieta Backend..."
docker-compose up -d
echo "✅ Services started!"
echo "🌐 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🩺 Health: http://localhost:8000/health"
STARTEOF

chmod +x start.sh

cat > stop.sh << 'STOPEOF'
#!/bin/bash
echo "🛑 Stopping services..."
docker-compose down
echo "✅ Services stopped"
STOPEOF

chmod +x stop.sh

# 4. README
cat > README.md << 'READMEEOF'
# Dieta Backend - Codespaces

## Quick Start
\`\`\`bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your API keys

# 2. Start services
./start.sh

# 3. Test API
curl http://localhost:8000/health
\`\`\`

## Services
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Commands
- \`./start.sh\` - Start all services
- \`./stop.sh\` - Stop all services
- \`docker-compose logs -f\` - View logs
READMEEOF

echo "✅ Setup completo!"
echo ""
echo "📝 Pasos siguientes:"
echo "1. cd $PROJECT_NAME"
echo "2. cp .env.example .env"
echo "3. ./start.sh"
echo "4. Open: http://localhost:8000/docs"
