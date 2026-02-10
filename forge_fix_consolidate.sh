#!/usr/bin/env bash
set -euo pipefail

log(){ printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S%z')" "$*" >&2; }

# 1) Detectar último backend_consolidate_*
CANDIDATE="$(ls -d backend_consolidate_* 2>/dev/null | sort | tail -n1 || true)"
if [[ -z "${CANDIDATE:-}" || ! -d "$CANDIDATE" ]]; then
  log "❌ No encontré ningún directorio backend_consolidate_* en $(pwd)"
  exit 1
fi
log "📁 Usando backend consolidado: $CANDIDATE"

# 2) Verificar estructura esperada (app/)
if [[ ! -d "$CANDIDATE/app" ]]; then
  log "⚠️ $CANDIDATE no tiene 'app/'. Intento localizar subcarpeta equivalente..."
  # Busca una 'app' dentro de profundidad 2
  ALT_APP="$(find "$CANDIDATE" -maxdepth 2 -type d -name app | head -n1 || true)"
  if [[ -z "${ALT_APP:-}" ]]; then
    log "❌ No encuentro carpeta 'app' dentro de $CANDIDATE. Aborta para no romper nada."
    exit 1
  fi
  # Recolocar CANDIDATE a la raíz que contiene app
  CANDIDATE="$(dirname "$ALT_APP")"
  log "✅ Usaré como raíz: $CANDIDATE"
fi

# 3) Crear ai_config.py si no existe
CFG_DIR="$CANDIDATE/app/config"
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
  log "ℹ️ Ya existe: $CFG_FILE (no toco contenido)"
fi

# 4) Symlink 'backend' -> consolidado (para Dockerfile/paths antiguos)
if [[ -L backend || -d backend ]]; then
  if [[ -L backend ]]; then
    CURRENT="$(readlink backend || true)"
    if [[ "$CURRENT" != "$CANDIDATE" ]]; then
      rm -f backend
      ln -s "$CANDIDATE" backend
      log "🔗 Actualizado symlink backend -> $CANDIDATE"
    else
      log "�� Symlink backend ya apunta a $CANDIDATE"
    fi
  else
    log "⚠️ Existe una carpeta 'backend' real. Creo backup y la sustituyo por symlink."
    mv backend "backend.bak.$(date +%Y%m%d_%H%M%S)"
    ln -s "$CANDIDATE" backend
    log "🔗 backend → $CANDIDATE"
  fi
else
  ln -s "$CANDIDATE" backend
  log "🔗 backend → $CANDIDATE"
fi

# 5) Exponer puertos en docker/compose.yml si faltan
COMPOSE="docker/compose.yml"
if [[ ! -f "$COMPOSE" ]]; then
  log "❌ No encuentro $COMPOSE"
  exit 1
fi

ensure_port() {
  local service="$1" private="$2" public="$3"
  # Si ya hay línea con el mapeo, no tocar
  if grep -qE "^[[:space:]]*-[[:space:]]*\"?$public:$private\"?" "$COMPOSE"; then
    log "✅ $service ya publica $public:$private"
    return 0
  fi
  # Insertar bloque ports: si no existe, lo creamos; si existe, añadimos item
  if awk "/^[[:space:]]*$service:/{flag=1} flag && /^[[:space:]]*ports:/{print; exit}" "$COMPOSE" >/dev/null; then
    # añadir item bajo ports:
    awk -v svc="$service" -v map="      - \"$public:$private\"" '
      $0 ~ "^[ \t]*"svc":" {print; svc_found=1; next}
      svc_found && $0 ~ /^[ \t]*ports:/ {print; print map; svc_found=0; next}
      {print}
    ' "$COMPOSE" > "$COMPOSE.tmp" && mv "$COMPOSE.tmp" "$COMPOSE"
    log "🔧 Añadido puerto en $service: $public:$private"
  else
    # crear bloque ports: bajo el servicio
    awk -v svc="$service" -v ports="    ports:\n      - \"$public:$private\"" '
      $0 ~ "^[ \t]*"svc":" {
        print; print ports; inserted=1; next
      }
      {print}
      END { if (!inserted) { exit 1 } }
    ' "$COMPOSE" > "$COMPOSE.tmp" && mv "$COMPOSE.tmp" "$COMPOSE"
    log "🔧 Creado bloque ports en $service: $public:$private"
  fi
}

ensure_port "backend" 8000 8000
ensure_port "frontend" 3000 3000
ensure_port "postgres" 5432 5432 || true  # opcional exponer

# 6) Rebuild & up
log "🛠️ Reconstruyendo imágenes…"
docker compose -f "$COMPOSE" build

log "🚢 Levantando servicios…"
docker compose -f "$COMPOSE" up -d

# 7) Probar health
log "🩺 Probando /api/health (hasta 10 intentos)…"
for i in {1..10}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then
    echo "OK" && break
  fi
  sleep 2
done

log "📡 Respuesta /api/health:"
curl -sS "http://localhost:8000/api/health" || true
echo

log "✅ Listo."
