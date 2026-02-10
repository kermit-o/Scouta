from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from core.database.database import Base  # ya lo usan los modelos

# Intentar obtener un engine reutilizable
try:
    from core.database.database import engine  # type: ignore
except Exception as exc:  # pragma: no cover - fallback
    engine = None
    print(f"[forge_lego_sync_db] WARNING: no se pudo importar 'engine' directamente: {exc}")


def _load_generated_models(root: Path) -> int:
    """
    Importa todos los models_*.py generados bajo 'workdir' para que sus
    clases se registren en Base.metadata.
    """
    workdir = root / "workdir"
    if not workdir.exists():
        print(f"[forge_lego_sync_db] No existe workdir en: {workdir}")
        return 0

    count = 0
    for path in workdir.rglob("models_*.py"):
        # Evitamos cosas raras tipo backups
        if path.name.startswith("._"):
            continue

        module_name = path.stem  # p.ej. models_product
        spec = spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            print(f"[forge_lego_sync_db] No se pudo crear spec para: {path}")
            continue

        module = module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore[call-arg]
        count += 1
        print(f"[forge_lego_sync_db] Cargado módulo de modelos: {path}")

    return count


def main() -> None:
    root = Path(__file__).parent
    print(f"[forge_lego_sync_db] Root: {root}")

    loaded = _load_generated_models(root)
    print(f"[forge_lego_sync_db] Módulos de modelos cargados: {loaded}")

    if loaded == 0:
        print("[forge_lego_sync_db] Nada que sincronizar (no hay models_*.py).")
        return

    global engine
    if engine is None:
        # Intento tardío de obtener un engine si no lo tuvimos arriba
        try:
            from core.database.database import get_engine  # type: ignore
        except Exception as exc:  # pragma: no cover
            print(
                "[forge_lego_sync_db] ERROR: no encontré ni 'engine' ni 'get_engine' "
                f"en core.database.database: {exc}"
            )
            return
        engine = get_engine()

    print("[forge_lego_sync_db] Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("[forge_lego_sync_db] Tablas creadas. Lista actual de tablas:")
    for name in sorted(Base.metadata.tables.keys()):
        print(" -", name)


if __name__ == "__main__":
    main()
