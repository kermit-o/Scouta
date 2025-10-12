#!/usr/bin/env bash
set -Eeuo pipefail

FILE="backend/app/routers/projects.py"

echo "== 1) Respaldar ${FILE} =="
cp -n "$FILE" "${FILE}.bak" || true

echo "== 2) Parchar decoradores de /run y /runs a rutas relativas =="
# Quita cualquier prefijo duro '/api/projects' en esos dos endpoints
sed -i \
  -e 's|@router.post("/api/projects/\{project_id\}/run"|@router.post("/{project_id}/run"|g' \
  -e 's|@router.get("/api/projects/\{project_id\}/runs"|@router.get("/{project_id}/runs"|g' \
  "$FILE"

echo "== 3) Mostrar diff breve =="
if command -v git >/dev/null 2>&1; then
  git --no-pager diff -- "$FILE" || true
else
  echo "(git no disponible)"
fi

echo "== 4) Reconstruir y relanzar backend =="
docker compose up -d --build backend
sleep 1

echo "== 5) Verificar OpenAPI rutas corregidas =="
curl -sS http://localhost:8000/openapi.json \
  | python - <<'PY'
import sys,json,re
paths = json.load(sys.stdin)['paths'].keys()
targets = [p for p in paths if re.search(r'/api/projects/.*/run(s)?$', p)]
print("\n".join(sorted(targets)) or "NO_RUN_ROUTES")
PY

echo "== 6) Smoke rápido =="
API="http://localhost:8000"
set -e
curl -fsS "$API/api/health" >/dev/null
NEW=$(curl -fsS -X POST "$API/api/projects/" -H "content-type: application/json" -d '{"name":"multi-agent-demo"}')
PID=$(jq -r '.id' <<<"$NEW")
echo "PID=$PID"
curl -fsS -X POST "$API/api/projects/$PID/run" >/dev/null && echo "POST /run -> OK"
curl -fsS "$API/api/projects/$PID/runs" | python -m json.tool || true
