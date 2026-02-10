from typing import Dict, List

from fastapi import APIRouter

from app.modules.registry import list_modules
from services.lego_module_executor import MODULE_RESOURCES

router = APIRouter(prefix="/forge", tags=["forge-lego-status"])


@router.get("/modules")
def get_lego_modules() -> List[dict]:
    """
    List all Lego modules registered in the central registry.
    """
    mods = list_modules()
    return [
        {
            "name": m.name,
            "category": m.category,
            "tags": list(m.tags),
            "required_env": list(m.required_env),
            "description": getattr(m, "description", ""),
        }
        for m in mods
    ]


@router.get("/module_resources")
def get_module_resources() -> Dict[str, List[dict]]:
    """
    List the resources (models/endpoints) that each module will generate.
    """
    output: Dict[str, List[dict]] = {}
    for module_name, specs in MODULE_RESOURCES.items():
        output[module_name] = []
        for spec in specs:
            output[module_name].append(
                {
                    "model_class_name": spec.model_class_name,
                    "table_name": spec.table_name,
                    "resource_name": spec.resource_name,
                    "resource_name_plural": spec.resource_name_plural,
                    "fields": [
                        {
                            "name": f.name,
                            "sqlalchemy_type": f.sqlalchemy_type,
                            "type_hint": f.type_hint,
                            "options": f.options,
                        }
                        for f in spec.fields
                    ],
                }
            )
    return output
