from typing import Dict, Tuple

def generate_plan(requirements: Dict) -> Tuple[Dict, Dict, Dict]:
    """Devuelve (plan_json, technology_stack, generated_plan[resumen])."""
    features = requirements.get("features", [])
    entities = requirements.get("entities", [{"name": "Project", "fields": [{"name":"id","type":"uuid"},{"name":"name","type":"string"}]}])

    plan = {
        "epics": [
            {"name": "Projects CRUD", "stories": ["Create project", "List projects", "Update requirements"]},
            {"name": "Planning", "stories": ["Generate plan", "Show plan in UI"]},
            {"name": "Build & Package", "stories": ["Codegen skeleton", "Zip artifact"]},
        ],
        "api": [
            {"path": "/api/projects", "methods": ["GET", "POST"]},
            {"path": "/api/projects/{id}", "methods": ["GET"]},
            {"path": "/api/projects/{id}/requirements", "methods": ["POST"]},
            {"path": "/api/projects/{id}/plan", "methods": ["POST"]},
            {"path": "/api/projects/{id}/build", "methods": ["POST"]},
            {"path": "/api/projects/{id}/artifact", "methods": ["GET"]},
        ],
        "entities": entities,
        "features": features,
    }

    stack = {
        "backend": {"framework": "FastAPI", "db": "PostgreSQL", "orm": "SQLAlchemy", "migrations": "Alembic"},
        "ui": {"framework": "Streamlit"},
        "devops": {"docker": True, "compose": True}
    }

    resumen = {
        "overview": "Proyecto SaaS mínimo con CRUD de proyectos, planificador y empaquetado.",
        "highlights": ["Plan visible", "Build que genera ZIP", "UI con acciones Plan/Build"],
    }

    return plan, stack, resumen
