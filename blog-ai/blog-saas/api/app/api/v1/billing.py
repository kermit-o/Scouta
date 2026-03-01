"""
Billing endpoints — Stripe Elements + Webhooks
"""
import stripe
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


# ─── GET /billing/plans ───────────────────────────────────────────────────────
@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    """Devuelve los 3 planes disponibles."""
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



# ─── GET /billing/diag ───────────────────────────────────────────────────────
@router.get("/diag")
def billing_diag():
    """Diagnóstico temporal — verificar config Stripe."""
    import os
    return {
        "stripe_secret_set": bool(settings.STRIPE_SECRET_KEY),
        "stripe_secret_prefix": settings.STRIPE_SECRET_KEY[:7] if settings.STRIPE_SECRET_KEY else "EMPTY",
        "stripe_pub_set": bool(settings.STRIPE_PUBLISHABLE_KEY),
        "env_stripe_secret": bool(os.getenv("STRIPE_SECRET_KEY")),
        "env_stripe_prefix": (os.getenv("STRIPE_SECRET_KEY") or "")[:7],
    }

# ─── GET /billing/me ──────────────────────────────────────────────────────────
@router.get("/me")
def my_billing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Estado actual de suscripción del usuario."""
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
    """Crea o reutiliza un Stripe Customer y devuelve un SetupIntent client_secret."""
    s = get_stripe()
    plan_id = body.get("plan_id")
    if plan_id not in [2, 3]:
        raise HTTPException(400, "plan_id debe ser 2 (creator) o 3 (brand)")

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan or not plan.stripe_price_id:
        raise HTTPException(400, "Plan sin stripe_price_id configurado")

    # Crear o recuperar customer
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

    # Crear suscripción con payment_behavior=default_incomplete
    subscription = s.Subscription.create(
        customer=customer.id,
        items=[{"price": plan.stripe_price_id}],
        payment_behavior="default_incomplete",
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
        metadata={"user_id": str(current_user.id), "plan_id": str(plan_id)},
    )

    client_secret = subscription.latest_invoice.payment_intent.client_secret

    return {
        "client_secret": client_secret,
        "subscription_id": subscription.id,
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }


# ─── POST /billing/cancel ─────────────────────────────────────────────────────
@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancela la suscripción activa al final del período."""
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
    """Webhook de Stripe — activa/cancela suscripciones."""
    s = get_stripe()
    payload = await request.body()

    try:
        event = s.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    if event["type"] == "invoice.payment_succeeded":
        _handle_payment_succeeded(event["data"]["object"], db)
    elif event["type"] in ("customer.subscription.deleted", "invoice.payment_failed"):
        _handle_subscription_ended(event["data"]["object"], db)

    return {"ok": True}


def _handle_payment_succeeded(invoice, db: Session):
    stripe_sub_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    if not stripe_sub_id:
        return

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        return

    s = get_stripe()
    stripe_sub = s.Subscription.retrieve(stripe_sub_id)
    plan_id = int(stripe_sub.metadata.get("plan_id", 2))

    from datetime import datetime, timezone
    period_end = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc)

    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).first()

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

    # Actualizar org del usuario
    from app.models.org_member import OrgMember
    member = db.query(OrgMember).filter(OrgMember.user_id == user.id).first()
    if member:
        org = db.query(Org).filter(Org.id == member.org_id).first()
        if org:
            org.plan_id = plan_id
            org.subscription_status = "active"

    db.commit()


def _handle_subscription_ended(obj, db: Session):
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
            member = db.query(__import__('app.models.org_member', fromlist=['OrgMember']).OrgMember).filter_by(user_id=user.id).first()
            if member:
                org = db.query(Org).filter(Org.id == member.org_id).first()
                if org:
                    org.plan_id = 1
                    org.subscription_status = "free"
        db.commit()
