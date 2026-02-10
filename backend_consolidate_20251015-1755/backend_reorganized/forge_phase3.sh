#!/usr/bin/env bash

set -e
echo "===> Fase 3: Integración Lego Modules → LegoBackendGenerator"
echo "===> Ejecutando en: $(pwd)"

BASE="backend_reorganized"
MOD_PATH="$BASE/app/modules"
SERV_PATH="$BASE/services"
API_PATH="$BASE/api/v1"

###########################################
# 1. Extender ModuleSpec en specs.py
###########################################
echo "===> Patching specs.py..."

cat > $MOD_PATH/specs.py << 'PYEOF'
from dataclasses import dataclass
from typing import List

@dataclass
class FieldSpec:
    name: str
    sqlalchemy_type: str
    type_hint: str
    options: str = ""

@dataclass
class ResourceSpec:
    model_class_name: str
    table_name: str
    resource_name: str
    resource_name_plural: str
    fields: List[FieldSpec]

@dataclass
class ModuleSpec:
    name: str
    category: str
    tags: List[str]

@dataclass
class ModuleResource:
    """
    Defines one resource that a module can auto-generate.
    """
    resource: ResourceSpec
    output_subdir: str
PYEOF


###########################################
# 2. Registry con soporte module_resources
###########################################
echo "===> Generating new registry..."

cat > $MOD_PATH/registry.py << 'PYEOF'
"""
Central registry for Lego Modules + Resources.
"""

from typing import List, Optional
from .specs import ModuleSpec, ModuleResource
from .core.database.postgresql.module import module_spec as postgres_db_module
from .business.ecommerce.product_catalog.module import (
    module_spec as catalog_module_spec,
    module_resources as catalog_resources
)

modules = [
    postgres_db_module,
    catalog_module_spec,
]

resources_by_module = {
    "business.ecommerce.product_catalog": catalog_resources,
}

def list_modules() -> List[ModuleSpec]:
    return modules

def lookup_module(name: str) -> Optional[ModuleSpec]:
    return next((m for m in modules if m.name == name), None)

def get_module_resources(name: str) -> List[ModuleResource]:
    return resources_by_module.get(name, [])
PYEOF


###########################################
# 3. Crear lego_module_executor.py
###########################################
echo "===> Creating lego_module_executor.py..."

cat > $SERV_PATH/lego_module_executor.py << 'PYEOF'
from pathlib import Path
from typing import List

from app.modules.registry import (
    lookup_module,
    get_module_resources,
)
from services.lego_backend_service import LegoBackendGenerator

def generate_from_module(module_name: str, output_dir: Path) -> List[dict]:
    """
    Generates all resources defined under a module.
    """
    module = lookup_module(module_name)
    if not module:
        raise ValueError(f"Module '{module_name}' not found.")

    resources = get_module_resources(module_name)

    gen = LegoBackendGenerator()
    results = []

    for mr in resources:
        subdir = output_dir / mr.output_subdir
        subdir.mkdir(parents=True, exist_ok=True)
        result = gen.generate(mr.resource, subdir)
        results.append(result)

    return results
PYEOF


###########################################
# 4. Añadir Router /api/forge/generate_from_module
###########################################
echo "===> Creating API endpoint generate_from_module..."

cat > $API_PATH/lego_backend_modules.py << 'PYEOF'
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.lego_module_executor import generate_from_module

router = APIRouter(prefix="/forge", tags=["forge-modules"])

class ModuleRequest(BaseModel):
    module_name: str

@router.post("/generate_from_module")
def generate_from_module_api(payload: ModuleRequest):
    try:
        base = Path("backend_reorganized/workdir/from_modules")
        base.mkdir(parents=True, exist_ok=True)
        results = generate_from_module(payload.module_name, base)
        return {"module": payload.module_name, "generated": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
PYEOF


###########################################
# 5. Registrar nuevo router en main_forge.py
###########################################
echo "===> Adding new router to app/main_forge.py..."

sed -i '/lego_backend.router/a \ \ \ ,lego_backend_modules.router' \
    $BASE/app/main_forge.py 2>/dev/null || true


###########################################
# 6. Smoke test automático
###########################################
echo "===> Creating smoke test file..."

cat > smoke_test_phase3.py << 'PYEOF'
from pathlib import Path
from services.lego_module_executor import generate_from_module

print("===> SMOKE TEST: module generation (business.ecommerce.product_catalog)")
output = generate_from_module("business.ecommerce.product_catalog", Path("test_outputs"))
print(output)
PYEOF

echo "===> DONE. Ejecuta:"
echo "     1) uvicorn app.main_forge:app --port 8000 --reload"
echo "     2) curl -X POST http://localhost:8000/api/forge/generate_from_module -H 'Content-Type: application/json' -d '{\"module_name\": \"business.ecommerce.product_catalog\"}'"
