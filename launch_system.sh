#!/bin/bash

echo "🚀 FORGE SAAS - SISTEMA COMPLETO DE ARRANQUE"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio base
BASE_DIR="/workspaces/Scouta/forge_saas"
cd $BASE_DIR

# Función para verificar puertos
check_port() {
    netstat -tulpn 2>/dev/null | grep ":$1" > /dev/null
}

# Función para matar procesos en puerto
kill_port() {
    echo -e "${YELLOW}🛑 Deteniendo proceso en puerto $1...${NC}"
    lsof -ti:$1 | xargs kill -9 2>/dev/null
}

# Crear directorio de logs
mkdir -p logs

echo -e "${BLUE}📁 Configurando entorno...${NC}"

# Verificar PostgreSQL
if ! check_port 5432; then
    echo -e "${YELLOW}🐘 Iniciando PostgreSQL...${NC}"
    docker run -d --name postgres-forge \
        -e POSTGRES_DB=forge_saas \
        -e POSTGRES_USER=forge_user \
        -e POSTGRES_PASSWORD=forge_password \
        -p 5432:5432 \
        postgres:13 > /dev/null 2>&1
    sleep 5
fi

# Detener servicios previos
echo -e "${YELLOW}🧹 Limpiando servicios anteriores...${NC}"
kill_port 8000
kill_port 8001
kill_port 8005
kill_port 8010
kill_port 8501
kill_port 5173
kill_port 5174

sleep 2

# Iniciar Backend con logging
echo -e "${GREEN}🔧 Iniciando Backend FastAPI...${NC}"
python -c "
import uvicorn
from backend_final import app
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)

print('🚀 Backend iniciando en puerto 8010...')
uvicorn.run(app, host='0.0.0.0', port=8010, log_level='info')
" > logs/backend_output.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > logs/backend.pid

# Esperar que backend esté listo
echo -e "${YELLOW}⏳ Esperando backend...${NC}"
sleep 8

# Verificar backend
if curl -s http://localhost:8010/api/v1/payments/health > /dev/null; then
    echo -e "${GREEN}✅ Backend funcionando en http://localhost:8010${NC}"
else
    echo -e "${RED}❌ Backend no responde${NC}"
    tail -20 logs/backend_output.log
    exit 1
fi

# Iniciar Frontend Streamlit
echo -e "${GREEN}🎨 Iniciando Frontend Streamlit...${NC}"
cd ui
streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --logger.level info \
    > ../logs/frontend_output.log 2>&1 &

FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

sleep 5

# Iniciar Monitor de Sistema
echo -e "${GREEN}👁️  Iniciando Sistema de Monitorización...${NC}"
python monitoring_system.py > logs/monitoring.log 2>&1 &

MONITOR_PID=$!
echo $MONITOR_PID > logs/monitor.pid

# Mostrar estado final
echo ""
echo -e "${GREEN}🎉 SISTEMA COMPLETAMENTE OPERATIVO${NC}"
echo "=========================================="
echo -e "${BLUE}🔧 Backend API:${NC}    http://localhost:8010"
echo -e "${BLUE}🎨 Frontend:${NC}       http://localhost:8501"
echo -e "${BLUE}🐘 PostgreSQL:${NC}     localhost:5432"
echo -e "${BLUE}📊 Logs:${NC}           ./logs/"
echo ""
echo -e "${YELLOW}📋 Comandos útiles:${NC}"
echo "  tail -f logs/backend_output.log    # Ver logs backend"
echo "  tail -f logs/frontend_output.log   # Ver logs frontend"
echo "  tail -f logs/monitoring.log        # Ver monitorización"
echo ""
echo -e "${RED}🛑 Para detener: ./stop_system.sh${NC}"

# Mantener script corriendo
wait
