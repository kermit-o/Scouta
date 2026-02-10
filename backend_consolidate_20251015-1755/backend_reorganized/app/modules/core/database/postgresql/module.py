from app.modules.specs import ModuleSpec


# PostgreSQL core database module specification
module_spec = ModuleSpec(
    name="core.database.postgresql",
    category="core",
    tags=["database", "postgresql", "sqlalchemy", "migrations"],
    required_env=[
        "DATABASE_URL",   # Main Forge app DB (and canonical entry for generated projects)
    ],
    description=(
        "Core PostgreSQL database module for Forge-generated projects. "
        "Provides SQLAlchemy engine/session configuration, Alembic migrations "
        "integration and health-check helpers."
    ),
)
