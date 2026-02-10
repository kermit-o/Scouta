from __future__ import annotations

from pathlib import Path
from shutil import copytree, make_archive
from typing import List


class ProjectPackagingError(Exception):
    """Raised when a Forge Lego project cannot be materialized from workdir."""


def get_repo_root() -> Path:
    """
    Returns backend_reorganized root.

    This file lives in backend_reorganized/services, so parents[1] is the root.
    """
    return Path(__file__).resolve().parents[1]


def get_workdir_base() -> Path:
    """Base workdir for Lego artifacts."""
    return get_repo_root() / "workdir"


def ensure_project_dir(slug: str) -> Path:
    """
    Ensure workdir/projects/<slug>/backend exists and return the project root dir.
    """
    workdir = get_workdir_base()
    project_dir = workdir / "projects" / slug
    backend_dir = project_dir / "backend"

    backend_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def collect_lego_sources() -> List[Path]:
    """
    Collect top-level Lego-generated directories under:

      - workdir/from_requirements
      - workdir/from_modules
    """
    base = get_workdir_base()
    sources: List[Path] = []

    for sub in ("from_requirements", "from_modules"):
        subdir = base / sub
        if not subdir.exists():
            continue
        for child in subdir.iterdir():
            if child.is_dir():
                sources.append(child)

    return sources


def materialize_project_from_lego(slug: str) -> Path:
    """
    Build a minimal project structure under workdir/projects/<slug> from Lego artifacts.

    Current layout:

      workdir/projects/<slug>/
        backend/
          lego_generated/
            <all dirs from workdir/from_requirements and workdir/from_modules>
        README.md
    """
    project_dir = ensure_project_dir(slug)
    backend_generated = project_dir / "backend" / "lego_generated"
    backend_generated.mkdir(parents=True, exist_ok=True)

    sources = collect_lego_sources()
    if not sources:
        raise ProjectPackagingError("No Lego-generated sources found under workdir.")

    for src in sources:
        dest = backend_generated / src.name
        # Do not overwrite existing trees (idempotent packaging).
        if dest.exists():
            continue
        copytree(src, dest)

    readme = project_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# Forge demo project: {slug}\n\n"
            "This project was generated from Lego modules under `workdir/`.\n"
            "\n"
            "Structure:\n"
            "- backend/lego_generated/: auto-generated FastAPI resources (models/schemas/services/routers).\n",
            encoding="utf-8",
        )

    return project_dir


def ensure_project_zip(slug: str) -> Path:
    """
    Ensure there is a ZIP for the given project slug and return its path.

    If the ZIP does not exist, materialize the project structure and create it.
    """
    workdir = get_workdir_base()
    zip_dir = workdir / "zips"
    zip_dir.mkdir(parents=True, exist_ok=True)

    zip_path = zip_dir / f"{slug}.zip"
    if zip_path.exists():
        return zip_path

    project_dir = materialize_project_from_lego(slug)

    # shutil.make_archive expects the base name WITHOUT .zip
    base_name = zip_path.with_suffix("")
    make_archive(str(base_name), "zip", project_dir)

    return zip_path
