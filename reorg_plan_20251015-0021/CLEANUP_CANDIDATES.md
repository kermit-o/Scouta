# CLEANUP_CANDIDATES (solo sugerencias)
- Entornos: .venv/, venv/ (no deben versionarse).
- Caches: __pycache__/, .pytest_cache/, .mypy_cache/.
- Artefactos: *.zip, *.tar, recovered_from_pyc/.
- Secretos: .env (usar .env.example en repo), tokens en código.
- Duplicados de migraciones Alembic o backends paralelos que queden obsoletos.
