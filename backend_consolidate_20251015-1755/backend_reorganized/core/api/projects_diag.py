from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List, Dict, Any
from core import settings

router = APIRouter(prefix="/api/projects/diagnostics", tags=["projects-diagnostics"])

@router.get("/latest-artifact")
def latest_artifact() -> Dict[str, Any]:
    delivery = settings.ARTIFACT_ROOT / "delivery"
    zips = sorted(delivery.glob("SAAS_Forge_Project_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not zips:
        raise HTTPException(status_code=404, detail="No artifacts found")
    zp = zips[0]
    # Resumen de contenidos
    from zipfile import ZipFile
    with ZipFile(zp, "r") as zf:
        files = [{"name": i.filename, "size": i.file_size} for i in zf.infolist()]
    return {
        "path": str(zp),
        "filename": zp.name,
        "size_bytes": zp.stat().st_size,
        "files": files
    }

@router.get("/artifacts")
def list_artifacts() -> List[Dict[str, Any]]:
    delivery = settings.ARTIFACT_ROOT / "delivery"
    zips = sorted(delivery.glob("SAAS_Forge_Project_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for zp in zips:
        out.append({
            "path": str(zp),
            "filename": zp.name,
            "size_bytes": zp.stat().st_size,
            "mtime": zp.stat().st_mtime,
        })
    return out
