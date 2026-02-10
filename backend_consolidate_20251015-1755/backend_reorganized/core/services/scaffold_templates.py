# core/services/scaffold_templates.py

USERS_ROUTER = """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    obj = models.User(email=user.email, full_name=user.full_name, is_active=user.is_active)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj
"""

SCHEMAS = """\
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase): pass

class UserOut(UserBase):
    id: int
"""

MODELS = """\
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
"""

DB = """\
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

HEALTH = """\
from fastapi import APIRouter
router = APIRouter()
@router.get("/api/health")
def health():
    return {"status": "healthy"}
"""

MAIN = """\
from fastapi import FastAPI
from .routers.health import router as health_router
from .routers.users import router as users_router

app = FastAPI(title="Forge App")
app.include_router(health_router)
app.include_router(users_router)
"""

REQ = """\
fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.12.4
SQLAlchemy==2.0.30
email-validator==2.2.0
"""

ALEMBIC_INI = """\
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./app.db
"""

ALEMBIC_ENV = """\
from alembic import context
from sqlalchemy import engine_from_config, pool
config = context.config
target_metadata = None

def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
"""

ALEMBIC_0001 = """\
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
    )

def downgrade():
    op.drop_table("users")
"""

DOCKERFILE = """\
FROM python:3.12-slim
WORKDIR /app
COPY backend/app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend /app/backend
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
"""

COMPOSE = """\
services:
  app:
    build: .
    ports: ["8080:8080"]
    volumes: ["./backend:/app/backend"]
    environment:
      - DATABASE_URL=sqlite:///./app.db
"""
