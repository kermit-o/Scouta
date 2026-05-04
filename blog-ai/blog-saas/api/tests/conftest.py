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
    from app.core import deps as core_deps

    # There are THREE separate get_db definitions in this codebase:
    #   - app.core.db.get_db        (canonical)
    #   - app.core.deps.get_db      (used by auth.py and most routers)
    #   - coins.get_db              (shadowed inside coins.py)
    # FastAPI dependency_overrides keys by function identity, so we have to
    # override every variant or some routes will hit the real production DB.
    for fn in (core_db.get_db, core_deps.get_db, coins_module.get_db):
        app.dependency_overrides[fn] = _override_get_db

    # Reset slowapi storage so per-IP buckets from previous tests don't bleed
    # over and turn assertions into 429s.
    try:
        from app.core.rate_limit import limiter as _slowapi_limiter
        _slowapi_limiter.reset()
    except Exception:
        pass

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def make_wallet(db_session):
    """Factory for seeding a CoinWallet row with arbitrary balances."""
    session, _ = db_session

    def _make(
        user_id: int,
        balance: int = 0,
        withdrawable_balance: int = 0,
        lifetime_earned: int = 0,
        lifetime_spent: int = 0,
    ):
        from app.models.coin_wallet import CoinWallet
        existing = session.query(CoinWallet).filter_by(user_id=user_id).first()
        if existing:
            existing.balance = balance
            existing.withdrawable_balance = withdrawable_balance
            existing.lifetime_earned = lifetime_earned
            existing.lifetime_spent = lifetime_spent
            session.commit()
            return existing
        wallet = CoinWallet(
            user_id=user_id,
            balance=balance,
            withdrawable_balance=withdrawable_balance,
            lifetime_earned=lifetime_earned,
            lifetime_spent=lifetime_spent,
        )
        session.add(wallet)
        session.commit()
        session.refresh(wallet)
        return wallet

    return _make


@pytest.fixture
def make_stream(db_session):
    """Seed a LiveStream row."""
    session, _ = db_session

    def _make(
        room_name: str,
        host_user_id: int,
        status: str = "live",
        title: str = "demo",
        is_private: bool = False,
        access_type: str = "public",
        password_hash: str | None = None,
        entry_coin_cost: int = 0,
        max_viewer_limit: int = 0,
        viewer_count: int = 0,
    ):
        from app.models.live_stream import LiveStream
        s = LiveStream(
            room_name=room_name,
            title=title,
            host_user_id=host_user_id,
            status=status,
            is_private=is_private,
            access_type=access_type,
            password_hash=password_hash,
            entry_coin_cost=entry_coin_cost,
            max_viewer_limit=max_viewer_limit,
            viewer_count=viewer_count,
        )
        session.add(s)
        session.commit()
        session.refresh(s)
        return s

    return _make


@pytest.fixture
def make_user(db_session):
    """Factory for creating a User row in the test DB.
    Returns a callable; defaults to verified, non-banned. Override via kwargs."""
    session, _ = db_session

    def _make(
        email: str = "user@example.com",
        username: str = "user",
        password_hash: str = "x",
        is_verified: bool = True,
        is_banned: bool = False,
        **extra,
    ):
        from app.models.user import User
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            is_verified=is_verified,
            is_banned=is_banned,
            **extra,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return _make


@pytest.fixture
def auth_header():
    """Mint a real JWT for a given user_id and return an Authorization header."""
    from app.core.security import create_access_token

    def _header(user_id: int) -> dict:
        token = create_access_token(subject=str(user_id))
        return {"Authorization": f"Bearer {token}"}

    return _header


@pytest.fixture(autouse=True)
def _mute_outbound_email(monkeypatch):
    """Stub all outbound email so tests don't hit Resend.

    Applied to every test automatically — none of our tests want to send
    real email. The stubs return None and are no-ops."""
    import app.services.email_service as email_svc
    for fn in (
        "send_verification_email",
        "send_welcome_email",
        "send_admin_notification",
        "send_reset_email",
    ):
        if hasattr(email_svc, fn):
            monkeypatch.setattr(email_svc, fn, lambda *a, **kw: None)
