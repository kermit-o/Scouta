#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
SERVICE="backend"
MIG="backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py"
PREV_HEAD="724eef377a2d"   # último head que mostraste antes de nuestra migración manual

green(){ printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }
red(){ printf "\033[31m%s\033[0m\n" "$*"; }
bar(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

bar "1) Stamp base y upgrade al head previo (${PREV_HEAD})"
$DC run --rm -T $SERVICE alembic stamp base
$DC run --rm -T $SERVICE alembic upgrade $PREV_HEAD

bar "2) Detectar tipo de projects.id"
PID_TYPE="$($DC run --rm -T $SERVICE python - <<'PY'
import os, sqlalchemy as sa
eng = sa.create_engine(os.environ["DATABASE_URL"], future=True)
ins = sa.inspect(eng)
cols = {c['name']: str(c['type']).lower() for c in ins.get_columns('projects', schema='public')}
print(cols.get('id', 'unknown'))
PY
)"
echo "projects.id type = ${PID_TYPE}"

if [[ "$PID_TYPE" == "unknown" ]]; then
  red "No encuentro tabla 'projects'. Algo no aplicó bien. Aborta."
  exit 1
fi

bar "3) Parchear migración ${MIG} para alinear FK a projects.id"
if [[ ! -f "$MIG" ]]; then
  red "No existe ${MIG}. Asegúrate de haber creado la migración manual."
  exit 1
fi

cp -n "$MIG" "${MIG}.bak" || true

if echo "$PID_TYPE" | grep -qi uuid; then
  # projects.id es UUID → aseguramos UUID en project_id
  sed -i 's/sa\.Column("project_id", *sa\.String() *,/sa.Column("project_id", postgresql.UUID(as_uuid=True), /g' "$MIG" || true
  # por si la migración quedó en UUID ya, lo dejamos tal cual
  yellow "Usaremos UUID para project_id en jobs/agent_runs/artifacts"
else
  # projects.id es varchar → aseguramos String en project_id
  sed -i 's/postgresql\.UUID(as_uuid=True)/sa.String()/g' "$MIG"
  yellow "Usaremos String (varchar) para project_id en jobs/agent_runs/artifacts"
fi

bar "4) Aplicar migración nueva (subir a head)"
$DC up -d $SERVICE
$DC exec -T $SERVICE alembic upgrade head

bar "5) Imprimir esquema actual (db_introspect)"
if [[ -x dev/db_introspect.sh ]]; then
  bash dev/db_introspect.sh
else
  yellow "dev/db_introspect.sh no existe/ejecutable. Lo creo por ti."
  cat > dev/db_introspect.sh <<'INT'
#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
SERVICE="${SERVICE:-backend}"
printf "\n== Alembic ==\n"
$DC run --rm -T "$SERVICE" alembic current || true
$DC run --rm -T "$SERVICE" alembic heads || true
printf "\n== DATABASE_URL ==\n"
$DC run --rm -T "$SERVICE" python - <<'PY'
import os; print(os.getenv("DATABASE_URL"))
PY
printf "\n== Esquema ==\n"
$DC run --rm -T "$SERVICE" python - <<'PY'
import os, sqlalchemy as sa
eng = sa.create_engine(os.environ["DATABASE_URL"], future=True)
ins = sa.inspect(eng)
tabs = ins.get_table_names(schema="public")
print("Tables:", tabs)
def dump(t):
  if t not in tabs: print(f"-- {t} (NO EXISTE)"); return
  print(f"-- {t} --")
  for c in ins.get_columns(t, schema="public"):
    print(" ", c["name"], str(c["type"]).lower(), "nullable=", c["nullable"])
  print(" PK:", ins.get_pk_constraint(t, schema="public"))
  print(" FKs:", ins.get_foreign_keys(t, schema="public"))
for t in ["projects","jobs","agent_runs","artifacts"]: dump(t)
PY
INT
  chmod +x dev/db_introspect.sh
  bash dev/db_introspect.sh
fi

green "DONE"
