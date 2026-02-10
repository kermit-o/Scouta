#!/bin/bash

echo "🔧 Reparación rápida Diet AI"
echo "============================="

echo "1. Corrigiendo main.py..."
cd api
# Ya creamos el main.py corregido arriba

echo "2. Actualizando docker-compose.yml..."
cd ..
cat > docker-compose.yml << 'COMPOSE'
services:
  postgres:
    image: postgres:15-alpine
    container_name: dieta-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: dietai
      POSTGRES_PASSWORD: dietai123
      POSTGRES_DB: dietai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dietai"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: dieta-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: ./api
    container_name: dieta-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://dietai:dietai123@postgres:5432/dietai
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: your-super-secret-jwt-key-change-this-in-production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./api:/app

volumes:
  postgres_data:
COMPOSE

echo "3. Reconstruyendo API..."
docker-compose build api --no-cache

echo "4. Reiniciando API..."
docker-compose up -d api

echo "5. Esperando 15 segundos..."
sleep 15

echo "6. Verificando..."
if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ ¡API funcionando correctamente!"
    echo ""
    echo "🎉 Endpoints disponibles:"
    echo "   http://localhost:8000/"
    echo "   http://localhost:8000/docs"
    echo "   http://localhost:8000/health"
    echo ""
    echo "📋 Prueba rápida:"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "⚠️  Revisando logs..."
    docker-compose logs api --tail=30
fi
