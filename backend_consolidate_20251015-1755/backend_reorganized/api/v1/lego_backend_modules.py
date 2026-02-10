from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.lego_module_executor import generate_from_module

router = APIRouter(
    prefix="/forge",
    tags=["forge-modules"],
)


class ModuleRequest(BaseModel):
    module_name: str


@router.post("/generate_from_module")
def generate_from_module_api(payload: ModuleRequest) -> Dict[str, Any]:
    """
    Generate all resources associated with a Lego module.

    Example payload:
    {
        "module_name": "business.ecommerce.product_catalog"
    }
    """
    base = Path("workdir") / "from_modules"
    try:
        base.mkdir(parents=True, exist_ok=True)
        results = generate_from_module(payload.module_name, base)
        return {"module": payload.module_name, "generated": results}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # generic safety guard
        raise HTTPException(status_code=400, detail=str(exc))
