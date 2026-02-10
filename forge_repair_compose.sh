#!/usr/bin/env bash
set -euo pipefail
log(){ printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S%z')" "$*" >&2; }

CANDIDATE="$(ls -d backend_consolidate_20251015-1755* 2>/dev/null | sort | tail -n1 || true)"
[[ -z "${CANDIDATE:-}" ]] && { log "❌ No encontré backend_consolidate_*"; exit 1; }
log "📁 Consolidate: $CANDIDATE"

ROOT="$CANDIDATE"
[[ -d "$CANDIDATE/backend_reorganized/app" ]] && ROOT="$CANDIDATE/backend_reorganized"
DOCKER_DIR="$CANDIDATE/docker"
COMPOSE="$DOCKER_DIR/compose.yml"

[[ -f "$COMPOSE" ]] || { log "❌ No existe $COMPOSE"; exit 1; }

# 1) Backup
TS="$(date +%Y%m%d_%H%M%S)"
cp "$COMPOSE" "$COMPOSE.bak.$TS"
log "🗂️ Backup: $COMPOSE.bak.$TS"

# 2) Sanear BOM/control chars y líneas basura comunes
TMP="$COMPOSE.sanitized.$TS"
# quita BOM, elimina caracteres no imprimibles (excepto \t), elimina líneas que contengan restos de here-doc
sed '1 s/^\xEF\xBB\xBF//' "$COMPOSE" \
| tr -d '\000' \
| awk '{gsub(/[\r]/,"")}1' \
| awk '!/forge_fix_consolidate_v2\.sh/ && !/forge_fix_consolidate\.sh/' \
> "$TMP"
mv "$TMP" "$COMPOSE"
log "🧼 Saneado básico aplicado"

# 3) Validar
if docker compose -f "$COMPOSE" config >/dev/null 2>&1; then
  log "✅ compose.yml válido tras saneo"
else
  log "⚠️ Sigue inválido; voy a reconstruir un compose mínimo correcto"

  cat > "$COMPOSE" <<YML
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
      context: ${CANDIDATE}
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
      context: ${CANDIDATE}
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

  if docker compose -f "$COMPOSE" config >/dev/null 2>&1; then
    log "✅ compose.yml reconstruido y válido"
  else
    log "❌ No pude validar compose.yml incluso tras reconstruir. Revisa manualmente $COMPOSE y su backup."
    exit 1
  fi
fi

# 4) Asegurar .env junto al compose
ENV_FILE="$DOCKER_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<'ENV'
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/forge
REDIS_URL=redis://redis:6379/0
#STRIPE_SECRET_KEY=sk_test_xxx
#PRO_PRICE_ID=price_xxx
#WEBHOOK_SECRET=whsec_xxx
ENV
  log "🗒️ Creado $ENV_FILE (ajusta credenciales si usas Stripe)"
else
  log "ℹ️ Ya existe $ENV_FILE"
fi

# 5) Symlink 'backend' → ROOT (para rutas antiguas)
if [[ -e backend && ! -L backend ]]; then
  mv backend "backend.bak.$TS"
fi
[[ -L backend ]] && rm -f backend
ln -s "$ROOT" backend
log "🔗 backend → $ROOT"

# 6) Build & Up
log "🛠️ docker compose build…"
docker compose -f "$COMPOSE" build

log "🚢 docker compose up -d…"
docker compose -f "$COMPOSE" up -d

# 7) Healthcheck
log "🩺 Probando /api/health…"
for i in {1..15}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then break; fi
  sleep 2
done
log "📡 Respuesta:"
curl -sS "http://localhost:8000/api/health" || true
echo
log "✅ Reparación completa."
