"""
Central registry for Lego Modules.
"""

from typing import List, Optional

from .specs import ModuleSpec
from .core.database.postgresql.module import module_spec as postgres_db_module
from .business.ecommerce.product_catalog.module import module_spec as catalog_module_spec

# --- Virtual/inline specs (no own module.py) --------------------------------

order_module_spec = ModuleSpec(
    name="business.ecommerce.order_management",
    category="business",
    tags=["ecommerce", "orders", "checkout"],
    required_env=[],
    description="Order management resources (Order model, CRUD, router).",
)

users_module_spec = ModuleSpec(
    name="core.auth.users",
    category="core",
    tags=["auth", "users", "identity"],
    required_env=[],
    description="Core user model for authentication and identity. Intended to be combined with sessions/auth modules and business features.",
)

# ---------------------------------------------------------------------------

modules: List[ModuleSpec] = [
    postgres_db_module,
    catalog_module_spec,
    order_module_spec,
    users_module_spec,
]


def list_modules() -> List[ModuleSpec]:
    return modules


def lookup_module(name: str) -> Optional[ModuleSpec]:
    return next((m for m in modules if m.name == name), None)
