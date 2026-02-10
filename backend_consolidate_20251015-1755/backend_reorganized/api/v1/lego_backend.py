from pathlib import Path
from typing import List, Optional, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.lego_backend_service import (
    FieldSpec,
    ResourceSpec,
    LegoBackendGenerator,
)

router = APIRouter(
    prefix="/forge",
    tags=["forge-lego"],
)


class FieldSpecIn(BaseModel):
    """Input specification for a single field."""

    name: str
    sqlalchemy_type: str
    type_hint: str
    options: Optional[str] = ""


class ResourceSpecIn(BaseModel):
    """Input specification for a backend resource."""

    model_class_name: str
    table_name: str
    resource_name: str
    resource_name_plural: str
    fields: List[FieldSpecIn]

    pk_name: str = "id"
    api_prefix: Optional[str] = None
    api_tag: Optional[str] = None


@router.post("/generate_resource")
def generate_resource(spec_in: ResourceSpecIn) -> Dict[str, object]:
    """
    Generate backend artifacts (model/schemas/service/router)
    for a given resource using the LegoBackendGenerator.

    The generated files are written under:

        backend_reorganized/workdir/lego_resources/<resource_name>/
    """
    if not spec_in.fields:
        raise HTTPException(status_code=400, detail="At least one field is required.")

    # backend_reorganized/api/v1/lego_backend.py -> backend_reorganized/
    root_dir = Path(__file__).resolve().parents[2]
    output_dir = root_dir / "workdir" / "lego_resources" / spec_in.resource_name

    # Map input models to dataclasses used by the generator
    fields = [
        FieldSpec(
            name=f.name,
            sqlalchemy_type=f.sqlalchemy_type,
            type_hint=f.type_hint,
            options=f.options or "",
        )
        for f in spec_in.fields
    ]

    spec = ResourceSpec(
        model_class_name=spec_in.model_class_name,
        table_name=spec_in.table_name,
        resource_name=spec_in.resource_name,
        resource_name_plural=spec_in.resource_name_plural,
        fields=fields,
        pk_name=spec_in.pk_name,
        api_prefix=spec_in.api_prefix,
        api_tag=spec_in.api_tag,
    )

    generator = LegoBackendGenerator()
    result_paths = generator.generate_all_for_resource(spec, output_dir)

    return {
        "resource_name": spec.resource_name,
        "table_name": spec.table_name,
        "api_prefix": spec.resolved_api_prefix(),
        "api_tag": spec.resolved_api_tag(),
        "output_dir": str(output_dir),
        "files": {key: str(path) for key, path in result_paths.items()},
    }
