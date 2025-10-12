#!/bin/bash

# stop_all_services.sh - Detiene todos los servicios

echo "🛑 DETENIENDO TODOS LOS SERVICIOS"
echo "================================"

# Detener procesos por PID
for service in backend frontend worker; do
    PID_FILE="/tmp/forge_${service}.pid"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "🔫 Deteniendo $service (PID: $PID)"
            kill $PID
            rm "$PID_FILE"
        fi
    fi
done

# Detener contenedores Docker
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "🐳 Deteniendo contenedores Docker..."
    docker-compose down
fi

# Matar procesos por puerto
for port in 8000 3000; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "🔓 Liberando puerto $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null
    fi
done

echo "✅ Todos los servicios detenidos"