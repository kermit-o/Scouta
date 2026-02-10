from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.routing import APIRouter


BASE_DIR = Path(__file__).resolve().parent.parent  # backend_reorganized/
GENERATED_ROOTS = [
    BASE_DIR / "workdir" / "from_requirements",
    BASE_DIR / "workdir" / "from_modules",
]


def _find_router_files() -> List[Path]:
    """Return all routers_*.py files under known generated roots."""
    files: List[Path] = []
    for root in GENERATED_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("routers_*.py"):
            if path.is_file():
                files.append(path)
    return files


def _load_router_from_file(path: Path) -> APIRouter | None:
    """
    Dynamically import a module from path and return its 'router' if present.

    To support imports like 'from schemas_x import ...' that live next to the router,
    we temporarily add the router's directory to sys.path during import.
    """
    module_name = f"generated_{path.stem}_{abs(hash(str(path))) % 10**8}"
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None

    module_dir = str(path.parent)
    added = False
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        added = True

    try:
        module = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[arg-type]
    except ModuleNotFoundError as exc:
        # Si falla un import interno (schemas_*, services_*, etc.), simplemente
        # ignoramos este router para no tumbar toda la app.
        print(f"[lego_runtime_loader] Skipping router {path} due to import error: {exc}")
        return None
    finally:
        if added:
            try:
                sys.path.remove(module_dir)
            except ValueError:
                pass

    router = getattr(module, "router", None)
    if isinstance(router, APIRouter):
        return router
    return None


def include_generated_routers(app: FastAPI, base_prefix: str = "/api") -> List[str]:
    """
    Discover and mount all generated routers into the FastAPI app.

    Returns a list of file paths from which routers were successfully mounted.
    """
    mounted: List[str] = []
    for path in _find_router_files():
        router = _load_router_from_file(path)
        if not router:
            continue

        app.include_router(router, prefix=base_prefix)
        mounted.append(str(path))

    if mounted:
        print("[lego_runtime_loader] Mounted routers from:")
        for m in mounted:
            print("  -", m)

    return mounted
