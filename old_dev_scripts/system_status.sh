#!/bin/bash
echo "=== SCOUTA/FORGE - ESTADO DEL SISTEMA ==="
echo ""

echo "�� CONTENEDORES:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}\t{{.Ports}}" | grep forge

echo ""
echo "🔧 BACKEND STATUS:"
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend API respondiendo"
    curl -s http://localhost:8000/api/health | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'   Health: {data}')
except:
    print('   (respuesta no JSON)')
"
else
    echo "❌ Backend API NO responde"
    echo "   Revisar: docker compose logs backend --tail=10"
fi

echo ""
echo "📊 DATABASE STATS:"
docker compose exec postgres psql -U forge -d forge -c "
SELECT 
  'Projects' as type, COUNT(*) as count FROM projects
UNION ALL
  SELECT 'Jobs', COUNT(*) FROM jobs
UNION ALL  
  SELECT 'Agent Runs', COUNT(*) FROM agent_runs
UNION ALL
  SELECT 'Artifacts', COUNT(*) FROM artifacts;
"

echo ""
echo "🔄 JOBS STATUS:"
docker compose exec postgres psql -U forge -d forge -c "
SELECT state, COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs), 2) as percentage
FROM jobs 
GROUP BY state 
ORDER BY state;
"

echo ""
echo "🤖 AGENT SUCCESS RATE:"
docker compose exec postgres psql -U forge -d forge -c "
SELECT agent, 
  COUNT(*) as total_runs,
  SUM(CASE WHEN status = 'ok' THEN 1 ELSE 0 END) as success,
  ROUND(100.0 * SUM(CASE WHEN status = 'ok' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM agent_runs 
GROUP BY agent 
ORDER BY success_rate DESC;
"
