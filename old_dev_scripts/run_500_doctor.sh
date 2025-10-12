#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8000}"

echo "== Health =="
curl -fsS "$API/api/health" && echo

echo "== Crear proyecto =="
NEW=$(curl -fsS -X POST "$API/api/projects/" -H 'content-type: application/json' -d '{"name":"multi-agent-demo"}')
echo "$NEW"
PID=$(jq -r '.id' <<<"$NEW")
echo "PID=$PID"

echo "== POST /run (debería 200) =="
set +e
RESP=$(curl -sS -w "\n%{http_code}\n" -X POST "$API/api/projects/$PID/run")
CODE=$(tail -n1 <<<"$RESP")
BODY=$(sed '$d' <<<"$RESP")
set -e
echo "HTTP $CODE"
echo "$BODY"

echo "== Últimos 120 logs del backend (buscando Traceback) =="
docker compose logs --tail=120 backend | sed -n '1,120p'

echo "== OpenAPI (rutas de run/runs) =="
curl -fsS "$API/openapi.json" | jq -r '.paths | keys[]' | grep -E '/api/projects/.*/run|/api/projects/.*/runs' || true

echo "== Alembic (current/heads) =="
docker compose run --rm -T backend alembic current || true
docker compose run --rm -T backend alembic heads || true

echo "== Tablas presentes =="
docker compose exec -T postgres psql -U forge -d forge -c "\dt"

echo "== Descripción de projects/jobs/agent_runs/artifacts (si existen) =="
for t in projects jobs agent_runs artifacts; do
  docker compose exec -T postgres psql -U forge -d forge -c "\d+ $t" || true
done
