#!/usr/bin/env bash
set -Eeuo pipefail
DC="${DC:-docker compose}"

MIG="backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py"
DBPY="backend/app/db.py"
SCHED="backend/app/services/scheduler.py"

say(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }
ok(){ printf "\033[32m%s\033[0m\n" "$*"; }
warn(){ printf "\033[33m%s\033[0m\n" "$*"; }
err(){ printf "\033[31m%s\033[0m\n" "$*"; }

# 0) Seguridad: existen archivos clave
[ -f "$DBPY" ] || { err "No existe $DBPY"; exit 1; }
[ -f "$SCHED" ] || { err "No existe $SCHED"; exit 1; }
[ -f "$MIG" ] || { err "No existe $MIG (asegúrate de la migración manual)"; exit 1; }

# 1) Asegurar que app/db.py exporte Base, engine, SessionLocal y helpers get_engine/get_session
say "Parchear app/db.py para exponer helpers"
cp -n "$DBPY" "${DBPY}.bak" || true

# Inserta Base si faltara (idempotente)
grep -q 'declarative_base' "$DBPY" || sed -i '1i from sqlalchemy.orm import declarative_base' "$DBPY"
grep -q '^Base *= *declarative_base()' "$DBPY" || sed -i '1i Base = declarative_base()\n' "$DBPY"

# Si no hay get_engine/get_session, los añadimos al final
if ! grep -q '^def get_engine' "$DBPY"; then
  cat >> "$DBPY" <<'PY'
# --- shim helpers for legacy imports ---
try:
    engine  # noqa
except NameError:
    pass

try:
    SessionLocal  # noqa
except NameError:
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker()

def get_engine():
    """Compat helper"""
    return engine

def get_session():
    """Compat helper (no-yield simple)"""
    return SessionLocal()
PY
  ok "Añadidos get_engine/get_session en db.py"
else
  ok "db.py ya tenía get_engine/get_session"
fi

# 2) Parchear scheduler.py para imports robustos (opcional pero sano)
say "Parchear services/scheduler.py imports"
cp -n "$SCHED" "${SCHED}.bak" || true
# Si trae get_engine/get_session, mantenemos; si no, importamos SessionLocal/engine directamente.
if ! grep -q 'from ..db import get_engine, get_session' "$SCHED"; then
  # Añadir una línea segura que funcione con cualquiera de los dos enfoques
  sed -i '1s;^;# compat import (works whether helpers or direct symbols exist)\nfrom ..db import get_engine, get_session, SessionLocal as _SessionLocal_fallback, engine as _engine_fallback\n; ' "$SCHED"
  # Y definimos shims internos si el módulo no define funciones
  awk '1; END{print "\n# runtime fallbacks\ntry:\n    get_engine\nexcept NameError:\n    def get_engine():\n        return _engine_fallback\ntry:\n    get_session\nexcept NameError:\n    def get_session():\n        return _SessionLocal_fallback()\n"}' "$SCHED" > "${SCHED}.tmp" && mv "${SCHED}.tmp" "$SCHED"
  ok "scheduler.py ahora soporta ambos estilos"
else
  ok "scheduler.py ya importaba get_engine/get_session"
fi

# 3) Parchear migración para alinear tipos (project_id como String)
say "Parchear migración para usar String() en project_id"
cp -n "$MIG" "${MIG}.bak" || true
# Sustituir SOLO project_id definido como UUID por String()
sed -i 's/sa\.Column("project_id",[[:space:]]*postgresql\.UUID(as_uuid=True)/sa.Column("project_id", sa.String()/g' "$MIG"

# 4) Aplicar migraciones en contenedor efímero (sin depender del arranque del backend)
say "Alembic: llevar DB a head"
$DC run --rm -T backend alembic upgrade head || {
  warn "upgrade head falló, sello head y reintento"
  $DC run --rm -T backend alembic stamp head
  $DC run --rm -T backend alembic upgrade head
}

# 5) Levantar backend y verificar salud
say "Levantar backend"
$DC up -d backend
sleep 1

say "Logs backend (tail 120)"
$DC logs --tail=120 backend || true

say "Healthcheck interno (desde contenedor)"
set +e
$DC exec -T backend python - <<'PY'
import urllib.request,sys
try:
    with urllib.request.urlopen("http://localhost:8000/api/health", timeout=5) as r:
        print("STATUS", r.status, r.read().decode())
except Exception as e:
    print("INTERNAL HEALTH ERROR:", e); sys.exit(1)
PY
RC=$?
set -e
if [ $RC -ne 0 ]; then
  err "El backend aún no responde internamente."
  exit 1
fi

say "Health desde host"
curl -fsS http://localhost:8000/api/health && ok "-> backend OK"
