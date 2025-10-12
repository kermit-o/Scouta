#!/bin/bash
echo "🚀 INICIANDO SCOUTA/FORGE SAAS - MODO PRODUCCIÓN"
echo "================================================"

# Parar contenedores existentes
docker compose down 2>/dev/null
docker stop backend-simple worker-simple 2>/dev/null

# Iniciar sistema completo
docker compose up -d

echo ""
echo "⏳ Esperando que los servicios estén listos..."
sleep 15

echo ""
echo "✅ SERVICIOS:"
docker compose ps

echo ""
echo "🌐 URLs:"
echo "  - API Backend: http://localhost:8000"
echo "  - UI Streamlit: http://localhost:8501" 
echo "  - Database: localhost:5432"
echo ""
echo "📊 Comandos útiles:"
echo "  - Ver logs: docker compose logs -f"
echo "  - Monitoreo: ./system_status.sh"
echo "  - Detener: docker compose down"
echo ""
echo "🎯 El sistema está listo para generar proyectos!"
