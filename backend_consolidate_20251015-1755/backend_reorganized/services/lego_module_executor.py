from pathlib import Path
from typing import Any, Dict, List

from app.modules.registry import lookup_module
from services.lego_backend_service import FieldSpec, ResourceSpec, LegoBackendGenerator


# Mapping from module name -> list of ResourceSpec that should be generated.
MODULE_RESOURCES: Dict[str, List[ResourceSpec]] = {
    # --- Catálogo de productos ----------------------------------------------
    "business.ecommerce.product_catalog": [
        ResourceSpec(
            model_class_name="Product",
            table_name="products",
            resource_name="product",
            resource_name_plural="products",
            fields=[
                FieldSpec(
                    name="name",
                    sqlalchemy_type="String(255)",
                    type_hint="str",
                    options="nullable=False, index=True",
                ),
                FieldSpec(
                    name="description",
                    sqlalchemy_type="Text",
                    type_hint="str | None",
                    options="nullable=True",
                ),
                FieldSpec(
                    name="price",
                    sqlalchemy_type="Numeric(10, 2)",
                    type_hint="float",
                    options="nullable=False",
                ),
                FieldSpec(
                    name="is_active",
                    sqlalchemy_type="Boolean",
                    type_hint="bool",
                    options="nullable=False, server_default='1'",
                ),
            ],
        ),
    ],

    # --- Gestión de pedidos (orders) ----------------------------------------
    "business.ecommerce.order_management": [
        ResourceSpec(
            model_class_name="Order",
            table_name="orders",
            resource_name="order",
            resource_name_plural="orders",
            fields=[
                FieldSpec(
                    name="reference",
                    sqlalchemy_type="String(50)",
                    type_hint="str",
                    options="nullable=False, index=True",
                ),
                FieldSpec(
                    name="total_amount",
                    sqlalchemy_type="Numeric(10, 2)",
                    type_hint="float",
                    options="nullable=False",
                ),
                FieldSpec(
                    name="status",
                    sqlalchemy_type="String(32)",
                    type_hint="str",
                    options="nullable=False, server_default=\"'pending'\"",
                ),
            ],
        ),
    ],

    # --- Core auth: Users ----------------------------------------------------
    "core.auth.users": [
        ResourceSpec(
            model_class_name="User",
            table_name="users",
            resource_name="user",
            resource_name_plural="users",
            fields=[
                FieldSpec(
                    name="email",
                    sqlalchemy_type="String(255)",
                    type_hint="str",
                    options="nullable=False, unique=True, index=True",
                ),
                FieldSpec(
                    name="password_hash",
                    sqlalchemy_type="String(255)",
                    type_hint="str",
                    options="nullable=False",
                ),
                FieldSpec(
                    name="full_name",
                    sqlalchemy_type="String(255)",
                    type_hint="str | None",
                    options="nullable=True",
                ),
                FieldSpec(
                    name="is_active",
                    sqlalchemy_type="Boolean",
                    type_hint="bool",
                    options="nullable=False, server_default='1'",
                ),
            ],
        ),
    ],
}


def list_module_resources() -> Dict[str, List[ResourceSpec]]:
    """Return the mapping of module -> resource specs."""
    return MODULE_RESOURCES


def generate_from_module(
    module_name: str,
    output_root: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate backend artifacts (models/schemas/services/routers) for a module.

    Returns a list of dicts with:
      - module
      - resource_name
      - output_dir
      - files (paths as strings)
    """
    module_spec = lookup_module(module_name)
    if not module_spec and module_name not in MODULE_RESOURCES:
        raise ValueError(
            f"Module '{module_name}' not found in registry or MODULE_RESOURCES."
        )

    # Carpeta base donde se escriben los recursos generados
    base = Path(output_root or "workdir/from_modules") / module_name.replace(".", "_")
    base.mkdir(parents=True, exist_ok=True)

    # 📌 Directorio de plantillas Lego backend (donde está model_sqlalchemy.py.j2, etc.)
    # __file__ -> .../backend_reorganized/services/lego_module_executor.py
    # parents[1] -> .../backend_reorganized
    templates_root = Path(__file__).resolve().parents[1] / "templates" / "lego_backend"

    # LegoBackendGenerator espera primero el directorio de plantillas
    # y luego el "root" de trabajo/salida (base).
    generator = LegoBackendGenerator(templates_root, base)

    results: List[Dict[str, Any]] = []

    for res in MODULE_RESOURCES.get(module_name, []):
        # Cada recurso va en su subcarpeta: products/, orders/, users/, etc.
        out_dir = base / res.resource_name_plural
        out_dir.mkdir(parents=True, exist_ok=True)

        # IMPORTANTE: generate_all_for_resource espera (spec, output_dir)
        paths = generator.generate_all_for_resource(res, out_dir)

        results.append(
            {
                "module": module_name,
                "resource_name": res.resource_name,
                "output_dir": str(out_dir),
                "files": {key: str(path) for key, path in paths.items()},
            }
        )

    return results
