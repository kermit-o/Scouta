"""
Auth flow tests.

Covers register / login / forgot-password / reset-password / verify-email.
Email side-effects are stubbed via the autouse fixture in conftest.

Note on rate limits: register=2/min, login=3/min, forgot=1/min. With slowapi's
in-memory store and per-test fresh app, the limits are scoped per process and
will accumulate across tests in the same module. We stay well under the limits
by using distinct emails/IPs and not hammering any single endpoint.
"""
from __future__ import annotations

from app.models.user import User


REGISTER_PATH = "/api/v1/auth/register"
LOGIN_PATH = "/api/v1/auth/login"
FORGOT_PATH = "/api/v1/auth/forgot-password"
RESET_PATH = "/api/v1/auth/reset-password"
VERIFY_PATH = "/api/v1/auth/verify"


def _register_payload(email="alice@example.com", username="alice", password="hunter22long"):
    return {
        "email": email,
        "password": password,
        "username": username,
        "display_name": "Alice",
        "cf_turnstile_token": "ok",
    }


def test_register_success(client, db_session):
    session, _ = db_session
    resp = client.post(REGISTER_PATH, json=_register_payload())
    assert resp.status_code == 200
    assert "Registration successful" in resp.json()["message"]

    user = session.query(User).filter_by(email="alice@example.com").one()
    assert user.is_verified is False
    assert user.verification_token is not None
    # Password is hashed, not stored in plaintext.
    assert user.password_hash != "hunter22long"


def test_register_duplicate_email_returns_409(client, make_user):
    make_user(email="dupe@example.com", username="other")
    resp = client.post(REGISTER_PATH, json=_register_payload(email="dupe@example.com", username="brandnew"))
    assert resp.status_code == 409
    assert "email" in resp.json()["detail"].lower()


def test_register_duplicate_username_returns_409(client, make_user):
    make_user(email="taken@example.com", username="takenuser")
    resp = client.post(REGISTER_PATH, json=_register_payload(email="fresh@example.com", username="takenuser"))
    assert resp.status_code == 409
    assert "username" in resp.json()["detail"].lower()


def test_register_short_password_rejected(client):
    resp = client.post(REGISTER_PATH, json=_register_payload(password="short"))
    # Pydantic validation
    assert resp.status_code == 422


def test_login_success_returns_jwt(client, make_user):
    from app.core.security import hash_password

    make_user(
        email="bob@example.com",
        username="bob",
        password_hash=hash_password("correct-horse-battery"),
        is_verified=True,
    )
    resp = client.post(
        LOGIN_PATH,
        json={"email": "bob@example.com", "password": "correct-horse-battery", "cf_turnstile_token": "ok"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["username"] == "bob"


def test_login_wrong_password_returns_401(client, make_user):
    from app.core.security import hash_password

    make_user(email="charlie@example.com", username="charlie", password_hash=hash_password("real-pw"))
    resp = client.post(
        LOGIN_PATH,
        json={"email": "charlie@example.com", "password": "WRONG", "cf_turnstile_token": "ok"},
    )
    assert resp.status_code == 401


def test_login_unknown_email_returns_401(client):
    resp = client.post(
        LOGIN_PATH,
        json={"email": "nobody@example.com", "password": "any", "cf_turnstile_token": "ok"},
    )
    assert resp.status_code == 401


def test_login_unverified_user_blocked(client, make_user):
    from app.core.security import hash_password

    make_user(
        email="dora@example.com",
        username="dora",
        password_hash=hash_password("password123"),
        is_verified=False,
    )
    resp = client.post(
        LOGIN_PATH,
        json={"email": "dora@example.com", "password": "password123", "cf_turnstile_token": "ok"},
    )
    assert resp.status_code == 403
    assert "verify" in resp.json()["detail"].lower()


def test_login_banned_user_blocked(client, make_user):
    from app.core.security import hash_password

    make_user(
        email="evan@example.com",
        username="evan",
        password_hash=hash_password("password123"),
        is_verified=True,
        is_banned=True,
        ban_reason="spam",
    )
    resp = client.post(
        LOGIN_PATH,
        json={"email": "evan@example.com", "password": "password123", "cf_turnstile_token": "ok"},
    )
    assert resp.status_code == 403
    assert "suspended" in resp.json()["detail"].lower()


def test_forgot_password_unknown_email_still_returns_200(client):
    """Must not reveal whether the email exists — same response either way."""
    resp = client.post(FORGOT_PATH, json={"email": "ghost@example.com"})
    assert resp.status_code == 200
    assert "If that email exists" in resp.json()["message"]


def test_forgot_password_known_email_sets_reset_token(client, db_session, make_user):
    session, _ = db_session
    make_user(email="frank@example.com", username="frank")
    resp = client.post(FORGOT_PATH, json={"email": "frank@example.com"})
    assert resp.status_code == 200

    session.expire_all()
    user = session.query(User).filter_by(email="frank@example.com").one()
    assert user.verification_token is not None


def test_reset_password_with_valid_token(client, db_session, make_user):
    """A user holding a valid reset token can pick a new password and log in."""
    from app.core.security import hash_password, verify_and_update_password

    session, _ = db_session
    user = make_user(
        email="grace@example.com",
        username="grace",
        password_hash=hash_password("old-pw-12345"),
    )
    user.verification_token = "valid-reset-token"
    session.add(user)
    session.commit()

    resp = client.post(RESET_PATH, json={"token": "valid-reset-token", "password": "new-pw-67890"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]

    session.expire_all()
    refreshed = session.query(User).filter_by(email="grace@example.com").one()
    ok, _ = verify_and_update_password("new-pw-67890", refreshed.password_hash)
    assert ok is True
    # Token cleared after use
    assert refreshed.verification_token is None


def test_reset_password_with_invalid_token_returns_400(client):
    resp = client.post(RESET_PATH, json={"token": "nope", "password": "anything-12345"})
    assert resp.status_code == 400


def test_verify_email_flips_flag_and_returns_token(client, db_session, make_user):
    session, _ = db_session
    user = make_user(
        email="henry@example.com",
        username="henry",
        is_verified=False,
    )
    user.verification_token = "verify-token-xyz"
    session.add(user)
    session.commit()

    resp = client.get(f"{VERIFY_PATH}?token=verify-token-xyz")
    assert resp.status_code == 200
    assert resp.json()["access_token"]

    session.expire_all()
    refreshed = session.query(User).filter_by(email="henry@example.com").one()
    assert refreshed.is_verified is True
    assert refreshed.verification_token is None


def test_verify_email_invalid_token_returns_400(client):
    resp = client.get(f"{VERIFY_PATH}?token=does-not-exist")
    assert resp.status_code == 400
