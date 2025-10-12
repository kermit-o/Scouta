#!/usr/bin/env bash
set -Eeuo pipefail
API="${API:-http://localhost:8000}"

say(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

say "Health"
curl -fsS "$API/api/health" | jq -r .

say "Crear proyecto"
NEW=$(curl -fsS -X POST "$API/api/projects/" \
  -H "content-type: application/json" \
  -d '{"name":"multi-agent-demo"}')
echo "$NEW"

PID=$(python - <<'PY' <<<"$NEW"
import json,sys
print(json.loads(sys.stdin.read())["id"])
PY
)
echo "PID=$PID"

say "Encolar /run"
curl -fsS -X POST "$API/api/projects/$PID/run" | jq -r .

say "Lanzar worker 10s (foreground)"
docker compose exec -T backend python - <<'PY'
from app.services.scheduler import worker_loop
# procesa cada 0.5s durante ~10s
worker_loop(0.5, max_seconds=10)
print("worker finished")
PY

say "Listar /runs"
curl -fsS "$API/api/projects/$PID/runs" | python -m json.tool || true
