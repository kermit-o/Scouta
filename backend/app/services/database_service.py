from __future__ import annotations
import os
from typing import Iterator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://forge:forge@postgres:5432/forge")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class DatabaseService:
    def __init__(self) -> None:
        self.SessionLocal = SessionLocal

    @contextmanager
    def get_db(self) -> Iterator[Session]:
        db: Session = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
