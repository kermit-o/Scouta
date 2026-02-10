#!/usr/bin/env bash
set -euo pipefail
log(){ printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S%z')" "$*" >&2; }

# 1) Detectar último backend_consolidate_*
CANDIDATE="$(ls -d backend_consolidate_20251015-1755 2>/dev/null | sort | tail -n1 || true)"
if [[ -z "${CANDIDATE:-}" || ! -d "$CANDIDATE" ]]; then
  log "❌ No encontré ningún directorio backend_consolidate_* en $(pwd)"
  exit 1
fi
log "📁 Usando backend consolidado: $CANDIDATE"

# Si dentro hay backend_reorganized/app, usarlo como raíz
ROOT="$CANDIDATE"
if [[ -d "$CANDIDATE/backend_reorganized/app" ]]; then
  ROOT="$CANDIDATE/backend_reorganized"
  log "✅ Raíz backend detectada: $ROOT"
fi

# 2) Crear stub ai_config.py si falta
CFG_DIR="$ROOT/app/config"
mkdir -p "$CFG_DIR"
CFG_FILE="$CFG_DIR/ai_config.py"
if [[ ! -f "$CFG_FILE" ]]; then
  cat > "$CFG_FILE" <<'PY'
# Minimal AI config stub to unblock imports
class AIConfig:
    provider = "deepseek"
    model = "deepseek-chat"
    temperature = 0.7
ai_config = AIConfig()
PY
  log "🧩 Creado stub: $CFG_FILE"
else
  log "ℹ️ Ya existe: $CFG_FILE"
fi

# 3) Symlink 'backend' → raíz consolidada (para rutas antiguas)
if [[ -L backend || -d backend ]]; then
  if [[ -L backend && "$(readlink backend)" == "$ROOT" ]]; then
    log "🔗 Symlink 'backend' ya apunta a $ROOT"
  else
    [[ -e backend ]] && mv backend "backend.bak.$(date +%Y%m%d_%H%M%S)"
    ln -s "$ROOT" backend
    log "🔗 backend → $ROOT"
  fi
else
  ln -s "$ROOT" backend
  log "🔗 backend → $ROOT"
fi

# 4) Localizar docker/compose.yml (primero en el consolidate)
COMPOSE=""
if [[ -f "$CANDIDATE/docker/compose.yml" ]]; then
  COMPOSE="$CANDIDATE/docker/compose.yml"
elif [[ -f "docker/compose.yml" ]]; then
  COMPOSE="docker/compose.yml"
elif [[ -f "$CANDIDATE/compose.yml" ]]; then
  COMPOSE="$CANDIDATE/compose.yml"
else
  log "❌ No encuentro compose.yml (probé $CANDIDATE/docker/compose.yml, docker/compose.yml, $CANDIDATE/compose.yml)"
  exit 1
fi
log "📄 Compose file: $COMPOSE"

# 5) Asegurar puertos publicados en ese compose
ensure_port() {
  local svc="$1" private="$2" public="$3"
  if grep -qE "^[[:space:]]*-[[:space:]]*\"?$public:$private\"?" "$COMPOSE"; then
    log "✅ $svc ya publica $public:$private"
    return
  fi
  if awk "/^[[:space:]]*$svc:/{flag=1} flag && /^[[:space:]]*ports:/{print; exit}" "$COMPOSE" >/dev/null; then
    awk -v svc="$svc" -v map="      - \"$public:$private\"" '
      $0 ~ "^[ \t]*"svc":" {print; svc_found=1; next}
      svc_found && $0 ~ /^[ \t]*ports:/ {print; print map; svc_found=0; next}
      {print}
    ' "$COMPOSE" > "$COMPOSE.tmp" && mv "$COMPOSE.tmp" "$COMPOSE"
    log "🔧 Añadido puerto en $svc: $public:$private"
  else
    awk -v svc="$svc" -v ports="    ports:\n      - \"$public:$private\"" '
      $0 ~ "^[ \t]*"svc":" {print; print ports; inserted=1; next}
      {print}
      END { if (!inserted) exit 1 }
    ' "$COMPOSE" > "$COMPOSE.tmp" && mv "$COMPOSE.tmp" "$COMPOSE" || {
      log "⚠️ No pude insertar bloque ports en $svc (¿no existe el servicio?)"
    }
    log "🔧 Creado bloque ports en $svc: $public:$private"
  fi
}
ensure_port "backend" 8000 8000
ensure_port "frontend" 3000 3000
ensure_port "postgres" 5432 5432 || true  # opcional

# 6) .env junto al compose (si no existe, crear plantilla mínima)
COMPOSE_DIR="$(dirname "$COMPOSE")"
ENV_FILE="$COMPOSE_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<'EOV'
# ===== Forge SaaS minimal env (.env) =====
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/forge
REDIS_URL=redis://redis:6379/0
#STRIPE_SECRET_KEY=sk_test_xxx
#PRO_PRICE_ID=price_xxx
#WEBHOOK_SECRET=whsec_xxx
EOV
  log "🗂️ Creado $ENV_FILE (ajusta valores reales si usas Stripe)"
else
  log "ℹ️ Ya existe $ENV_FILE"
fi

# 7) Build & Up usando ese compose
log "🛠️ docker compose build…"
docker compose -f "$COMPOSE" build

log "🚢 docker compose up -d…"
docker compose -f "$COMPOSE" up -d

# 8) Healthcheck
log "🩺 Probando /api/health (hasta 12 intentos)…"
for i in {1..12}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
log "📡 Respuesta /api/health:"
curl -sS "http://localhost:8000/api/health" || true
echo
log "✅ Listo."
