"""
Subscription/billing flow tests.

Coverage of /billing endpoints — the second Stripe surface (separate from
the coin-purchase webhook in coins.py). Subscriptions track which plan a
user is on (free/creator/brand) and their Org's plan tier.

The webhook is the source of truth for activation, renewal, and
cancellation. Tests assert that:
- Bad signatures are rejected (400)
- invoice.payment_succeeded creates/updates Subscription + Org plan
- subscription.deleted / payment_failed → status=canceled + Org back to free
- payment_intent.succeeded with type=coin_purchase credits the wallet
  (this is the legacy alternative path before checkout sessions; still
  supported for any old payment_intent flow)
- Idempotency on coin credit (replayed payment_intent doesn't double-credit)

Skipped: /billing/create-payment-intent — would require mocking 4-5 Stripe
SDK calls just to assert glue. Low ROI vs. the webhook coverage which is
the actual contract with Stripe.
"""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from app.models.coin_transaction import CoinTransaction
from app.models.coin_wallet import CoinWallet
from app.models.org import Org
from app.models.org_member import OrgMember
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.user import User


PLANS_PATH = "/api/v1/billing/plans"
ME_PATH = "/api/v1/billing/me"
CANCEL_PATH = "/api/v1/billing/cancel"
WEBHOOK_PATH = "/api/v1/billing/webhook"


@pytest.fixture
def seed_plans(db_session):
    """Seed the three plans the app expects (free=1, creator=2, brand=3)."""
    session, _ = db_session

    def _seed():
        for p in [
            Plan(id=1, name="free", price_cents=0, max_agents=0, max_posts_month=10, can_create_posts=False),
            Plan(id=2, name="creator", price_cents=1900, max_agents=3, max_posts_month=100, can_create_posts=True, stripe_price_id="price_creator"),
            Plan(id=3, name="brand", price_cents=7900, max_agents=10, max_posts_month=500, can_create_posts=True, stripe_price_id="price_brand"),
        ]:
            session.merge(p)
        session.commit()

    return _seed


@pytest.fixture
def seed_org_for(db_session):
    """Seed an Org + OrgMember linkage so webhook handlers can find them."""
    session, _ = db_session

    def _seed(user_id: int, org_id: int = 1, slug: str = "default"):
        existing_org = session.query(Org).filter_by(id=org_id).first()
        if not existing_org:
            session.add(Org(id=org_id, name=slug.capitalize(), slug=slug, plan_id=1, subscription_status="free"))
            session.commit()
        if not session.query(OrgMember).filter_by(user_id=user_id, org_id=org_id).first():
            session.add(OrgMember(org_id=org_id, user_id=user_id, role="owner"))
            session.commit()

    return _seed


# ---------- Plans listing ----------

def test_plans_listed_publicly(client, seed_plans):
    seed_plans()
    resp = client.get(PLANS_PATH)
    assert resp.status_code == 200
    plans = resp.json()
    assert len(plans) == 3
    by_name = {p["name"]: p for p in plans}
    assert by_name["free"]["price_cents"] == 0
    assert by_name["creator"]["price_cents"] == 1900
    assert by_name["brand"]["price_cents"] == 7900


# ---------- /billing/me ----------

def test_me_requires_auth(client):
    resp = client.get(ME_PATH)
    assert resp.status_code == 401


def test_me_returns_free_plan_for_user_without_subscription(
    client, make_user, auth_header, seed_plans
):
    seed_plans()
    user = make_user(email="freeuser@example.com", username="freeuser")
    resp = client.get(ME_PATH, headers=auth_header(user.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["plan"] == "free"
    assert body["plan_id"] == 1
    assert body["status"] == "free"
    assert body["stripe_subscription_id"] is None


def test_me_returns_active_subscription(
    client, db_session, make_user, auth_header, seed_plans
):
    session, _ = db_session
    seed_plans()
    user = make_user(email="paid@example.com", username="paid")
    sub = Subscription(
        user_id=user.id,
        plan_id=2,
        stripe_subscription_id="sub_xyz",
        status="active",
    )
    session.add(sub)
    session.commit()

    resp = client.get(ME_PATH, headers=auth_header(user.id))
    assert resp.status_code == 200
    body = resp.json()
    assert body["plan"] == "creator"
    assert body["plan_id"] == 2
    assert body["status"] == "active"
    assert body["stripe_subscription_id"] == "sub_xyz"


# ---------- /billing/cancel ----------

def test_cancel_requires_auth(client):
    resp = client.post(CANCEL_PATH)
    assert resp.status_code == 401


def test_cancel_without_active_sub_returns_404(client, make_user, auth_header):
    user = make_user(email="nosub@example.com", username="nosub")
    resp = client.post(CANCEL_PATH, headers=auth_header(user.id))
    assert resp.status_code == 404


@patch("app.api.v1.billing.stripe.Subscription.modify")
def test_cancel_marks_canceling_and_calls_stripe(
    mock_modify, client, db_session, make_user, auth_header
):
    session, _ = db_session
    user = make_user(email="canceler@example.com", username="canceler")
    sub = Subscription(
        user_id=user.id,
        plan_id=2,
        stripe_subscription_id="sub_to_cancel",
        status="active",
    )
    session.add(sub)
    session.commit()

    resp = client.post(CANCEL_PATH, headers=auth_header(user.id))
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    # Stripe was called with cancel_at_period_end (graceful cancel)
    mock_modify.assert_called_once_with("sub_to_cancel", cancel_at_period_end=True)

    session.expire_all()
    refreshed = session.query(Subscription).filter_by(user_id=user.id).one()
    assert refreshed.status == "canceling"


# ---------- Webhook: signature ----------

def test_webhook_bad_signature_returns_400(client):
    resp = client.post(
        WEBHOOK_PATH,
        content=b'{"type":"customer.subscription.deleted"}',
        headers={"stripe-signature": "t=1,v1=deadbeef", "content-type": "application/json"},
    )
    assert resp.status_code == 400


# ---------- Webhook: invoice.payment_succeeded ----------

@patch("app.api.v1.billing.stripe.Webhook.construct_event")
@patch("app.api.v1.billing.stripe.Subscription.retrieve")
def test_webhook_payment_succeeded_creates_subscription_and_upgrades_org(
    mock_sub_retrieve, mock_construct,
    client, db_session, make_user, seed_plans, seed_org_for,
):
    session, _ = db_session
    seed_plans()
    user = make_user(email="newpaid@example.com", username="newpaid")
    user.stripe_customer_id = "cus_xyz"
    session.add(user)
    session.commit()
    seed_org_for(user.id)

    mock_construct.return_value = None  # bypass signature verification

    # Stripe Subscription.retrieve mock — must support both attribute access
    # and item lookup (the handler uses both styles)
    fake_sub = MagicMock()
    fake_sub.current_period_end = 9_999_999_999  # far future timestamp
    fake_sub.__getitem__ = lambda self, key: {"metadata": {"plan_id": "2"}}[key]
    mock_sub_retrieve.return_value = fake_sub

    payload = json.dumps({
        "type": "invoice.payment_succeeded",
        "data": {"object": {"subscription": "sub_new", "customer": "cus_xyz"}},
    }).encode()
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200

    session.expire_all()
    sub = session.query(Subscription).filter_by(user_id=user.id).one()
    assert sub.plan_id == 2
    assert sub.stripe_subscription_id == "sub_new"
    assert sub.status == "active"
    assert sub.current_period_end is not None

    # Org plan was bumped to creator (id=2) and status active
    org = session.query(Org).filter_by(id=1).one()
    assert org.plan_id == 2
    assert org.subscription_status == "active"


# ---------- Webhook: subscription deleted ----------

@patch("app.api.v1.billing.stripe.Webhook.construct_event")
def test_webhook_subscription_deleted_marks_canceled_and_downgrades_org(
    mock_construct, client, db_session, make_user, seed_plans, seed_org_for,
):
    session, _ = db_session
    seed_plans()
    user = make_user(email="dropper@example.com", username="dropper")
    seed_org_for(user.id)

    sub = Subscription(
        user_id=user.id,
        plan_id=2,
        stripe_subscription_id="sub_dying",
        status="active",
    )
    session.add(sub)
    # bump org to creator first so we can verify the downgrade
    org = session.query(Org).filter_by(id=1).one()
    org.plan_id = 2
    org.subscription_status = "active"
    session.commit()

    mock_construct.return_value = None
    payload = json.dumps({
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_dying"}},
    }).encode()

    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200

    session.expire_all()
    refreshed = session.query(Subscription).filter_by(stripe_subscription_id="sub_dying").one()
    assert refreshed.status == "canceled"

    org = session.query(Org).filter_by(id=1).one()
    assert org.plan_id == 1  # back to free
    assert org.subscription_status == "free"


# ---------- Webhook: payment_intent.succeeded coin credit ----------

@patch("app.api.v1.billing.stripe.Webhook.construct_event")
def test_webhook_payment_intent_succeeded_credits_coins(
    mock_construct, client, db_session, make_user,
):
    session, _ = db_session
    user = make_user(email="coinbuyer@example.com", username="coinbuyer")
    mock_construct.return_value = None

    payload = json.dumps({
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_abc",
            "metadata": {
                "type": "coin_purchase",
                "user_id": str(user.id),
                "coin_amount": "500",
            },
        }},
    }).encode()

    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200

    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=user.id).one()
    assert wallet.balance == 500
    assert wallet.lifetime_earned == 500

    tx = session.query(CoinTransaction).filter_by(reference_id="pi_abc").one()
    assert tx.amount == 500
    assert tx.type == "purchase"


@patch("app.api.v1.billing.stripe.Webhook.construct_event")
def test_webhook_payment_intent_idempotent_on_replay(
    mock_construct, client, db_session, make_user,
):
    """Stripe occasionally redelivers the same payment_intent.succeeded.
    Two deliveries for the same payment_intent.id must credit only once."""
    session, _ = db_session
    user = make_user(email="replay@example.com", username="replay")
    mock_construct.return_value = None

    payload = json.dumps({
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_replay",
            "metadata": {
                "type": "coin_purchase",
                "user_id": str(user.id),
                "coin_amount": "200",
            },
        }},
    }).encode()

    r1 = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    r2 = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert r1.status_code == r2.status_code == 200

    session.expire_all()
    wallet = session.query(CoinWallet).filter_by(user_id=user.id).one()
    assert wallet.balance == 200  # not 400
    assert session.query(CoinTransaction).filter_by(reference_id="pi_replay").count() == 1


@patch("app.api.v1.billing.stripe.Webhook.construct_event")
def test_webhook_payment_intent_with_non_coin_metadata_is_ignored(
    mock_construct, client, db_session, make_user,
):
    """A payment_intent.succeeded for a subscription (not a coin purchase)
    must not touch wallets."""
    session, _ = db_session
    user = make_user(email="other@example.com", username="other")
    mock_construct.return_value = None

    payload = json.dumps({
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_subscription",
            "metadata": {"type": "subscription"},
        }},
    }).encode()

    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200

    session.expire_all()
    assert session.query(CoinWallet).filter_by(user_id=user.id).first() is None
    assert session.query(CoinTransaction).filter_by(reference_id="pi_subscription").first() is None


# ---------- Webhook: unknown event types are no-op ----------

@patch("app.api.v1.billing.stripe.Webhook.construct_event")
def test_webhook_unknown_event_type_is_ok(mock_construct, client):
    mock_construct.return_value = None
    payload = json.dumps({"type": "charge.refunded", "data": {"object": {}}}).encode()
    resp = client.post(WEBHOOK_PATH, content=payload, headers={"stripe-signature": "ok"})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
