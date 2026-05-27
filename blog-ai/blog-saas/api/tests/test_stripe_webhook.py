"""
Stripe webhook tests for /api/v1/coins/stripe-webhook.

Covers what would actually hurt in production:
- bad signature → 400
- non-checkout events → 200 ignored
- non-coin_purchase metadata → 200 ignored
- valid event → wallet credited + transaction row written
- replayed event (same session_id) → 200 already_credited, no double credit
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from app.models.user import User
from app.models.coin_wallet import CoinWallet
from app.models.coin_transaction import CoinTransaction


WEBHOOK_PATH = "/api/v1/coins/stripe-webhook"


def _make_event(
    *,
    user_id: int,
    coins: int,
    session_id: str,
    amount_total: int = 99,
    event_type: str = "checkout.session.completed",
    metadata_type: str = "coin_purchase",
) -> bytes:
    event = {
        "id": f"evt_{session_id}",
        "type": event_type,
        "data": {
            "object": {
                "id": session_id,
                "amount_total": amount_total,
                "metadata": {
                    "type": metadata_type,
                    "user_id": str(user_id),
                    "coin_amount": str(coins),
                },
            },
        },
    }
    return json.dumps(event).encode("utf-8")


@pytest.fixture
def seeded_user(db_session):
    session, _ = db_session
    user = User(
        email="buyer@example.com",
        password_hash="x",
        username="buyer",
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_bad_signature_returns_400(client):
    payload = _make_event(user_id=1, coins=100, session_id="cs_bad")
    # No mock — real signature verification will fail with the dummy secret.
    resp = client.post(
        WEBHOOK_PATH,
        content=payload,
        headers={"stripe-signature": "t=1,v1=deadbeef", "content-type": "application/json"},
    )
    assert resp.status_code == 400
    assert "signature" in resp.json()["detail"].lower() or "payload" in resp.json()["detail"].lower()


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_non_checkout_event_ignored(mock_construct, client, seeded_user):
    mock_construct.return_value = None  # bypass signature verification
    payload = _make_event(
        user_id=seeded_user.id,
        coins=100,
        session_id="cs_ignored_evt",
        event_type="payment_intent.created",
    )
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200
    assert resp.json() == {"received": True, "ignored": True}


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_non_coin_purchase_metadata_ignored(mock_construct, client, seeded_user):
    mock_construct.return_value = None
    payload = _make_event(
        user_id=seeded_user.id,
        coins=100,
        session_id="cs_other",
        metadata_type="subscription",
    )
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200
    assert resp.json() == {"received": True, "ignored": True}


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_valid_event_credits_wallet(mock_construct, client, db_session, seeded_user):
    mock_construct.return_value = None
    session, _ = db_session

    payload = _make_event(user_id=seeded_user.id, coins=500, session_id="cs_credit_1")
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["credited"] is True
    assert body["coins"] == 500
    assert body["user_id"] == seeded_user.id

    # Wallet was credited + transaction recorded
    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=seeded_user.id).first()
    assert wallet is not None
    assert wallet.balance == 500

    tx = session.query(CoinTransaction).filter_by(reference_id="cs_credit_1").first()
    assert tx is not None
    assert tx.amount == 500
    assert tx.type == "purchase"


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_replayed_event_is_idempotent(mock_construct, client, db_session, seeded_user):
    mock_construct.return_value = None
    session, _ = db_session

    payload = _make_event(user_id=seeded_user.id, coins=500, session_id="cs_replay_1")

    # First delivery — credits.
    r1 = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert r1.status_code == 200
    assert r1.json().get("credited") is True

    # Second delivery — must NOT credit again.
    r2 = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert r2.status_code == 200
    assert r2.json() == {"received": True, "already_credited": True}

    # Wallet still has 500, not 1000.
    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=seeded_user.id).first()
    assert wallet.balance == 500

    tx_count = session.query(CoinTransaction).filter_by(reference_id="cs_replay_1").count()
    assert tx_count == 1


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_unknown_user_returns_200_ignored(mock_construct, client, db_session):
    mock_construct.return_value = None
    payload = _make_event(user_id=99999, coins=100, session_id="cs_no_user")
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["received"] is True
    assert body.get("ignored") is True


@patch("app.api.v1.coins.stripe.Webhook.construct_event")
def test_missing_metadata_returns_200_ignored(mock_construct, client, seeded_user):
    mock_construct.return_value = None
    event = {
        "id": "evt_no_meta",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_no_meta",
                "amount_total": 99,
                "metadata": {"type": "coin_purchase"},  # missing user_id, coin_amount
            }
        },
    }
    resp = client.post(
        WEBHOOK_PATH,
        content=json.dumps(event).encode("utf-8"),
        headers={"stripe-signature": "ok"},
    )
    assert resp.status_code == 200
    assert resp.json().get("ignored") is True
