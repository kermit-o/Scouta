#!/usr/bin/env bash
# dev/scan_api_problems.sh — Diagnóstico UI ⇄ Backend (Connection refused / api_base)
set -Eeuo pipefail
DC="${DC:-docker compose}"
UI_SERVICE="${UI_SERVICE:-ui}"
BACKEND_SERVICE="${BACKEND_SERVICE:-backend}"
BACKEND_HOST="${BACKEND_HOST:-backend}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
HOST_BACKEND_URL="http://localhost:${BACKEND_PORT}"
INTERNAL_BACKEND_URL="http://${BACKEND_HOST}:${BACKEND_PORT}"

echo "== compose ps =="
$DC ps

echo; echo "== curl HOST -> $HOST_BACKEND_URL/api/health =="
curl -v --max-time 5 "$HOST_BACKEND_URL/api/health" 2>&1 || true

UI_ID="$($DC ps -q $UI_SERVICE || true)"
echo; echo "== UI container: ${UI_ID:-<none>} =="

echo; echo "== logs ui (tail 120) =="
$DC logs --tail=120 $UI_SERVICE || true

echo; echo "== logs backend (tail 120) =="
$DC logs --tail=120 $BACKEND_SERVICE || true

echo; echo "== grep code patterns (UI) =="
grep -RIn --line-number --exclude-dir='.git' --exclude-dir='.venv' \
  -e 'PUBLIC_API_BASE' -e '\<api_base\>' -e 'http://localhost:8000' \
  -e 'http://127.0.0.1:8000' -e 'st\.select\(' ui/ || true

if [ -n "$UI_ID" ]; then
  echo; echo "== env inside UI =="
  docker exec "$UI_ID" sh -lc 'env | grep -Ei "PUBLIC_API_BASE|API_BASE|BACKEND|URL" || true'

  echo; echo "== DNS resolve backend from UI =="
  docker exec "$UI_ID" sh -lc 'getent hosts backend || nslookup backend 2>/dev/null || true'

  echo; echo "== curl UI -> backend:8000/api/health =="
  docker exec "$UI_ID" sh -lc 'apk add --no-cache curl >/dev/null 2>&1 || true; curl -v --max-time 5 http://backend:8000/api/health 2>&1 || true'

  echo; echo "== curl UI -> localhost:8000/api/health =="
  docker exec "$UI_ID" sh -lc 'curl -v --max-time 5 http://localhost:8000/api/health 2>&1 || true'

  echo; echo "== show ui/01_Projects.py (1-120) =="
  docker exec "$UI_ID" sh -lc 'sed -n "1,120p" ui/01_Projects.py 2>/dev/null || true'
fi

echo; echo "== compose config (ui snippet) =="
$DC config --services >/dev/null 2>&1 && $DC config | awk '/ui:/{flag=1} flag{print} /image:/{if(flag) exit}' || true

echo; echo "END"
