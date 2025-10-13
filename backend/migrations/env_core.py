from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os, sys, pathlib, pkgutil, importlib

from app.db import Base  
from app.models.job import Job
from app.models.agent_run import AgentRun
from app.models.artifact import Artifact
from app.models.project import Project  
import app.models as models_pkg

target_metadata = Base.metadata

# Asegura que /app esté en sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Importa TODOS los módulos bajo app.models para poblar metadata
for _, modname, _ in pkgutil.walk_packages(models_pkg.__path__, models_pkg.__name__ + "."):
    importlib.import_module(modname)


config = context.config

# Toma la URL de la variable de entorno
db_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name:
    fileConfig(config.config_file_name)

def run_migrations_offline():
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
