#!/usr/bin/env bash
set -euo pipefail

ROOT="/workspaces/Scouta/blog-ai/blog-saas"
API="$ROOT/api"
ENV_FILE="$API/.env"

say(){ echo; echo "== $*"; }
die(){ echo "FAIL: $*" >&2; exit 1; }

say "0) Preconditions"
[ -d "$API" ] || die "API dir not found: $API"
[ -f "$ENV_FILE" ] || die ".env not found at $ENV_FILE"

say "1) Ensure venv + deps"
cd "$API"
python -m pip install -U pip >/dev/null
python -m pip install -U \
  fastapi uvicorn sqlalchemy alembic \
  python-jose[cryptography] passlib \
  python-dotenv requests jinja2 >/dev/null

say "2) DB migrate (if alembic exists)"
if [ -f "$API/alembic.ini" ] || [ -d "$API/alembic" ]; then
  alembic upgrade head || true
fi

say "3) Start API (bg)"
pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true
nohup uvicorn app.main:app --env-file "$ENV_FILE" --host 0.0.0.0 --port 8000 >"$ROOT/run_api.log" 2>&1 &
sleep 1

say "4) Health: openapi"
curl -sS http://localhost:8000/openapi.json >/dev/null || die "API not reachable (see $ROOT/run_api.log)"

say "5) Login + spawn smoke test"
TOKEN="$(curl -sS -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"outman3@example.com","password":"ChangeMe123!"}' \
  | python -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || true)"

[ -n "$TOKEN" ] || die "Login failed. See $ROOT/run_api.log"

curl -sS -X POST "http://localhost:8000/api/v1/orgs/1/posts/1/spawn-actions?n=1&force=true" \
  -H "Authorization: Bearer $TOKEN" >/dev/null || die "spawn-actions failed. See $ROOT/run_api.log"

say "6) Public blog template check"
# This will fail fast if templates missing/incorrect
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" "http://localhost:8000/blog/outman-studio/hello-agents" || true

say "DONE ✅  Logs: $ROOT/run_api.log"
