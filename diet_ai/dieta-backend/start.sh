#!/bin/bash

echo "🚀 Iniciando Diet AI Backend..."

# Detener y eliminar containers existentes
echo "🛑 Limpiando containers anteriores..."
docker-compose down 2>/dev/null || true

# Construir y levantar servicios
echo "🔨 Construyendo servicios..."
docker-compose up -d --build

# Esperar a que los servicios estén listos
echo "⏳ Esperando inicialización de servicios..."
sleep 15

# Verificar estado
echo "📊 Estado de los servicios:"
docker-compose ps

# Verificar PostgreSQL
echo "🗄️  Verificando PostgreSQL..."
docker exec dieta-postgres psql -U dietai -d dietai -c "\dt" 2>/dev/null || echo "PostgreSQL no listo aún..."

# Verificar Redis
echo "🔴 Verificando Redis..."
docker exec dieta-redis redis-cli ping 2>/dev/null && echo "✅ Redis funcionando" || echo "❌ Redis no responde"

# Verificar API
echo "🌐 Verificando API..."
sleep 5
if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API saludable"
else
    echo "⚠️  API no responde - revisando logs..."
    docker-compose logs api --tail=20
fi

echo ""
echo "🎯 URLs importantes:"
echo "   API:              http://localhost:8000"
echo "   API Docs:         http://localhost:8000/docs"
echo "   PostgreSQL:       localhost:5432"
echo "   Redis:            localhost:6379"
echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs:         docker-compose logs -f"
echo "   Ver API:          curl http://localhost:8000/health"
echo "   Conectar a DB:    psql -h localhost -U dietai -d dietai"
echo "   Detener todo:     docker-compose down"
