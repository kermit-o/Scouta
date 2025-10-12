#!/bin/bash

echo "🛑 DETENIENDO SISTEMA FORGE SAAS"
echo "================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Detener por PIDs guardados
for service in backend frontend monitor; do
    if [ -f "logs/${service}.pid" ]; then
        pid=$(cat "logs/${service}.pid")
        if kill -0 $pid 2>/dev/null; then
            echo -e "${RED}🛑 Deteniendo $service (PID: $pid)...${NC}"
            kill -9 $pid
            rm "logs/${service}.pid"
        fi
    fi
done

# Detener por puertos conocidos
for port in 8010 8501; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${RED}🛑 Deteniendo proceso en puerto $port...${NC}"
        kill -9 $pid
    fi
done

# Detener PostgreSQL
docker stop postgres-forge 2>/dev/null && echo -e "${GREEN}✅ PostgreSQL detenido${NC}"

echo -e "${GREEN}🎯 Sistema completamente detenido${NC}"
