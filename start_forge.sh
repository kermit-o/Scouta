#!/bin/bash

echo "🚀 Iniciando Forge SaaS..."
echo "=========================="

# Limpiar puertos
echo "🔄 Limpiando puertos..."
sudo fuser -k 8001/tcp 2>/dev/null || true
sudo fuser -k 3000/tcp 2>/dev/null || true
sleep 2

echo ""
echo "1. Iniciando Backend API..."
cd /workspaces/Scouta/forge_saas
python main.py &
BACKEND_PID=$!
sleep 5

if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend: http://localhost:8001"
else
    echo "❌ Error iniciando backend"
    exit 1
fi

echo ""
echo "2. Iniciando Interfaz Web..."
cd /workspaces/Scouta/forge_saas/forge_ui

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
sleep 8

echo "✅ Frontend: http://localhost:3000"

echo ""
echo "🎉 Forge SaaS está listo!"
echo "========================"
echo "🌐 Interfaz: http://localhost:3000"
echo "🔗 API:      http://localhost:8001"
echo ""
echo "Presiona Ctrl+C para detener"

wait
