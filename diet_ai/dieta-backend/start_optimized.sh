#!/bin/bash

set -e  # Detener en primer error

echo "🚀 Diet AI - Inicio Optimizado con Docker"
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    if [ "$1" = "success" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "error" ]; then
        echo -e "${RED}❌ $2${NC}"
    elif [ "$1" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    else
        echo -e "$2"
    fi
}

# 1. Verificar Docker
print_status "info" "1. Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_status "error" "Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_status "error" "Docker daemon no está corriendo"
    exit 1
fi
print_status "success" "Docker funcionando"

# 2. Verificar docker-compose.yml
print_status "info" "2. Verificando docker-compose.yml..."
if [ ! -f docker-compose.yml ]; then
    print_status "error" "docker-compose.yml no encontrado"
    exit 1
fi

# 3. Limpiar previo (solo si se solicita)
if [ "$1" = "--clean" ]; then
    print_status "warning" "Limpiando containers previos..."
    docker-compose down -v 2>/dev/null || true
fi

# 4. Construir servicios
print_status "info" "3. Construyendo servicios (esto puede tomar unos minutos)..."
docker-compose build --no-cache

# 5. Iniciar servicios
print_status "info" "4. Iniciando servicios..."
docker-compose up -d

# 6. Esperar inicialización
print_status "info" "5. Esperando inicialización de servicios..."
sleep 20

# 7. Verificar estado
print_status "info" "6. Verificando estado de servicios..."

# PostgreSQL
if docker-compose exec -T postgres pg_isready -U dietai &> /dev/null; then
    print_status "success" "  PostgreSQL: ✅ CONECTADO"
else
    print_status "error" "  PostgreSQL: ❌ ERROR"
    docker-compose logs postgres --tail=10
fi

# Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    print_status "success" "  Redis: ✅ CONECTADO"
else
    print_status "error" "  Redis: ❌ ERROR"
fi

# API
print_status "info" "7. Verificando API..."
MAX_RETRIES=10
RETRY_COUNT=0
API_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f http://localhost:8000/health &> /dev/null; then
        API_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Intento $RETRY_COUNT/$MAX_RETRIES..."
    sleep 5
done

if [ "$API_READY" = true ]; then
    print_status "success" "  API: ✅ FUNCIONANDO"
    
    # Mostrar información de la API
    echo ""
    print_status "success" "🎉 ¡TODO LISTO! 🎉"
    echo ""
    echo "🌐 API disponible en:"
    echo "   - http://localhost:8000"
    echo "   - http://localhost:8000/docs (documentación Swagger)"
    echo "   - http://localhost:8000/health (health check)"
    echo ""
    echo "🗄️  Servicios:"
    echo "   - PostgreSQL: localhost:5432 (user: dietai, pass: dietai123)"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "🛠️  Comandos útiles:"
    echo "   Ver logs API:    docker-compose logs -f api"
    echo "   Ver todos logs:  docker-compose logs -f"
    echo "   Detener:         docker-compose down"
    echo "   Reiniciar:       docker-compose restart"
    
    # Prueba rápida
    echo ""
    print_status "info" "📋 Prueba rápida:"
    curl -s http://localhost:8000/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/
else
    print_status "error" "  API: ❌ NO RESPONDE"
    echo ""
    print_status "warning" "🔍 Últimos logs de la API:"
    docker-compose logs api --tail=30
    echo ""
    print_status "warning" "Intenta ver los logs con: docker-compose logs -f api"
fi
