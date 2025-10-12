#!/bin/bash

# start_all_services.sh - Inicia todos los servicios del proyecto

echo "🏃‍♂️ INICIANDO TODOS LOS SERVICIOS"
echo "==============================="

# Configurar entorno
export PYTHONPATH="/workspaces/Scouta/forge_saas/backend:$PYTHONPATH"

# Función para verificar puerto
check_port() {
    netstat -tulpn 2>/dev/null | grep ":$1 " > /dev/null
}

# 1. Liberar puertos si están ocupados
echo "1. 🔓 LIBERANDO PUERTOS..."
for port in 8000 3000 5432 6379; do
    if check_port $port; then
        echo "   🔫 Matando proceso en puerto $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 2
    fi
done

# 2. Iniciar base de datos (si hay Docker)
echo -e "\n2. 🗄️ INICIANDO BASE DE DATOS..."
if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "   🐳 Iniciando contenedores de base de datos..."
    docker-compose up -d db redis 2>/dev/null || echo "   ⚠️  No se pudieron iniciar contenedores"
else
    echo "   ℹ️  Docker no disponible - usando base de datos local"
fi

# 3. Inicializar base de datos
echo -e "\n3. 🔧 INICIALIZANDO BD..."
cd ./backend
python -c "
from app.db import init_db
try:
    init_db()
    print('   ✅ Base de datos inicializada')
except Exception as e:
    print(f'   ⚠️  Error inicializando BD: {e}')
"
cd ..

# 4. Iniciar backend
echo -e "\n4. 🤖 INICIANDO BACKEND (FASTAPI)..."
cd ./backend
echo "   🌐 Backend en: http://localhost:8000"
echo "   📚 Docs en: http://localhost:8000/docs"
echo "   ⏹️  Presiona Ctrl+C para detener"

# Iniciar en background y guardar PID
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/forge_backend.pid
cd ..

# 5. Iniciar frontend (si existe)
echo -e "\n5. 🎨 INICIANDO FRONTEND..."
if [ -d "./ui" ] && [ -f "./ui/package.json" ]; then
    cd ./ui
    echo "   📦 Instalando dependencias frontend..."
    npm install 2>/dev/null || echo "   ⚠️  Error instalando dependencias"
    
    echo "   🌐 Frontend en: http://localhost:3000"
    echo "   🚀 Iniciando servidor de desarrollo..."
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/forge_frontend.pid
    cd ..
else
    echo "   ℹ️  No se encontró frontend para iniciar"
fi

# 6. Iniciar workers (si existen)
echo -e "\n6. 🔄 INICIANDO WORKERS..."
if [ -f "./backend/app/worker.py" ]; then
    cd ./backend
    echo "   🎯 Iniciando worker de Celery..."
    celery -A app.worker worker --loglevel=info &
    WORKER_PID=$!
    echo $WORKER_PID > /tmp/forge_worker.pid
    cd ..
else
    echo "   ℹ️  No se encontró worker para iniciar"
fi

# 7. Mostrar estado final
echo -e "\n🎉 TODOS LOS SERVICIOS INICIADOS"
echo "================================="
sleep 3

echo -e "\n📊 ESTADO ACTUAL:"
echo "   ✅ Backend FastAPI: http://localhost:8000"
echo "   ✅ Documentación API: http://localhost:8000/docs" 
echo "   ✅ Frontend: http://localhost:3000 (si aplica)"
echo "   ✅ Workers: En ejecución (si aplica)"

echo -e "\n🔍 PARA VER LOGS:"
echo "   Backend: tail -f /workspaces/Scouta/forge_saas/backend/logs/app.log"
echo "   Workers: tail -f /workspaces/Scouta/forge_saas/backend/logs/worker.log"

echo -e "\n⏹️ PARA DETENER TODOS LOS SERVICIOS:"
echo "   ./stop_all_services.sh"