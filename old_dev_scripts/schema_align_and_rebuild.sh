#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
BACKEND="backend"
PG="postgres"

say(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }
ok(){ printf "\033[32m%s\033[0m\n" "$*"; }
warn(){ printf "\033[33m%s\033[0m\n" "$*"; }
err(){ printf "\033[31m%s\033[0m\n" "$*"; }

MIG="backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py"
say "1) Parchear migración manual para usar String() en project_id (coincide con projects.id VARCHAR)"
if [ -f "$MIG" ]; then
  cp -n "$MIG" "${MIG}.bak" || true
  # Cambia cualquier UUID(as_uuid=True) SOLO en project_id por String()
  sed -i 's/sa\.Column("project_id",[[:space:]]*postgresql\.UUID(as_uuid=True)/sa.Column("project_id", sa.String()/g' "$MIG"
  # Si quedaron CNs con UUID residuales, no tocamos (solo project_id)
  ok "Migración parcheada: $MIG"
else
  err "No existe $MIG (asegúrate de haber creado la migración manual)."; exit 1
fi

say "2) Parchear modelos para usar String en project_id"
for F in backend/app/models/job.py backend/app/models/agent_run.py backend/app/models/artifact.py; do
  if [ -f "$F" ]; then
    cp -n "$F" "${F}.bak" || true
    sed -i 's/Column(UUID(as_uuid=True), ForeignKey("projects.id")/Column(String, ForeignKey("projects.id")/g' "$F"
    ok "OK: $F"
  else
    warn "No existe $F (lo salto)"
  fi
done

say "3) Verificar import de Base"
$DC run --rm -T "$BACKEND" python - <<'PY'
from app.db import Base
print("Base OK:", Base)
PY

say "4) Reset controlado de Alembic y reproducción de migraciones"
# No tocaremos datos; si la DB está vacía, simplemente se recrea el esquema.
$DC run --rm -T "$BACKEND" alembic stamp base
$DC run --rm -T "$BACKEND" alembic upgrade head || {
  err "Fallo upgrade head; intento paso a paso..."
  # Intenta avanzar paso a paso por histórico (ajusta si tu serie cambia)
  $DC run --rm -T "$BACKEND" alembic upgrade a8c9437bc05e
  $DC run --rm -T "$BACKEND" alembic upgrade 9883c0d1530d
  $DC run --rm -T "$BACKEND" alembic upgrade 9d5a86746acc
  $DC run --rm -T "$BACKEND" alembic upgrade 2493383f2097
  $DC run --rm -T "$BACKEND" alembic upgrade 724eef377a2d
  $DC run --rm -T "$BACKEND" alembic upgrade head
}

say "5) Levantar backend y chequear salud"
$DC up -d "$BACKEND"
sleep 1
curl -fsS http://localhost:8000/api/health && ok "-> backend OK"

say "6) Versión Alembic actual"
$DC run --rm -T "$BACKEND" alembic current || true

ok "DONE"
