# NEXT STEPS
1) Abrir este stage en Codespaces y arrancar backend con SQLite:
   cd reorg_stage_*/backend
   export DATABASE_URL="sqlite:///./dev.sqlite3"
   export PYTHONPATH="$(pwd)"
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

2) Validar /health y endpoints principales.
3) Ajustar imports residuales si los hubiera.
4) Preparar docker/compose con Postgres/Redis para prueba real.
5) Resolver migraciones Alembic y ejecutar `alembic upgrade head`.
6) Cuando esté OK, usar DRYRUN_GIT_MV.sh como base para el commit final (o te genero script automático).
