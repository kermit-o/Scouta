# NEXT (Stage Backend Consolidation)

## Probar backend (SQLite)
cd backend
python -m pip install --user -r requirements.txt
export DATABASE_URL="sqlite:///./dev.sqlite3"
export PYTHONPATH="$(pwd)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# → http://localhost:8000/health

## Qué revisar
- /backend/app/core contiene el backend sólido (antes en core/), solo como **módulo**, no como entrypoint.
- Auto-discovery de routers: cualquier módulo que exporte `router`/`api` se monta.
- Un único Base (app.models.Base) y un único engine (app.config.db).
- Migraciones copiadas en backend/migrations/versions (resolver colisiones después).

## Siguientes pasos
1) Resolver colisiones de Alembic (si hay duplicados en versions/).
2) Ajustar modelos portables (sin uuid_generate_v4()/now()::text).
3) Añadir auth y deps (current_user, DB session) centralizados en app/deps.py si aún no están.
4) Preparar docker/compose.yml (postgres+redis+backend+frontend) para prueba real.
5) Cuando el stage esté ✅, generamos script `git mv` para aplicar en la rama real.
