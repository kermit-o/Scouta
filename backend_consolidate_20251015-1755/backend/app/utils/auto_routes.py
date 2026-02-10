# app/utils/auto_routes.py
import importlib
import pkgutil
from types import ModuleType
from typing import Optional, Set
from fastapi import APIRouter, FastAPI

def _iter_modules(pkg: ModuleType):
    """Yield submodules of a package recursively."""
    if not hasattr(pkg, "__path__"):
        return
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        yield m.name

def include_routers(
    app: FastAPI,
    package: ModuleType,
    base_prefix: str = "",
    exclude_modules: Optional[Set[str]] = None,
):
    """
    Busca objetos `router` (APIRouter) dentro de todos los submódulos del paquete
    y los monta en la app con el `base_prefix` dado, evitando duplicados.
    """
    exclude_modules = exclude_modules or set()
    mounted: Set[str] = set()

    for mod_name in _iter_modules(package):
        if any(mod_name == ex or mod_name.startswith(ex + ".") for ex in exclude_modules):
            continue
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue

        router = getattr(mod, "router", None)
        if isinstance(router, APIRouter):
            key = f"{mod_name}"
            if key in mounted:
                continue
            # Monta con base_prefix (ej. "/api")
            app.include_router(router, prefix=base_prefix)
            mounted.add(key)
