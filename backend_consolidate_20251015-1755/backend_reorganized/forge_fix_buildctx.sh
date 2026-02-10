#!/usr/bin/env bash
set -euo pipefail
log(){ printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S%z')" "$*" >&2; }

CANDIDATE="$(ls -d backend_consolidate_* 2>/dev/null | sort | tail -n1 || true)"
[[ -z "${CANDIDATE:-}" ]] && { log "❌ No encontré backend_consolidate_*"; exit 1; }
DOCKER_DIR="$CANDIDATE/docker"
COMPOSE="$DOCKER_DIR/compose.yml"
[[ -f "$COMPOSE" ]] || { log "❌ No existe $COMPOSE"; exit 1; }

# backup
TS="$(date +%Y%m%d_%H%M%S)"
cp "$COMPOSE" "$COMPOSE.bak.$TS"
log "🗂️ Backup: $COMPOSE.bak.$TS"

# reescribir compose con context correcto (..)
cat > "$COMPOSE" <<'YML'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: forge
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.backend
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile.frontend
    env_file:
      - .env
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  pgdata:
YML

# validar compose
docker compose -f "$COMPOSE" config >/dev/null
log "✅ compose.yml válido con context: .."

# .env junto a compose (si no existe)
ENV_FILE="$DOCKER_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<'ENV'
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/forge
REDIS_URL=redis://redis:6379/0
#STRIPE_SECRET_KEY=sk_test_xxx
#PRO_PRICE_ID=price_xxx
#WEBHOOK_SECRET=whsec_xxx
ENV
  log "🗒️ Creado $ENV_FILE"
else
  log "ℹ️ Ya existe $ENV_FILE"
fi

# asegurar symlink backend -> backend_reorganized para rutas antiguas
ROOT="$CANDIDATE"
[[ -d "$CANDIDATE/backend_reorganized/app" ]] && ROOT="$CANDIDATE/backend_reorganized"
[[ -e backend && ! -L backend ]] && mv backend "backend.bak.$TS"
[[ -L backend ]] && rm -f backend
ln -s "$ROOT" backend
log "🔗 backend → $ROOT"

# build + up
log "🛠️ docker compose build…"
docker compose -f "$COMPOSE" build

log "🚢 docker compose up -d…"
docker compose -f "$COMPOSE" up -d

# health
log "🩺 Probando /api/health…"
for i in {1..15}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then break; fi
  sleep 2
done
log "📡 Respuesta:"
curl -sS "http://localhost:8000/api/health" || true
echo
log "✅ Listo."
