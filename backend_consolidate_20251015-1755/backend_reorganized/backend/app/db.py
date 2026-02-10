from __future__ import annotations

from typing import Generator

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./backend/app/app.db",  # default for local dev
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
