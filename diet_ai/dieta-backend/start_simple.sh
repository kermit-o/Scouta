#!/bin/bash

echo "🚀 Diet AI - Inicio Simplificado"
echo "================================"

# 1. Verificar docker-compose.yml
echo "📋 Verificando docker-compose.yml..."
if [ ! -f docker-compose.yml ]; then
    echo "❌ Error: No existe docker-compose.yml"
    exit 1
fi

# Verificar sintaxis básica
if ! grep -q "services:" docker-compose.yml; then
    echo "❌ Error: docker-compose.yml no tiene sección 'services'"
    exit 1
fi

# 2. Limpiar containers anteriores
echo "🧹 Limpiando containers anteriores..."
docker-compose down 2>/dev/null || true

# 3. Construir e iniciar
echo "🔨 Construyendo e iniciando servicios..."
docker-compose up -d --build

# 4. Esperar
echo "⏳ Esperando 20 segundos para inicialización..."
sleep 20

# 5. Mostrar estado
echo ""
echo "📊 ESTADO DE LOS SERVICIOS:"
echo "============================"
docker-compose ps

echo ""
echo "🔍 VERIFICANDO SERVICIOS:"
echo "=========================="

# Verificar PostgreSQL
echo -n "🗄️  PostgreSQL: "
if docker exec dieta-postgres pg_isready -U dietai >/dev/null 2>&1; then
    echo "✅ CONECTADO"
else
    echo "❌ NO CONECTADO"
    echo "   Logs PostgreSQL:"
    docker-compose logs postgres --tail=5
fi

# Verificar Redis
echo -n "🔴 Redis: "
if docker exec dieta-redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ CONECTADO"
else
    echo "❌ NO CONECTADO"
fi

# Verificar API
echo -n "🌐 API: "
if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ FUNCIONANDO"
    echo "   Health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ NO RESPONDE"
    echo "   Últimos logs API:"
    docker-compose logs api --tail=10
fi

echo ""
echo "🎯 URLs IMPORTANTES:"
echo "===================="
echo "   API:              http://localhost:8000"
echo "   Documentación:    http://localhost:8000/docs"
echo "   PostgreSQL:       localhost:5432 (user: dietai, pass: dietai123)"
echo "   Redis:            localhost:6379"

echo ""
echo "🛠️  COMANDOS ÚTILES:"
echo "===================="
echo "   Ver logs API:     docker-compose logs -f api"
echo "   Ver todos logs:   docker-compose logs -f"
echo "   Conectar a DB:    psql -h localhost -U dietai -d dietai"
echo "   Detener todo:     docker-compose down"
