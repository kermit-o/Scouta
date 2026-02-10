from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader


TEMPLATES_SUBDIR = "lego_backend"


@dataclass
class FieldSpec:
    """Specification for a single model field."""

    name: str
    sqlalchemy_type: str
    type_hint: str
    options: str = ""  # e.g. "nullable=False, index=True"


@dataclass
class ResourceSpec:
    """Specification for a backend resource to generate."""

    model_class_name: str
    table_name: str
    resource_name: str
    resource_name_plural: str
    fields: List[FieldSpec]

    pk_name: str = "id"

    # Import paths for generated modules (relative to the package where they will live)
    model_module: str = "models"
    schemas_module: str = "schemas"
    service_module: str = "services"

    api_prefix: Optional[str] = None
    api_tag: Optional[str] = None

    def resolved_api_prefix(self) -> str:
        return self.api_prefix or f"/{self.resource_name_plural}"

    def resolved_api_tag(self) -> str:
        return self.api_tag or self.resource_name_plural


class LegoBackendGenerator:
    """Generate FastAPI + SQLAlchemy boilerplate from lego_backend templates."""

    def __init__(self, templates_root: Optional[Path] = None) -> None:
        if templates_root is None:
            # backend_reorganized/services -> backend_reorganized/templates/lego_backend
            services_dir = Path(__file__).resolve().parent
            root_dir = services_dir.parent
            templates_root = root_dir / "templates" / TEMPLATES_SUBDIR

        self.templates_root = templates_root
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_root)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_all_for_resource(self, spec: ResourceSpec, output_dir: Path) -> Dict[str, Path]:
        """
        Generate model, schemas, service and router files for a given resource.

        Returns a mapping of logical name -> generated file path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        context_common = {
            "model_class_name": spec.model_class_name,
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

        # --- MODEL ---
        model_context = {
            **context_common,
            "table_name": spec.table_name,
            "extra_imports": "from sqlalchemy import String, Text, Numeric, Boolean",
        }
        model_tpl = self.env.get_template("model_sqlalchemy.py.j2")
        model_path = output_dir / f"models_{spec.resource_name}.py"
        model_path.write_text(model_tpl.render(**model_context), encoding="utf-8")

        # --- SCHEMAS ---
        schema_fields = [
            {"name": f.name, "type_hint": f.type_hint} for f in spec.fields
        ]
        schema_context = {
            "model_class_name": spec.model_class_name,
            "schema_base_name": spec.model_class_name,
            "schema_create_name": f"{spec.model_class_name}Create",
            "schema_update_name": f"{spec.model_class_name}Update",
            "schema_read_name": f"{spec.model_class_name}Read",
            "fields": schema_fields,
            "extra_imports": "",
        }
        schema_tpl = self.env.get_template("schema_pydantic.py.j2")
        schema_path = output_dir / f"schemas_{spec.resource_name}.py"
        schema_path.write_text(schema_tpl.render(**schema_context), encoding="utf-8")

        # --- SERVICE ---
        service_context = {
            "model_module": f"models_{spec.resource_name}",
            "schemas_module": f"schemas_{spec.resource_name}",
            "model_class_name": spec.model_class_name,
            "schema_create_name": f"{spec.model_class_name}Create",
            "schema_update_name": f"{spec.model_class_name}Update",
            "schema_read_name": f"{spec.model_class_name}Read",
            "resource_name": spec.resource_name,
            "resource_name_plural": spec.resource_name_plural,
            "pk_name": spec.pk_name,
        }
        service_tpl = self.env.get_template("service_crud.py.j2")
        service_path = output_dir / f"services_{spec.resource_name}.py"
        service_path.write_text(service_tpl.render(**service_context), encoding="utf-8")

        # --- ROUTER ---
        router_context = {
            "schemas_module": f"schemas_{spec.resource_name}",
            "service_module": f"services_{spec.resource_name}",
            "model_class_name": spec.model_class_name,
            "schema_create_name": f"{spec.model_class_name}Create",
            "schema_update_name": f"{spec.model_class_name}Update",
            "schema_read_name": f"{spec.model_class_name}Read",
            "resource_name": spec.resource_name,
            "resource_name_plural": spec.resource_name_plural,
            "pk_name": spec.pk_name,
            "api_prefix": spec.resolved_api_prefix(),
            "api_tag": spec.resolved_api_tag(),
        }
        router_tpl = self.env.get_template("router_crud_fastapi.py.j2")
        router_path = output_dir / f"routers_{spec.resource_name}.py"
        router_path.write_text(router_tpl.render(**router_context), encoding="utf-8")

        return {
            "model": model_path,
            "schemas": schema_path,
            "service": service_path,
            "router": router_path,
        }
