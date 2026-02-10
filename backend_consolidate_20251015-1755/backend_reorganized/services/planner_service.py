from time import sleep
from sqlalchemy.orm import Session
from .progress_service import get_tracker
from models.project import Project

def _infer_stack(req: str):
    req_l = (req or "").lower()
    stack = {"frontend": [], "backend": [], "database": []}
    if "flutter" in req_l: stack["frontend"].append("Flutter")
    if "fastapi" in req_l: stack["backend"].append("Python/FastAPI")
    if "flask" in req_l and "Python/FastAPI" not in stack["backend"]: stack["backend"].append("Python/Flask")
    if "postgres" in req_l or "postgresql" in req_l: stack["database"].append("PostgreSQL")
    if not any(stack.values()):
        stack["backend"].append("Python/FastAPI")
        stack["database"].append("PostgreSQL")
    return stack

def plan_project(db: Session, project_id: str):
    tracker = get_tracker()
    tracker.start(project_id, "Validating input")

    proj = db.query(Project).filter(Project.id==project_id, Project.is_deleted==False).first()
    if not proj:
        tracker.update(project_id, 100, "project not found")
        tracker.complete(project_id, "not found")
        return

    steps = [
        ("Validating", 10),
        ("Extracting stack", 30),
        ("Drafting plan", 55),
        ("Generating structure", 70),
        ("Preparing docs", 85),
        ("Finalizing", 100),
    ]

    tech = _infer_stack(proj.requirements or "")
    plan = {
        "entities": ["users", "rooms", "tasks"],
        "endpoints": ["/health", "/rooms", "/tasks"],
        "notes": "MVP skeleton. Expand with auth + sockets in next iteration."
    }

    for msg, pct in steps:
        sleep(0.3)  # simula trabajo
        tracker.update(project_id, pct, msg)

    proj.status = "planned"
    proj.technology_stack = tech
    proj.generated_plan = plan
    db.add(proj)
    db.commit()

    tracker.complete(project_id, "planned")

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Lightweight helper to suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    from app.modules.registry import list_modules, lookup_module

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    from app.modules.registry import list_modules, lookup_module

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    # Relative import: backend_reorganized.services -> ..app.modules.registry
    from ..app.modules.registry import list_modules, lookup_module  # type: ignore

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    # Relative import: backend_reorganized.services -> ..app.modules.registry
    from ..app.modules.registry import list_modules, lookup_module  # type: ignore

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    # backend_reorganized.services.planner_service
    # -> relative import to backend_reorganized.app.modules.registry
    from ..app.modules.registry import list_modules, lookup_module  # type: ignore

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    # Import using absolute package path so it works when backend_reorganized
    # is imported as a top-level package.
    from backend_reorganized.app.modules.registry import list_modules, lookup_module  # type: ignore

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    This does NOT change the existing PlannerService behavior.
    It simply provides a small, reusable mapping from text -> module names
    using the central modules registry.
    """
    # En runtime normal se ejecuta desde backend_reorganized/, así que app es top-level.
    from app.modules.registry import list_modules, lookup_module  # type: ignore

    text = (requirements_text or "").lower()
    suggestions: list[str] = []

    all_modules = list_modules()

    def add_if_exists(module_name: str) -> None:
        if module_name not in suggestions and lookup_module(module_name) is not None:
            suggestions.append(module_name)

    # --- Heuristic 1: ecommerce / tienda / carrito ---
    ecommerce_keywords = ("ecommerce", "e-commerce", "shop", "store", "tienda", "checkout", "cart")
    if any(keyword in text for keyword in ecommerce_keywords):
        for spec in all_modules:
            if any(tag in spec.tags for tag in ("ecommerce", "products", "catalog", "categories", "listings")):
                if spec.name not in suggestions:
                    suggestions.append(spec.name)

    # --- Heuristic 2: base de datos relacional / Postgres ---
    db_keywords = ("postgres", "postgresql", "database", "sql", "relational")
    if any(keyword in text for keyword in db_keywords):
        add_if_exists("core.database.postgresql")

    # --- Fallback: al menos una base de datos por defecto ---
    if not suggestions:
        add_if_exists("core.database.postgresql")

    return suggestions

def generate_from_requirements(requirements_text: str, output_root: str | None = None) -> list[dict]:
    """
    High-level helper that:
      1) Suggests Lego modules from free-text requirements.
      2) Calls the Lego module executor to generate backend artifacts.

    It returns a list of dicts with:
      - module
      - resource_name
      - output_dir
      - files
    """
    from pathlib import Path
    from services.lego_module_executor import generate_from_module

    # 1) Elegir módulos a partir del texto
    module_names = suggest_modules_for_requirements(requirements_text)

    if output_root is None:
        base = Path("workdir") / "from_requirements"
    else:
        base = Path(output_root)
    base.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for module_name in module_names:
        module_root = base / module_name.replace(".", "_")
        module_root.mkdir(parents=True, exist_ok=True)
        generated = generate_from_module(module_name, module_root)
        results.extend(generated)

    return results

# --- Fixed version of generate_from_requirements (overrides previous one) ---

def generate_from_requirements(requirements_text: str, output_root: str | None = None) -> list[dict]:
    """
    High-level helper that:
      1) Suggests Lego modules from free-text requirements.
      2) Calls the Lego module executor to generate backend artifacts.

    It returns a list of dicts with:
      - module
      - resource_name
      - output_dir
      - files
    """
    from pathlib import Path
    from services.lego_module_executor import generate_from_module

    # 1) Elegir módulos a partir del texto
    module_names = suggest_modules_for_requirements(requirements_text)

    # 2) Directorio raíz para todo lo generado desde requisitos
    if output_root is None:
        base = Path("workdir") / "from_requirements"
    else:
        base = Path(output_root)
    base.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for module_name in module_names:
        # OJO: aquí ya no añadimos el nombre del módulo dos veces.
        # generate_from_module se encarga de añadir module_name.replace(".", "_")
        generated = generate_from_module(module_name, base)
        results.extend(generated)

    return results

# --- Fixed / extended version of suggest_modules_for_requirements (overrides previous one) ---

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    Very simple keyword-based heuristic for now.
    """
    text = requirements_text.lower()
    suggestions: list[str] = []

    # Catálogo de productos
    if any(word in text for word in ["producto", "productos", "catálogo", "catalogo", "catalogue"]):
        suggestions.append("business.ecommerce.product_catalog")

    # Órdenes / checkout / pagos
    if any(word in text for word in ["orden", "órdenes", "ordenes", "pedido", "checkout", "pago", "pagos"]):
        suggestions.append("business.ecommerce.order_management")

    # Fallback: si no detectamos nada, dejamos catálogo por defecto
    if not suggestions:
        suggestions.append("business.ecommerce.product_catalog")

    # Remove duplicates preserving order
    seen = set()
    unique: list[str] = []
    for name in suggestions:
        if name not in seen:
            seen.add(name)
            unique.append(name)

    return unique

# --- Fixed / extended version of suggest_modules_for_requirements (overrides previous ones) ---

def suggest_modules_for_requirements(requirements_text: str) -> list[str]:
    """
    Suggest Lego modules based on a free-text requirements description.

    Very simple keyword-based heuristic for now.
    """
    text = requirements_text.lower()
    suggestions: list[str] = []

    def add(name: str) -> None:
        if name not in suggestions:
            suggestions.append(name)

    # Ecommerce / catálogo
    if any(k in text for k in ["ecommerce", "tienda online", "catálogo", "catalogo", "productos", "product catalog"]):
        add("business.ecommerce.product_catalog")

    # Orders / checkout
    if any(k in text for k in ["pedido", "pedidos", "checkout", "orden", "órdenes", "ordenes", "order management"]):
        add("business.ecommerce.order_management")

    # Users / auth
    if any(
        k in text
        for k in [
            "usuario",
            "usuarios",
            "users",
            "login",
            "log in",
            "signin",
            "sign in",
            "registro",
            "signup",
            "sign up",
            "autenticación",
            "authentication",
        ]
    ):
        add("core.auth.users")

    return suggestions
