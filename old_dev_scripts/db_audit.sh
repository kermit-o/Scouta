#!/usr/bin/env bash
set -euo pipefail
DC="${DC:-docker compose}"
BACKEND="backend"
PG="postgres"
DBNAME="${DBNAME:-forge}"
DBUSER="${DBUSER:-forge}"

bold(){ printf "\033[1m%s\033[0m\n" "$*"; }
bar(){ printf "\n\033[1m== %s ==\033[0m\n" "$*"; }

bar "Alembic: revisión actual y heads"
$DC run --rm -T "$BACKEND" alembic current || true
$DC run --rm -T "$BACKEND" alembic heads || true

bar "DATABASE_URL (dentro del backend)"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os; print(os.getenv("DATABASE_URL","(no DATABASE_URL)"))
PY

bar "Listado de tablas en schema public"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os, sqlalchemy as sa
url=os.getenv("DATABASE_URL")
if not url: 
    print("Sin DATABASE_URL"); raise SystemExit(0)
e=sa.create_engine(url, future=True); i=sa.inspect(e)
tabs=i.get_table_names(schema="public")
print("Tables:", tabs)
PY

bar "Detalle de columnas, PK/FKs (todas las tablas)"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os, sqlalchemy as sa
url=os.getenv("DATABASE_URL")
e=sa.create_engine(url, future=True); i=sa.inspect(e)
tabs=i.get_table_names(schema="public")
for t in tabs:
    print(f"\n-- {t} --")
    for c in i.get_columns(t, schema="public"):
        print(f"  {c['name']:20} {str(c['type']).lower():20} nullable={c['nullable']}")
    print("  PK:", i.get_pk_constraint(t, schema="public"))
    fks=i.get_foreign_keys(t, schema="public")
    print("  FKs:")
    for fk in fks: print("   ", fk)
PY

bar "Comparativa de tipos: projects.id vs *.project_id"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os, sqlalchemy as sa
url=os.getenv("DATABASE_URL")
e=sa.create_engine(url, future=True); i=sa.inspect(e)
tabs=i.get_table_names(schema="public")
def ctype(t,c):
    try:
        for col in i.get_columns(t, schema="public"):
            if col["name"]==c: return str(col["type"]).lower()
    except Exception: return None
pid=ctype("projects","id")
print("projects.id =", pid)
for t in ("jobs","agent_runs","artifacts"):
    if t in tabs:
        pt=ctype(t,"project_id")
        print(f"{t}.project_id =", pt)
        if pid and pt and (("uuid" in pid)!=( "uuid" in pt )):
            print(f"!! MISMATCH entre projects.id ({pid}) y {t}.project_id ({pt})")
PY

bar "Recuento y primeras 5 filas (si existen)"
$DC run --rm -T "$BACKEND" python - <<'PY'
import os, sqlalchemy as sa, pandas as pd
url=os.getenv("DATABASE_URL")
e=sa.create_engine(url, future=True)
with e.connect() as con:
    tabs = [r[0] for r in con.exec_driver_sql(
        "select tablename from pg_tables where schemaname='public' order by 1"
    )]
    for t in tabs:
        try:
            n = con.exec_driver_sql(f"select count(*) from public.{t}").scalar()
            print(f"\n-- {t} -- rows={n}")
            df = pd.read_sql(f"select * from public.{t} order by 1 desc limit 5", con)
            print(df.to_string(index=False))
        except Exception as e:
            print(f"\n-- {t} -- error leyendo filas: {e}")
PY

bar "DDL por tabla (pg_dump) si está disponible en el contenedor postgres"
have_pg_dump="$($DC exec -T "$PG" sh -lc 'command -v pg_dump >/dev/null && echo yes || echo no' 2>/dev/null || echo no)"
if [ "$have_pg_dump" = "yes" ]; then
  # lista de tablas
  TABS="$($DC exec -T "$PG" sh -lc "psql -U '$DBUSER' -d '$DBNAME' -At -c \"select tablename from pg_tables where schemaname='public' order by 1;\"" 2>/dev/null || true)"
  if [ -n "$TABS" ]; then
    for t in $TABS; do
      echo
      bold "-- DDL: public.$t"
      $DC exec -T "$PG" sh -lc "pg_dump -s -U '$DBUSER' -d '$DBNAME' -t public.$t" || true
    done
  else
    echo "No hay tablas en public (según postgres)."
  fi
else
  echo "pg_dump no disponible en el contenedor $PG (saltando DDL)."
fi

echo
bold "FIN DEL REPORTE"
