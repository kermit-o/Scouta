#!/bin/bash

echo "🚀 INICIANDO SISTEMA COMPLETO FORGE SAAS"
echo "=========================================="

# Verificar que la UI esté construida
if [ ! -d "forge_ui/dist" ]; then
    echo "📦 Construyendo la UI..."
    cd forge_ui
    npm run build
    cd ..
fi

# Iniciar el backend
echo "🔧 Iniciando Backend (Puerto 8000)..."
python main.py &
BACKEND_PID=$!

# Pequeña pausa para que el backend inicie
sleep 3

# Verificar que el backend esté corriendo
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend funcionando en http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    
    # Si la UI está construida, servirla
    if [ -d "forge_ui/dist" ]; then
        echo "🎨 UI disponible en: http://localhost:8000"
        echo ""
        echo "🎯 SISTEMA LISTO!"
        echo "   - Backend: http://localhost:8000"
        echo "   - API: http://localhost:8000/api"
        echo "   - Docs: http://localhost:8000/docs"
        echo ""
        echo "Para desarrollo UI, en otra terminal ejecuta:"
        echo "  cd forge_ui && npm run dev"
        echo ""
    else
        echo "⚠️  UI no construida. Para desarrollo:"
        echo "  cd forge_ui && npm run dev"
    fi
    
    # Mantener el script corriendo
    echo "Presiona Ctrl+C para detener el sistema"
    wait $BACKEND_PID
else
    echo "❌ Error iniciando el backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
