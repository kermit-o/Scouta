from __future__ import annotations
from typing import Dict
import threading

class ProgressTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, Dict] = {}

    def start(self, project_id: str, message: str = "starting") -> None:
        with self._lock:
            self._store[project_id] = {"progress": 0, "status": "running", "message": message}

    def update(self, project_id: str, progress: int, message: str | None = None) -> None:
        with self._lock:
            s = self._store.setdefault(project_id, {"progress": 0, "status": "running", "message": ""})
            s["progress"] = max(0, min(progress, 100))
            if message is not None:
                s["message"] = message

    def complete(self, project_id: str, message: str = "done") -> None:
        with self._lock:
            s = self._store.setdefault(project_id, {})
            s.update({"progress": 100, "status": "done", "message": message})

    def get(self, project_id: str) -> Dict:
        with self._lock:
            return self._store.get(project_id, {"progress": 0, "status": "pending", "message": ""})

_tracker = ProgressTracker()

def get_tracker() -> ProgressTracker:
    return _tracker

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Lightweight helper to suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    from app.modules.registry import list_modules, lookup_module

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions
