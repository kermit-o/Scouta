#!/bin/bash

# Forge SaaS - Script de Arranque Completo
set -e

echo "🚀 Iniciando Forge SaaS..."
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ Error: $1 no está instalado${NC}"
        exit 1
    fi
}

# Verificar dependencias
echo -e "${BLUE}�� Verificando dependencias...${NC}"
check_command docker
check_command docker-compose

# Parar servicios si estaban corriendo
echo -e "${BLUE}🛑 Deteniendo servicios previos...${NC}"
docker compose down 2>/dev/null || true

# Limpiar recursos no utilizados
echo -e "${BLUE}🧹 Limpiando recursos Docker...${NC}"
docker system prune -f

# Construir y levantar servicios
echo -e "${BLUE}🔨 Construyendo servicios...${NC}"
docker compose build --no-cache

echo -e "${BLUE}⚡ Iniciando servicios...${NC}"
docker compose up -d

# Esperar a que los servicios estén listos
echo -e "${BLUE}⏳ Esperando inicialización de servicios...${NC}"
sleep 15

# Verificar estado de los servicios
echo -e "${BLUE}🔍 Verificando estado de servicios...${NC}"
docker compose ps

# Esperar específicamente a PostgreSQL
echo -e "${BLUE}🐘 Esperando a PostgreSQL...${NC}"
until docker compose exec postgres pg_isready -U forge -d forge > /dev/null 2>&1; do
    echo "Esperando a PostgreSQL..."
    sleep 5
done

# Verificar endpoints del backend
echo -e "${BLUE}🔌 Probando endpoints del backend...${NC}"
until curl -s http://localhost:8000/ > /dev/null; do
    echo "Esperando al backend..."
    sleep 5
done

# Test final
echo -e "${BLUE}🧪 Ejecutando tests finales...${NC}"
echo "------------------------------------------"

# Probar endpoints principales
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Backend saludable${NC}"
else
    echo -e "${RED}❌ Backend no responde${NC}"
fi

if curl -s http://localhost:8000/api/projects/ > /dev/null; then
    echo -e "${GREEN}✅ Endpoints de proyectos funcionando${NC}"
else
    echo -e "${RED}❌ Endpoints de proyectos no disponibles${NC}"
fi

if curl -s http://localhost:8501 > /dev/null; then
    echo -e "${GREEN}✅ UI accesible${NC}"
else
    echo -e "${RED}❌ UI no accesible${NC}"
fi

# Mostrar URLs
echo -e "\n${GREEN}🎉 Forge SaaS iniciado correctamente!${NC}"
echo "=========================================="
echo -e "${BLUE}📊 UI:${NC} http://localhost:8501"
echo -e "${BLUE}🔧 API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}�� PostgreSQL:${NC} localhost:5432"
echo "=========================================="
echo -e "${BLUE}📝 Logs en tiempo real:${NC} ./logs.sh"
echo -e "${BLUE}🛑 Detener servicios:${NC} ./stop.sh"
echo -e "${BLUE}🔁 Reiniciar:${NC} ./restart.sh"
