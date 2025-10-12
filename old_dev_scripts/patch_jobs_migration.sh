#!/usr/bin/env bash
set -euo pipefail
# Detecta el archivo de migración "jobs_agent_runs_artifacts_0001"
MIG=$(ls backend/migrations/versions/*jobs_agent_runs_artifacts* 2>/dev/null | head -n1 || true)
if [ -z "${MIG}" ]; then
  # fallback a nombre genérico por fecha que usaste
  MIG=$(ls backend/migrations/versions/*20250928_jobs_agent_runs_artifacts*.py 2>/dev/null | head -n1 || true)
fi
if [ -z "${MIG}" ]; then
  echo "No encuentro la migración de jobs/agent_runs/artifacts."
  exit 1
fi

cp -n "$MIG" "$MIG.bak" || true

# Cambia project_id de UUID -> sa.String()
sed -i 's/postgresql\.UUID(as_uuid=True)/sa.String()/g' "$MIG"
sed -i 's/SaUUID(as_uuid=True)/sa.String()/g' "$MIG" 2>/dev/null || true
# Asegúrate que imports tengan sa
grep -q 'import sqlalchemy as sa' "$MIG" || sed -i '1i import sqlalchemy as sa' "$MIG"

echo "Parcheado $MIG"
