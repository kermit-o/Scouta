#!/usr/bin/env bash
set -Eeuo pipefail
API="${API:-http://localhost:8000}"

log(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

log "Health"
curl -fsS "$API/api/health"

log "Crear proyecto"
NEW="$(curl -sS -X POST "$API/api/projects/" -H "content-type: application/json" -d '{"name":"multi-agent-demo"}')"
echo "$NEW"

PID="$(python - <<'PY'
import json,sys
raw=sys.stdin.read().strip()
print(json.loads(raw)["id"])
PY
<<<"$NEW")"
echo "PID=$PID"

log "Encolar /run"
curl -fsS -X POST "$API/api/projects/$PID/run" || true

log "Lanzar worker (foreground 10s)"
docker compose exec -T backend python - <<'PY'
import time
from services.scheduler import worker_loop
worker_loop(0.5, max_seconds=10)
PY

log "Listar /runs"
curl -sS "$API/api/projects/$PID/runs" | python -m json.tool || true
