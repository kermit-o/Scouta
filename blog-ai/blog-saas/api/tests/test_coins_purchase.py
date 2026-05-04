"""
Coin purchase + balance tests.

The /coins/purchase endpoint creates a Stripe Checkout Session — we mock
`stripe.checkout.Session.create` to assert metadata is correct without
calling Stripe. The actual coin credit happens later via webhook (covered
in test_stripe_webhook.py).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from app.models.coin_wallet import CoinWallet


PACKAGES_PATH = "/api/v1/coins/packages"
PURCHASE_PATH = "/api/v1/coins/purchase"
BALANCE_PATH = "/api/v1/coins/balance"


def test_packages_listed_publicly(client):
    """Anyone can list packages — no auth required."""
    resp = client.get(PACKAGES_PATH)
    assert resp.status_code == 200
    packages = resp.json()
    assert isinstance(packages, list)
    assert len(packages) == 3
    ids = {p["id"] for p in packages}
    assert ids == {"pack_100", "pack_500", "pack_2000"}
    # Each entry has the contract the frontend depends on.
    for p in packages:
        assert "coins" in p and isinstance(p["coins"], int)
        assert "price_cents" in p and isinstance(p["price_cents"], int)


def test_purchase_requires_auth(client):
    resp = client.post(PURCHASE_PATH, json={"package_id": "pack_100"})
    # Missing/invalid bearer → 401
    assert resp.status_code == 401


def test_purchase_unknown_package_returns_400(client, make_user, auth_header):
    user = make_user(email="buyer@example.com", username="buyer")
    resp = client.post(
        PURCHASE_PATH,
        json={"package_id": "pack_999_BOGUS"},
        headers=auth_header(user.id),
    )
    assert resp.status_code == 400
    assert "Invalid package_id" in resp.json()["detail"]


@patch("app.api.v1.coins.stripe.checkout.Session.create")
def test_purchase_creates_checkout_session_with_correct_metadata(
    mock_create, client, make_user, auth_header
):
    """Mock Stripe → assert we pass the right metadata so the webhook can
    later credit the right user with the right coin amount."""
    mock_create.return_value = SimpleNamespace(
        url="https://checkout.stripe.com/cs_test_xyz",
        id="cs_test_xyz",
    )
    user = make_user(email="buyer2@example.com", username="buyer2")

    resp = client.post(
        PURCHASE_PATH,
        json={"package_id": "pack_500"},
        headers=auth_header(user.id),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["checkout_url"] == "https://checkout.stripe.com/cs_test_xyz"
    assert body["session_id"] == "cs_test_xyz"
    assert body["coins"] == 500

    # Verify what we sent to Stripe
    mock_create.assert_called_once()
    kwargs = mock_create.call_args.kwargs
    assert kwargs["mode"] == "payment"
    assert kwargs["customer_email"] == "buyer2@example.com"

    metadata = kwargs["metadata"]
    assert metadata["type"] == "coin_purchase"
    assert metadata["user_id"] == str(user.id)
    assert metadata["coin_amount"] == "500"
    assert metadata["package_id"] == "pack_500"

    # Same metadata also embedded in payment_intent_data so it's available
    # on payment_intent.succeeded events too.
    pi_metadata = kwargs["payment_intent_data"]["metadata"]
    assert pi_metadata["user_id"] == str(user.id)
    assert pi_metadata["coin_amount"] == "500"


@patch("app.api.v1.coins.stripe.checkout.Session.create")
def test_purchase_propagates_stripe_error_as_502(
    mock_create, client, make_user, auth_header
):
    import stripe
    mock_create.side_effect = stripe.error.InvalidRequestError(
        "bad request", param="amount", code="invalid"
    )
    user = make_user(email="buyer3@example.com", username="buyer3")
    resp = client.post(
        PURCHASE_PATH,
        json={"package_id": "pack_100"},
        headers=auth_header(user.id),
    )
    assert resp.status_code == 502
    assert "Stripe error" in resp.json()["detail"]


def test_balance_requires_auth(client):
    resp = client.get(BALANCE_PATH)
    assert resp.status_code == 401


def test_balance_returns_zero_for_new_user(client, make_user, auth_header):
    """First read auto-creates an empty wallet."""
    user = make_user(email="newbie@example.com", username="newbie")
    resp = client.get(BALANCE_PATH, headers=auth_header(user.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "balance": 0,
        "withdrawable_balance": 0,
        "lifetime_earned": 0,
        "lifetime_spent": 0,
    }


def test_balance_reflects_existing_wallet(client, db_session, make_user, auth_header):
    session, _ = db_session
    user = make_user(email="rich@example.com", username="rich")
    wallet = CoinWallet(
        user_id=user.id,
        balance=750,
        withdrawable_balance=200,
        lifetime_earned=1000,
        lifetime_spent=250,
    )
    session.add(wallet)
    session.commit()

    resp = client.get(BALANCE_PATH, headers=auth_header(user.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == 750
    assert body["withdrawable_balance"] == 200
    assert body["lifetime_earned"] == 1000
    assert body["lifetime_spent"] == 250
