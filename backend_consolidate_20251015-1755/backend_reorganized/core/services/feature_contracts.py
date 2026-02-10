# core/services/feature_contracts.py
from __future__ import annotations
from typing import Dict, List

# ---- Base mínima siempre presente en cualquier backend FastAPI generado
_BASE_PATHS: List[str] = [
    "README.md",
    "backend/app/requirements.txt",
    "backend/app/main.py",
    "backend/app/routers/health.py",
]

# ---- Rutas/archivos por feature (contrato mínimo)
_FEATURE_PATHS: Dict[str, List[str]] = {
    "FastAPI": [],  # ya cubierto por _BASE_PATHS
    "health": [],   # ya cubierto por routers/health.py

    # CRUD de usuarios (estructura completa)
    "users_crud": [
        "backend/app/routers/users.py",
        "backend/app/models.py",
        "backend/app/schemas.py",
        "backend/app/db.py",
    ],

    # DB + migraciones
    "postgres": [
        "alembic.ini",
        "alembic/env.py",
        "alembic/versions/0001_init.py",
    ],
    "alembic": [
        "alembic.ini",
        "alembic/env.py",
        "alembic/versions/0001_init.py",
    ],

    # Contenedores
    "Dockerfile": [
        "Dockerfile",
    ],
    "docker_compose": [
        "docker-compose.yml",
    ],
}

# ---- Prompts (plantillas guía) por feature para el generador LLM
_GEN_PROMPTS: Dict[str, str] = {
    "users_crud": """
Create a FastAPI CRUD for a User entity:
- File: backend/app/routers/users.py (prefix `/api/users`)
- Model: backend/app/models.py (SQLAlchemy, fields: id UUID, name, email unique, created_at datetime)
- Schema: backend/app/schemas.py (Pydantic BaseModel)
- DB: backend/app/db.py (SessionLocal, engine, Base, get_db dependency)
Routes: list users, get by id, create, update, delete. 
Use dependency injection with get_db and return JSON responses (status 200/404/400).
""",

    "postgres": """
Provide Alembic setup for PostgreSQL:
- Files: alembic.ini, alembic/env.py, alembic/versions/0001_init.py
- Configure URL using DATABASE_URL from environment.
""",

    "alembic": """
Initialize Alembic migration structure for SQLAlchemy models.
Include env.py and initial migration script (0001_init.py).
""",

    "Dockerfile": """
Produce a Dockerfile for FastAPI + Uvicorn in production.
Use python:3.12-slim base, copy backend/app, install requirements, expose port 8000.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    "docker_compose": """
Generate docker-compose.yml wiring FastAPI app and PostgreSQL:
- Service app: build from ., ports 8000:8000, depends_on db
- Service db: image postgres:16, environment POSTGRES_USER/PASSWORD/DB
- Volumes: pgdata:/var/lib/postgresql/data
""",
}


def feature_required_paths(features: List[str]) -> List[str]:
    """Devuelve la lista de rutas requeridas por el conjunto de features."""
    paths: List[str] = list(_BASE_PATHS)
    for f in features:
        extra = _FEATURE_PATHS.get(f, [])
        for p in extra:
            if p not in paths:
                paths.append(p)
    return paths


def feature_gen_prompt(name: str) -> str:
    """Devuelve el prompt LLM asociado a un feature (si existe)."""
    return _GEN_PROMPTS.get(name, "")


# ---- Aliases de compatibilidad (para imports antiguos)
REQUIRED_FILES: Dict[str, List[str]] = _FEATURE_PATHS
GEN_PROMPTS: Dict[str, str] = _GEN_PROMPTS

def enforce_feature_contract(plan: dict) -> dict:
    """Ensure plan['structure'] contains all required paths for its features."""
    try:
        feats = plan.get("features", [])
        reqs = feature_required_paths(feats)
        existing = { (x or {}).get("path") for x in plan.get("structure", []) }
        for path in reqs:
            if path not in existing:
                plan.setdefault("structure", []).append({"path": path})
        return plan
    except Exception as e:
        print(f"[WARN] feature contract enforcement failed: {e}")
        return plan

