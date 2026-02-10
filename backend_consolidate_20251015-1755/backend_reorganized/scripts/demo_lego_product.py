import os
from jinja2 import Environment, FileSystemLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates", "lego_backend")
OUTPUT_DIR = os.path.join(ROOT_DIR, "workdir", "lego_demo_product")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # --- Domain definition for Product ---
    fields = [
        {
            "name": "name",
            "sqlalchemy_type": "String(255)",
            "options": "nullable=False, index=True",
            "type_hint": "str",
        },
        {
            "name": "description",
            "sqlalchemy_type": "Text",
            "options": "nullable=True",
            "type_hint": "str | None",
        },
        {
            "name": "price",
            "sqlalchemy_type": "Numeric(10, 2)",
            "options": "nullable=False",
            "type_hint": "float",
        },
        {
            "name": "is_active",
            "sqlalchemy_type": "Boolean",
            "options": "nullable=False, server_default='1'",
            "type_hint": "bool",
        },
    ]

    # --- MODEL ---
    model_context = {
        "model_class_name": "Product",
        "table_name": "products",
        "fields": fields,
        "extra_imports": "from sqlalchemy import String, Text, Numeric, Boolean",
    }

    model_tpl = env.get_template("model_sqlalchemy.py.j2")
    model_path = os.path.join(OUTPUT_DIR, "models_product.py")
    with open(model_path, "w", encoding="utf-8") as f:
        f.write(model_tpl.render(**model_context))

    # --- SCHEMAS ---
    schema_fields = [
        {"name": f["name"], "type_hint": f["type_hint"]} for f in fields
    ]
    schema_context = {
        "model_class_name": "Product",
        "schema_base_name": "Product",
        "schema_create_name": "ProductCreate",
        "schema_update_name": "ProductUpdate",
        "schema_read_name": "ProductRead",
        "fields": schema_fields,
        "extra_imports": "",
    }

    schema_tpl = env.get_template("schema_pydantic.py.j2")
    schema_path = os.path.join(OUTPUT_DIR, "schemas_product.py")
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(schema_tpl.render(**schema_context))

    # --- SERVICE ---
    service_context = {
        "model_module": "models_product",
        "schemas_module": "schemas_product",
        "model_class_name": "Product",
        "schema_create_name": "ProductCreate",
        "schema_update_name": "ProductUpdate",
        "schema_read_name": "ProductRead",
        "resource_name": "product",
        "resource_name_plural": "products",
        "pk_name": "id",
    }

    service_tpl = env.get_template("service_crud.py.j2")
    service_path = os.path.join(OUTPUT_DIR, "services_product.py")
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(service_tpl.render(**service_context))

    # --- ROUTER ---
    router_context = {
        "schemas_module": "schemas_product",
        "service_module": "services_product",
        "model_class_name": "Product",
        "schema_create_name": "ProductCreate",
        "schema_update_name": "ProductUpdate",
        "schema_read_name": "ProductRead",
        "resource_name": "product",
        "resource_name_plural": "products",
        "pk_name": "id",
        "api_prefix": "/products",
        "api_tag": "products",
    }

    router_tpl = env.get_template("router_crud_fastapi.py.j2")
    router_path = os.path.join(OUTPUT_DIR, "routers_product.py")
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(router_tpl.render(**router_context))

    print("Generated files in:", OUTPUT_DIR)
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        print(" -", filename)


if __name__ == "__main__":
    main()
