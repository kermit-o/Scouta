from app.modules.specs import ModuleSpec


# Ecommerce product catalog module specification
module_spec = ModuleSpec(
    name="business.ecommerce.product_catalog",
    category="business",
    tags=[
        "ecommerce",
        "products",
        "catalog",
        "categories",
        "listings",
    ],
    required_env=[
        # Normally nothing special beyond DB, but we keep this explicit
        # in case we later need search backends, feature flags, etc.
    ],
    description=(
        "Business module for managing an ecommerce product catalog: "
        "products, categories, pricing fields and basic CRUD operations. "
        "Intended to be combined with shopping_cart, order_management and "
        "integrations.payment_gateways.* modules."
    ),
)
