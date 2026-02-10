from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/forge",
    tags=["forge-projects"],
)


def _candidate_zip_paths(slug: str) -> list[Path]:
    """
    Devuelve posibles rutas donde podría estar el ZIP del proyecto.

    Este archivo está en:
      backend_reorganized/api/v1/lego_projects.py

    parents[0] -> .../backend_reorganized/api/v1
    parents[1] -> .../backend_reorganized/api
    parents[2] -> .../backend_reorganized   <- raíz del backend
    """
    root = Path(__file__).resolve().parents[2]

    paths = [
        root / "workdir" / "zips" / f"{slug}.zip",              # ruta actual
        root / "api" / "workdir" / "zips" / f"{slug}.zip",      # ruta antigua (fallback)
    ]

    print(f"[lego_projects] Candidate paths for '{slug}':")
    for p in paths:
        print(f"  - {p}")
    return paths


@router.get("/projects/{slug}/download")
def download_project(slug: str) -> FileResponse:
    """
    Devuelve el ZIP del proyecto si existe en alguna de las rutas candidatas.
    """
    candidates = _candidate_zip_paths(slug)

    for path in candidates:
        if path.exists():
            print(f"[lego_projects] Using ZIP for '{slug}': {path}")
            return FileResponse(
                path=path,
                media_type="application/zip",
                filename=f"{slug}.zip",
            )

    # Si no encontramos nada, devolvemos 404 con info de depuración
    details = " | ".join(str(p) for p in candidates)
    raise HTTPException(
        status_code=404,
        detail=f"ZIP for project '{slug}' not found. Checked: {details}",
    )
