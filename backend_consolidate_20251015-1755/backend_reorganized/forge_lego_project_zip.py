from __future__ import annotations

import sys
from pathlib import Path
import zipfile


def build_zip(slug: str) -> Path:
    """
    Crea un ZIP para el proyecto `slug`.

    1) Intenta usar workdir/projects/<slug>
    2) Si no existe, usa workdir/from_requirements como fallback
       (para nuestro demo_ecommerce actual).
    """
    root = Path(__file__).resolve().parent
    projects_root = root / "workdir" / "projects"
    from_req_root = root / "workdir" / "from_requirements"

    project_dir = projects_root / slug
    if not project_dir.exists():
        print(f"[forge_lego_project_zip] WARNING: {project_dir} no existe, usando fallback {from_req_root}")
        project_dir = from_req_root

    if not project_dir.exists():
        raise SystemExit(f"[forge_lego_project_zip] ERROR: {project_dir} no existe, no hay nada que zippear.")

    zips_root = root / "workdir" / "zips"
    zips_root.mkdir(parents=True, exist_ok=True)
    zip_path = zips_root / f"{slug}.zip"

    print(f"[forge_lego_project_zip] Root: {root}")
    print(f"[forge_lego_project_zip] Source dir: {project_dir}")
    print(f"[forge_lego_project_zip] Writing ZIP to: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Metemos los archivos bajo una carpeta raíz con el nombre del slug
        base = project_dir
        for path in base.rglob("*"):
            if path.is_file():
                arcname = Path(slug) / path.relative_to(base)
                zf.write(path, arcname)

    print("[forge_lego_project_zip] Done.")
    return zip_path


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python forge_lego_project_zip.py <project_slug>")

    slug = sys.argv[1]
    build_zip(slug)


if __name__ == "__main__":
    main()
