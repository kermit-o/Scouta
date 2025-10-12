#!/usr/bin/env bash
set -euo pipefail

DB="backend/app/db.py"
ENV="backend/migrations/env.py"

echo "== 1) Parchear ${DB} para exportar Base =="
cp -n "$DB" "${DB}.bak" || true
# Inserta import declarative_base si falta
grep -q 'from sqlalchemy.orm import declarative_base' "$DB" || \
  sed -i '1i from sqlalchemy.orm import declarative_base' "$DB"
# Inserta definición de Base si falta
grep -q '^Base *= *declarative_base()' "$DB" || \
  sed -i '2i Base = declarative_base()\n' "$DB"

echo "== 2) Parchear ${ENV} para usar Base y cargar modelos =="
cp -n "$ENV" "${ENV}.bak" || true

# Asegura import de Base
grep -q 'from app.db import Base' "$ENV" || \
  sed -i '1i from app.db import Base' "$ENV"

# Asegura imports explícitos de modelos (para autogenerate)
for mdl in 'from app.models.project import Project' \
           'from app.models.job import Job' \
           'from app.models.agent_run import AgentRun' \
           'from app.models.artifact import Artifact'
do
  grep -qF "$mdl" "$ENV" || echo "$mdl" >> "$ENV"
done

# Asegura target_metadata = Base.metadata
grep -q 'target_metadata *= *Base\.metadata' "$ENV" || \
  sed -i 's/^target_metadata *= *.*/target_metadata = Base.metadata/' "$ENV"

echo "== 3) Verificación de imports en contenedor efímero =="
docker compose run --rm -T backend python - <<'PY'
from app.db import Base
print("OK Base:", Base)
from app.models.project import Project
from app.models.job import Job
from app.models.agent_run import AgentRun
from app.models.artifact import Artifact
print("OK models imported")
PY

echo "== 4) Generar revisión Alembic autogenerada =="
docker compose run --rm -T backend alembic revision -m "init jobs/agent_runs/artifacts" --autogenerate

echo "== 5) Levantar backend y aplicar migraciones =="
docker compose up -d backend
docker compose exec -T backend alembic upgrade head

echo "== 6) Healthcheck =="
curl -fsS http://localhost:8000/api/health && echo " -> backend OK"

echo "DONE."
