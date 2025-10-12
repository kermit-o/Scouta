#!/bin/bash
echo "=== SCOUTA/FORGE - ESTADO FINAL ==="
echo ""

echo "🐳 CONTENEDORES ACTIVOS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 BACKEND API:"
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend respondiendo"
    curl -s http://localhost:8000/api/health
else
    echo "❌ Backend no responde"
fi

echo ""
echo "🤖 WORKER STATUS:"
if docker ps | grep -q worker-simple; then
    echo "✅ Worker activo"
    docker logs worker-simple --tail=3 2>/dev/null || echo "Worker sin logs recientes"
else
    echo "❌ Worker no activo"
fi

echo ""
echo "📊 DATABASE:"
docker compose exec postgres psql -U forge -d forge -c "
SELECT 
  (SELECT COUNT(*) FROM projects) as projects,
  (SELECT COUNT(*) FROM jobs WHERE state = 'queued') as queued_jobs,
  (SELECT COUNT(*) FROM jobs WHERE state = 'done') as completed_jobs,
  (SELECT COUNT(*) FROM agent_runs) as total_runs;
"
