#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
BACKEND="backend"
PG="postgres"
DBNAME="${DBNAME:-forge}"
DBUSER="${DBUSER:-forge}"

bar(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

bar "Alembic: current y heads"
$DC run --rm -T "$BACKEND" alembic current || true
$DC run --rm -T "$BACKEND" alembic heads || true

bar "DATABASE_URL"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os; print(os.getenv("DATABASE_URL","(no DATABASE_URL)"))
PY

bar "Tablas en public"
$DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -At -c \"select tablename from pg_tables where schemaname='public' order by 1;\"" || true

bar "Columnas + PK + FK por tabla"
$DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -c \"SELECT c.table_name, c.column_name, c.data_type, c.is_nullable FROM information_schema.columns c WHERE c.table_schema='public' ORDER BY 1,2;\"" || true
$DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -c \"SELECT tc.table_name, kcu.column_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema WHERE tc.constraint_type='PRIMARY KEY' AND tc.table_schema='public' ORDER BY 1;\"" || true
$DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -c \"SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table, ccu.column_name AS foreign_column FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name=tc.constraint_name AND ccu.table_schema=tc.table_schema WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public' ORDER BY 1;\"" || true

bar "Comparativa rápida types (projects.id vs *.project_id)"
$DC exec -T "$PG" sh -lc "
psql -U '$DBUSER' -d '$DBNAME' -At -c \"
WITH t AS (
  SELECT table_name, column_name, data_type
  FROM information_schema.columns
  WHERE table_schema='public'
)
SELECT
  'projects.id='||(SELECT data_type FROM t WHERE table_name='projects' AND column_name='id') AS p_id,
  'jobs.project_id='||(SELECT data_type FROM t WHERE table_name='jobs' AND column_name='project_id') AS j_pid,
  'agent_runs.project_id='||(SELECT data_type FROM t WHERE table_name='agent_runs' AND column_name='project_id') AS ar_pid,
  'artifacts.project_id='||(SELECT data_type FROM t WHERE table_name='artifacts' AND column_name='project_id') AS art_pid;
\"
" || true

bar "DDL por tabla (pg_dump -s)"
TABS="$($DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -At -c \"select tablename from pg_tables where schemaname='public' order by 1;\"" 2>/dev/null || true)"
if [ -n "$TABS" ]; then
  for t in $TABS; do
    echo; echo "-- DDL public.$t"
    $DC exec -T "$PG" sh -lc "pg_dump -s -U '$DBUSER' -d '$DBNAME' -t public.$t" || true
  done
else
  echo "(No hay tablas en public)"
fi
