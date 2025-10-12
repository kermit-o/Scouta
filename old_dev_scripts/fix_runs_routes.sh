#!/usr/bin/env bash
set -Eeuo pipefail

FILE="backend/app/routers/projects.py"
API="${API:-http://localhost:8000}"

echo "== 1) Backup =="
cp -n "$FILE" "${FILE}.bak" || true

echo "== 2) Normalizar decoradores a rutas relativas =="
# Cubre variantes con doble prefijo e incluso si quedó repetido dos veces
sed -i \
  -e 's|@router.post("/api/projects/\{project_id\}/run"|@router.post("/{project_id}/run"|g' \
  -e 's|@router.get("/api/projects/\{project_id\}/runs"|@router.get("/{project_id}/runs"|g' \
  -e 's|@router.post("/api/projects/api/projects/\{project_id\}/run"|@router.post("/{project_id}/run"|g' \
  -e 's|@router.get("/api/projects/api/projects/\{project_id\}/runs"|@router.get("/{project_id}/runs"|g' \
  "$FILE"

echo "== 3) (Opcional) Garantizar prefix del router =="
# Si por accidente cambiaron el prefix, lo normalizamos
sed -i \
  -e 's|APIRouter(\s*prefix\s*=\s*"/api/projects".*|APIRouter(prefix="/api/projects")|g' \
  "$FILE"

echo "== 4) Rebuild y restart backend =="
docker compose up -d --build backend
sleep 1

echo "== 5) Verificar OpenAPI para /run y /runs =="
curl -sS "$API/openapi.json" \
 | python - <<'PY'
import sys,json,re
paths = json.load(sys.stdin)['paths'].keys()
targets = sorted([p for p in paths if re.search(r'^/api/projects/\{project_id\}/run(s)?$', p)])
print("\n".join(targets) or "NO_RUN_ROUTES")
PY

echo "== 6) Smoke test =="
set -e
curl -fsS "$API/api/health" >/dev/null

NEW=$(curl -fsS -X POST "$API/api/projects/" -H "content-type: application/json" -d '{"name":"multi-agent-demo"}')
echo "$NEW"
PID=$(jq -r '.id' <<<"$NEW")
[[ -n "$PID" && "$PID" != "null" ]] || { echo "PID vacío"; exit 1; }
echo "PID=$PID"

curl -fsS -X POST "$API/api/projects/$PID/run" && echo "POST /run -> OK"
curl -sS "$API/api/projects/$PID/runs" | python -m json.tool || true
