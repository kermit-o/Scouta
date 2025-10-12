#!/usr/bin/env bash
set -Eeuo pipefail

DC="${DC:-docker compose}"
BACKEND=backend
PG=postgres
HEALTH_HOST="http://localhost:8000/api/health"
HEALTH_IN="http://localhost:8000/api/health"

log() { printf "\n\033[1m== %s ==\033[0m\n" "$*"; }
ok()  { printf "\033[32m%s\033[0m\n" "$*"; }
warn(){ printf "\033[33m%s\033[0m\n" "$*"; }
err() { printf "\033[31m%s\033[0m\n" "$*"; }

# 0) Estado compose
log "compose ps"
$DC ps || true

# 1) Asegurar Postgres saludable
log "Asegurar Postgres"
$DC up -d $PG
$DC ps $PG
# Espera a healthy si hay healthcheck
for i in {1..40}; do
  st="$($DC ps $PG 2>/dev/null | awk 'NR==2{print $4,$5}')"
  echo "  postgres status: $st"
  if echo "$st" | grep -qi 'healthy'; then break; fi
  sleep 1
done

# 2) Aplicar migraciones aunque el backend no esté arriba (one-off)
log "Alembic upgrade head (one-off)"
$DC run --rm -T $BACKEND alembic upgrade head || {
  warn "upgrade head falló; intento stamp head y reintento"
  $DC run --rm -T $BACKEND alembic stamp head
  $DC run --rm -T $BACKEND alembic upgrade head
}

# 3) Levantar backend
log "Levantar backend"
$DC up -d $BACKEND
$DC ps $BACKEND

# 4) Ver logs recientes
log "Logs backend (tail 120)"
$DC logs --tail=120 $BACKEND || true

# 5) Healthcheck desde dentro del contenedor
log "Health desde DENTRO del backend (urllib)"
$DC exec -T $BACKEND python - <<'PY' || true
import json,urllib.request,sys
try:
    with urllib.request.urlopen("http://localhost:8000/api/health", timeout=5) as r:
        print(r.status, r.read().decode())
except Exception as e:
    print("INTERNAL HEALTH ERROR:", e); sys.exit(1)
PY

# 6) Healthcheck desde el host
log "Health desde el HOST"
set +e
OUT="$(curl -fsS "$HEALTH_HOST" 2>&1)"
RC=$?
set -e
if [ $RC -ne 0 ]; then
  err "HOST health fallo: $OUT"
  log "Diagnóstico extra"
  CID="$($DC ps -q $BACKEND || true)"
  if [ -n "$CID" ]; then
    docker inspect -f 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' "$CID" || true
  fi
  log "Puertos publicados"
  $DC ps $BACKEND
  exit 1
else
  echo "$OUT"
  ok "-> backend OK"
fi
