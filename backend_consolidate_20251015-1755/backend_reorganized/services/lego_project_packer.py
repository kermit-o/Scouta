from __future__ import annotations

import shutil
from pathlib import Path


def _get_root() -> Path:
    """
    Returns the backend root directory (where app/, services/, workdir/ live).
    """
    return Path(__file__).resolve().parent


def build_demo_ecommerce_zip() -> Path:
    """
    Empaqueta el contenido de workdir/from_requirements en
    generated_projects/demo_ecommerce.zip.

    Fase 1 (MVP):
      - No intentamos re-estructurar los ficheros.
      - Simplemente zipeamos todo lo que haya en from_requirements.
    """
    root = _get_root()
    src = root / "workdir" / "from_requirements"
    if not src.exists():
        raise FileNotFoundError(
            f"[lego_project_packer] Source directory not found: {src}"
        )

    # Crear carpeta destino
    out_dir = root / "generated_projects"
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_base = out_dir / "demo_ecommerce"  # -> demo_ecommerce.zip
    zip_path_str = shutil.make_archive(str(zip_base), "zip", root_dir=src)
    zip_path = Path(zip_path_str)

    print(f"[lego_project_packer] Created ZIP at: {zip_path}")
    return zip_path
