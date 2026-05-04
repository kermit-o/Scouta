"""
Shared pytest fixtures.

Strategy: spin up a fresh in-memory SQLite database per test, override the
`get_db` dependency in both `app.core.db` and `app.api.v1.coins` (the coins
module re-defines its own `get_db` shadowing the global one), and yield a
FastAPI TestClient bound to that DB.

Models are imported via `app.models` so SQLAlchemy registers all tables
before `Base.metadata.create_all`.
"""
from __future__ import annotations

import os

# Set required env vars BEFORE any app modules import; settings reads them at module load.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-do-not-use-in-prod")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_dummy")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_dummy")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import db as core_db
from app.core.db import Base


@pytest.fixture
def db_session():
    """Fresh in-memory SQLite DB per test, shared across the connection pool
    (StaticPool) so the TestClient and the test see the same data."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Register all models on Base before create_all
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session, TestingSessionLocal
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """TestClient with get_db overridden to use the in-memory SQLite session."""
    session, TestingSessionLocal = db_session

    def _override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    # Import lazily so env vars set above are picked up.
    from app.main import app
    from app.api.v1 import coins as coins_module

    # The coins module defines its own get_db that shadows the core one;
    # override both to be safe.
    app.dependency_overrides[core_db.get_db] = _override_get_db
    app.dependency_overrides[coins_module.get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
