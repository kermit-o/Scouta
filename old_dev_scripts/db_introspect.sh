#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
SERVICE="${SERVICE:-backend}"

green(){ printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }
red(){ printf "\033[31m%s\033[0m\n" "$*"; }
bar(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

bar "Alembic (revisión actual y heads)"
$DC run --rm -T "$SERVICE" alembic current || true
$DC run --rm -T "$SERVICE" alembic heads || true

bar "DATABASE_URL visible dentro del backend"
$DC run --rm -T "$SERVICE" python - <<'PY'
import os
print(os.getenv("DATABASE_URL", "(no DATABASE_URL)"))
PY

bar "Tablas y columnas (schema público)"
$DC run --rm -T "$SERVICE" python - <<'PY'
import os, sys, json
import sqlalchemy as sa

url = os.getenv("DATABASE_URL")
if not url:
    print("Sin DATABASE_URL"); sys.exit(0)

engine = sa.create_engine(url, pool_pre_ping=True, future=True)
ins = sa.inspect(engine)

# Listado de tablas
tables = ins.get_table_names(schema="public")
print("Tables:", tables)

def print_table(tbl):
    cols = ins.get_columns(tbl, schema="public")
    pks = ins.get_pk_constraint(tbl, schema="public")
    fks = ins.get_foreign_keys(tbl, schema="public")
    print(f"\n-- {tbl} --")
    for c in cols:
        print(f"  {c['name']}: {c['type']}, nullable={c['nullable']}, default={c.get('default')}")
    print("  PK:", pks)
    print("  FKs:")
    for fk in fks:
        print("   ", fk)

for t in ["projects", "jobs", "agent_runs", "artifacts"]:
    if t in tables:
        print_table(t)
    else:
        print(f"\n-- {t} -- (NO EXISTE)")

# Comparación de tipos: projects.id vs project_id de otras
def col_type(tbl, col):
    for c in ins.get_columns(tbl, schema="public"):
        if c["name"] == col:
            return str(c["type"]).lower()
    return None

pid_t = col_type("projects", "id")
print("\nType projects.id:", pid_t)

for t in ["jobs","agent_runs","artifacts"]:
    if t in tables:
        pt = col_type(t, "project_id")
        print(f"Type {t}.project_id:", pt)
        # heurística simple de mismatch
        if pid_t and pt and (("uuid" in pid_t) != ("uuid" in pt)):
            print(f"!! MISMATCH: projects.id ({pid_t}) vs {t}.project_id ({pt})")
PY

bar "Contenido de migración 20250928_jobs_agent_runs_artifacts.py (si existe)"
[ -f backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py ] && \
    sed -n '1,200p' backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py || \
    echo "No existe backend/migrations/versions/20250928_jobs_agent_runs_artifacts.py"

bar "Resumen y pista"
cat <<'TXT'
- Si ves "MISMATCH", significa que el tipo de projects.id y los project_id asociados no coinciden.
- Corrige o bien:
  (A) Cambiando project_id a que use el mismo tipo que projects.id en modelos + migración, o
  (B) Migrando projects.id al tipo deseado (más invasivo).
- Después: reconstruye y aplica migraciones.
TXT
