from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from services import planner_service

router = APIRouter(
    prefix="/forge",
    tags=["forge-planner"],
)


class RequirementsRequest(BaseModel):
    requirements_text: str


@router.post("/generate_from_requirements")
def generate_from_requirements_api(payload: RequirementsRequest) -> Dict[str, Any]:
    """
    From a free-text description of requirements, suggest modules and generate
    backend artifacts (models/schemas/services/routers).
    """
    results = planner_service.generate_from_requirements(payload.requirements_text)
    return {
        "requirements_text": payload.requirements_text,
        "generated": results,
    }

# --- Download generated project ZIP by slug ---


@router.get("/projects/{slug}/download")
def download_project_zip(slug: str):
    """
    Download a generated project ZIP from workdir/zips/<slug>.zip.

    Example:
      GET /api/forge/projects/demo_ecommerce/download
    """
    from pathlib import Path
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    root = Path(__file__).resolve().parents[1]  # backend_reorganized/
    zips_dir = root / "workdir" / "zips"
    zip_path = zips_dir / f"{slug}.zip"

    if not zip_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"ZIP for project '{slug}' not found. Expected at {zip_path}",
        )

    return FileResponse(
        path=zip_path,
        filename=f"{slug}.zip",
        media_type="application/zip",
    )
