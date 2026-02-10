#!/bin/bash
# Monitor en tiempo real del proyecto

echo "Monitor Blog-AI - Ctrl+C para salir"
echo "======================================"

while true; do
    clear
    echo "$(date) - Monitor activo"
    echo ""
    
    # Estado servidor
    echo "📊 SERVIDOR:"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Online"
        
        # Últimas requests
        echo "   Últimas requests:"
        tail -n 5 /tmp/api.log 2>/dev/null | grep "\[REQ\]" || echo "   Ninguna reciente"
    else
        echo "   ❌ Offline"
    fi
    
    # Contadores
    echo ""
    echo "📈 ESTADÍSTICAS:"
    cd /workspaces/Scouta/blog-ai/blog-saas/api
    sqlite3 dev.db << SQL | while read line; do echo "   $line"; done
SELECT 'Posts: ' || (SELECT COUNT(*) FROM posts) ||
       ' | Agents: ' || (SELECT COUNT(*) FROM agent_profiles) ||
       ' | Comments: ' || (SELECT COUNT(*) FROM comments) ||
       ' | Actions: ' || (SELECT COUNT(*) FROM agent_actions)
SQL
    
    # Errores recientes
    echo ""
    echo "⚠️  ERRORES RECIENTES:"
    grep -i "error\|exception" /tmp/api.log 2>/dev/null | tail -3 || echo "   Ninguno"
    
    sleep 5
done
