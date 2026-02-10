#!/bin/bash
# Forge SaaS - Comandos de producción
# Uso: ./forge_saas_commands.sh [comando]

SERVER_URL="http://localhost:8001"

case "$1" in
    "start")
        echo "🚀 Iniciando Forge SaaS..."
        nohup python persistent_server_fixed.py > server.log 2>&1 &
        echo $! > server.pid
        echo "Servidor iniciado en $SERVER_URL"
        echo "Logs: server.log"
        ;;
    "stop")
        echo "🛑 Deteniendo Forge SaaS..."
        if [ -f server.pid ]; then
            kill $(cat server.pid) 2>/dev/null
            rm server.pid
        fi
        pkill -f "python.*persistent_server" 2>/dev/null
        echo "Servidor detenido"
        ;;
    "restart")
        echo "🔄 Reiniciando Forge SaaS..."
        ./forge_saas_commands.sh stop
        sleep 2
        ./forge_saas_commands.sh start
        ;;
    "status")
        echo "🔍 Estado del sistema:"
        response=$(curl -s -w "%{http_code}" "$SERVER_URL/api/health" 2>/dev/null)
        status_code=${response: -3}
        body=${response%???}
        
        if [ "$status_code" = "200" ]; then
            echo "$body" | python3 -m json.tool
        else
            echo "❌ Servidor no responde (código: $status_code)"
        fi
        ;;
    "projects")
        echo "📂 Listando proyectos:"
        response=$(curl -s -w "%{http_code}" "$SERVER_URL/api/projects" 2>/dev/null)
        status_code=${response: -3}
        body=${response%???}
        
        if [ "$status_code" = "200" ]; then
            echo "$body" | python3 -c "
import sys, json
try:
    projects = json.load(sys.stdin)
    print(f'Total: {len(projects)} proyectos')
    for i, p in enumerate(projects):
        print(f'{i+1}. {p[\"project_name\"]} ({p[\"status\"]}) - {p[\"id\"]}')
except Exception as e:
    print('Error:', e)
"
        else
            echo "❌ Error obteniendo proyectos (código: $status_code)"
        fi
        ;;
    "create")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Uso: ./forge_saas_commands.sh create \"Nombre del Proyecto\" \"Requisitos\""
            exit 1
        fi
        echo "📝 Creando proyecto: $2"
        PROJECT_DATA=$(cat << END
{
    "project_name": "$2",
    "requirements": "$3"
}
END
)
        response=$(curl -s -w "%{http_code}" -X POST "$SERVER_URL/api/projects" \
            -H "Content-Type: application/json" \
            -d "$PROJECT_DATA" 2>/dev/null)
        status_code=${response: -3}
        body=${response%???}
        
        if [ "$status_code" = "200" ]; then
            echo "✅ Proyecto creado exitosamente:"
            echo "$body" | python3 -m json.tool
        else
            echo "❌ Error creando proyecto (código: $status_code)"
            echo "$body"
        fi
        ;;
    "generate")
        if [ -z "$2" ]; then
            echo "Uso: ./forge_saas_commands.sh generate [project_id]"
            echo "Primero ejecuta: ./forge_saas_commands.sh projects"
            exit 1
        fi
        echo "🏗️ Generando proyecto $2..."
        
        # Planificar
        plan_response=$(curl -s -X POST "$SERVER_URL/api/projects/$2/plan" 2>/dev/null)
        echo "📋 Planificación iniciada..."
        
        # Esperar y generar
        sleep 5
        gen_response=$(curl -s -X POST "$SERVER_URL/api/projects/$2/generate" 2>/dev/null)
        echo "💻 Generación iniciada..."
        
        echo "⏳ La generación está en progreso. Verifica el estado con:"
        echo "   ./forge_saas_commands.sh status"
        echo "   tail -f server.log"
        ;;
    "logs")
        echo "📋 Últimos logs del servidor:"
        if [ -f "server.log" ]; then
            tail -20 server.log
        else
            echo "No hay archivo de logs. Ejecuta './forge_saas_commands.sh start' primero."
        fi
        ;;
    "clean")
        echo "🧹 Limpiando archivos temporales..."
        ./forge_saas_commands.sh stop
        rm -f server.log server.pid 2>/dev/null
        echo "✅ Limpieza completada"
        ;;
    *)
        echo "Forge SaaS - Sistema de Generación de Código"
        echo "Comandos disponibles:"
        echo "  start     - Iniciar servidor"
        echo "  stop      - Detener servidor" 
        echo "  restart   - Reiniciar servidor"
        echo "  status    - Estado del sistema"
        echo "  projects  - Listar proyectos"
        echo "  create    - Crear nuevo proyecto"
        echo "  generate  - Generar proyecto existente"
        echo "  logs      - Ver logs del servidor"
        echo "  clean     - Limpiar archivos temporales"
        echo ""
        echo "Ejemplos:"
        echo "  ./forge_saas_commands.sh create \"Mi App\" \"Una app React con Node.js\""
        echo "  ./forge_saas_commands.sh generate [project-id]"
        echo "  ./forge_saas_commands.sh logs"
        ;;
esac
