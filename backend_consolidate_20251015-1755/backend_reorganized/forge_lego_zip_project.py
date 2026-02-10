from __future__ import annotations

from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).parent
GENERATED_ROOT = ROOT / "generated_projects"
ZIPS_ROOT = ROOT / "workdir" / "zips"


def zip_project(slug: str) -> Path:
    """
    Empaqueta generated_projects/<slug> en workdir/zips/<slug>.zip.
    No modifica el contenido del proyecto, solo lo comprime.
    """
    project_dir = GENERATED_ROOT / slug

    if not project_dir.exists():
        raise SystemExit(
            f"[forge_lego_zip_project] ERROR: no existe {project_dir}. "
            "Asegúrate de haber ejecutado antes forge_lego_pack_project.py."
        )

    ZIPS_ROOT.mkdir(parents=True, exist_ok=True)

    # Ruta base del ZIP (sin extensión) para make_archive
    zip_base = ZIPS_ROOT / slug

    # shutil.make_archive añade la extensión automáticamente
    archive_path = shutil.make_archive(
        base_name=str(zip_base),
        format="zip",
        root_dir=str(project_dir.parent),
        base_dir=project_dir.name,
    )

    return Path(archive_path)


def main() -> None:
    if len(sys.argv) > 1:
        slug = sys.argv[1]
    else:
        slug = "demo_ecommerce"

    print(f"[forge_lego_zip_project] ROOT: {ROOT}")
    print(f"[forge_lego_zip_project] Proyecto: {slug}")

    archive = zip_project(slug)
    print(f"[forge_lego_zip_project] ZIP creado en: {archive}")


if __name__ == "__main__":
    main()
