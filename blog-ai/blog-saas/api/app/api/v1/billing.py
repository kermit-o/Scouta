"""
Billing endpoints — Stripe Elements + Webhooks
"""
import json
import stripe
import traceback as tb
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import SessionLocal
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.org import Org

router = APIRouter(prefix="/billing", tags=["billing"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_stripe():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


# ─── GET /billing/diag ───────────────────────────────────────────────────────
@router.get("/diag")
def billing_diag():
    import os
    return {
        "stripe_secret_set": bool(settings.STRIPE_SECRET_KEY),
        "stripe_secret_prefix": settings.STRIPE_SECRET_KEY[:7] if settings.STRIPE_SECRET_KEY else "EMPTY",
        "stripe_pub_set": bool(settings.STRIPE_PUBLISHABLE_KEY),
        "env_stripe_secret": bool(os.getenv("STRIPE_SECRET_KEY")),
        "env_stripe_prefix": (os.getenv("STRIPE_SECRET_KEY") or "")[:7],
    }


# ─── GET /billing/plans ───────────────────────────────────────────────────────
@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).order_by(Plan.price_cents).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_cents": p.price_cents,
            "max_agents": p.max_agents,
            "max_posts_month": p.max_posts_month,
            "can_create_posts": p.can_create_posts,
            "description": p.description,
        }
        for p in plans
    ]


# ─── GET /billing/me ──────────────────────────────────────────────────────────
@router.get("/me")
def my_billing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
    ).first()
    plan_id = sub.plan_id if sub else 1
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    return {
        "plan": plan.name if plan else "free",
        "plan_id": plan_id,
        "status": sub.status if sub else "free",
        "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
        "stripe_subscription_id": sub.stripe_subscription_id if sub else None,
    }


# ─── POST /billing/create-payment-intent ─────────────────────────────────────
@router.post("/create-payment-intent")
def create_payment_intent(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = get_stripe()
    plan_id = body.get("plan_id")
    if plan_id not in [2, 3]:
        raise HTTPException(400, "plan_id debe ser 2 (creator) o 3 (brand)")
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan or not plan.stripe_price_id:
        raise HTTPException(400, f"Plan sin stripe_price_id. plan={plan} price_id={plan.stripe_price_id if plan else None}")
    try:
        if not current_user.stripe_customer_id:
            customer = s.Customer.create(
                email=current_user.email,
                name=current_user.display_name or current_user.username or current_user.email,
                metadata={"user_id": str(current_user.id)},
            )
            current_user.stripe_customer_id = customer.id
            db.commit()
        else:
            customer = s.Customer.retrieve(current_user.stripe_customer_id)
        subscription = s.Subscription.create(
            customer=customer.id,
            items=[{"price": plan.stripe_price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            metadata={"user_id": str(current_user.id), "plan_id": str(plan_id)},
        )
        # Obtener invoice y luego payment intent por separado
        invoice_id = subscription.latest_invoice
        if hasattr(invoice_id, "id"):
            invoice_id = invoice_id.id
        invoice = s.Invoice.retrieve(str(invoice_id))
        # Buscar payment intent asociado al invoice
        pi_list = s.PaymentIntent.list(customer=customer.id, limit=5)
        client_secret = None
        for pi in pi_list.data:
            if pi.status in ("requires_payment_method", "requires_confirmation", "requires_action"):
                client_secret = pi.client_secret
                break
        if not client_secret and pi_list.data:
            client_secret = pi_list.data[0].client_secret
        if not client_secret:
            raise HTTPException(500, "No se pudo obtener client_secret de Stripe")
        return {
            "client_secret": client_secret,
            "subscription_id": subscription.id,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Stripe error: {str(e)} | {tb.format_exc()}")


# ─── POST /billing/cancel ─────────────────────────────────────────────────────
@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = get_stripe()
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
    ).first()
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(404, "No hay suscripción activa")
    s.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)
    sub.status = "canceling"
    db.commit()
    return {"ok": True, "message": "Suscripción cancelada al final del período"}


# ─── POST /billing/webhook ────────────────────────────────────────────────────
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Handles subscription lifecycle events. Verifies signature, then parses
    the payload as plain JSON to avoid Stripe SDK 9+ StripeObject .get() trap.
    """
    s = get_stripe()
    payload = await request.body()
    try:
        s.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    except ValueError:
        raise HTTPException(400, "Invalid payload")

    event = json.loads(payload)
    event_type = event.get("type")
    obj = (event.get("data") or {}).get("object") or {}

    if event_type == "invoice.payment_succeeded":
        _handle_payment_succeeded(obj, db)
    elif event_type in ("customer.subscription.deleted", "invoice.payment_failed"):
        _handle_subscription_ended(obj, db)
    elif event_type == "payment_intent.succeeded":
        _handle_coin_purchase(obj, db)
    return {"ok": True}


def _handle_payment_succeeded(invoice: dict, db: Session):
    stripe_sub_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    if not stripe_sub_id:
        return
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        return
    s = get_stripe()
    stripe_sub = s.Subscription.retrieve(stripe_sub_id)
    # StripeObject metadata doesn't expose .get() in SDK 9+; use bracket access
    # with try/except so missing/malformed metadata defaults to plan_id=2 (creator).
    try:
        plan_id = int(stripe_sub["metadata"]["plan_id"])
    except (KeyError, TypeError, ValueError):
        plan_id = 2
    from datetime import datetime, timezone
    period_end = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc)
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub:
        sub.plan_id = plan_id
        sub.stripe_subscription_id = stripe_sub_id
        sub.status = "active"
        sub.current_period_end = period_end
    else:
        sub = Subscription(
            user_id=user.id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_sub_id,
            status="active",
            current_period_end=period_end,
        )
        db.add(sub)
    from app.models.org_member import OrgMember
    member = db.query(OrgMember).filter(OrgMember.user_id == user.id).first()
    if member:
        org = db.query(Org).filter(Org.id == member.org_id).first()
        if org:
            org.plan_id = plan_id
            org.subscription_status = "active"
    db.commit()
    # Send subscription confirmation email
    try:
        from app.services.email_service import send_subscription_confirmation
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        plan_name = plan.name.capitalize() if plan else "Creator"
        send_subscription_confirmation(
            to_email=user.email,
            username=user.display_name or user.username or "there",
            plan_name=plan_name,
        )
    except Exception as e:
        print(f"[email] subscription confirmation failed: {e}")


def _handle_subscription_ended(obj: dict, db: Session):
    stripe_sub_id = obj.get("id") or obj.get("subscription")
    if not stripe_sub_id:
        return
    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()
    if sub:
        sub.status = "canceled"
        user = db.query(User).filter(User.id == sub.user_id).first()
        if user:
            from app.models.org_member import OrgMember
            member = db.query(OrgMember).filter(OrgMember.user_id == user.id).first()
            if member:
                org = db.query(Org).filter(Org.id == member.org_id).first()
                if org:
                    org.plan_id = 1
                    org.subscription_status = "free"
        db.commit()


def _handle_coin_purchase(payment_intent: dict, db: Session):
    """Credit coins to user wallet after successful Stripe payment."""
    metadata = payment_intent.get("metadata") or {}
    if metadata.get("type") != "coin_purchase":
        return  # Not a coin purchase, skip

    user_id = metadata.get("user_id")
    coin_amount = metadata.get("coin_amount")
    if not user_id or not coin_amount:
        return

    user_id = int(user_id)
    coin_amount = int(coin_amount)
    payment_id = payment_intent.get("id", "")

    from app.models.coin_wallet import CoinWallet
    from app.models.coin_transaction import CoinTransaction

    # Check for duplicate (idempotency)
    existing = db.query(CoinTransaction).filter(
        CoinTransaction.reference_id == payment_id,
        CoinTransaction.type == "purchase",
    ).first()
    if existing:
        return

    # Get or create wallet
    wallet = db.query(CoinWallet).filter(CoinWallet.user_id == user_id).first()
    if not wallet:
        wallet = CoinWallet(user_id=user_id, balance=0)
        db.add(wallet)
        db.flush()

    # Add coins to existing balance
    wallet.balance += coin_amount
    wallet.lifetime_earned += coin_amount

    # Record transaction
    txn = CoinTransaction(
        user_id=user_id,
        amount=coin_amount,
        type="purchase",
        reference_id=payment_id,
        description=f"Purchased {coin_amount} coins",
    )
    db.add(txn)
    db.commit()
    print(f"[coins] credited {coin_amount} coins to user {user_id} (payment {payment_id})")
