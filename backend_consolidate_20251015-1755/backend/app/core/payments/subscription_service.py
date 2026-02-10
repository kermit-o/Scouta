# 📁 core/payments/subscription_service.py

from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.core.database.models import User
from backend.app.core.database.subscription_models import UserSubscription, SubscriptionPlan, SubscriptionStatus, BillingHistory
from backend.app.core.payments.stripe_client import stripe_client
from backend.app.core.payments.stripe_config import stripe_config

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Obtener suscripción del usuario"""
        return self.db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id
        ).first()
    
    def create_or_update_subscription(self, user: User, stripe_subscription_data: Dict) -> UserSubscription:
        """Crear o actualizar suscripción basada en webhook de Stripe"""
        subscription = self.get_user_subscription(user.id)
        
        if not subscription:
            subscription = UserSubscription(user_id=user.id)
            self.db.add(subscription)
        
        # Actualizar con datos de Stripe
        subscription.stripe_subscription_id = stripe_subscription_data["id"]
        subscription.stripe_price_id = stripe_subscription_data["items"]["data"][0]["price"]["id"]
        subscription.status = stripe_subscription_data["status"]
        subscription.plan_type = self._get_plan_from_price_id(subscription.stripe_price_id)
        
        # Actualizar período
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription_data["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription_data["current_period_end"]
        )
        
        # Actualizar límites basados en el plan
        limits = self._get_plan_limits(subscription.plan_type)
        subscription.monthly_projects_limit = limits["projects"]
        subscription.monthly_ai_requests_limit = limits["ai_requests"]
        
        # Actualizar usuario
        user.plan = subscription.plan_type
        user.max_projects_per_month = limits["projects"]
        
        self.db.commit()
        return subscription
    
    def can_user_create_project(self, user: User) -> bool:
        """Verificar si el usuario puede crear un nuevo proyecto"""
        if user.plan == SubscriptionPlan.ENTERPRISE.value:
            return True
        
        return user.projects_used_this_month < user.max_projects_per_month
    
    def increment_user_usage(self, user: User) -> None:
        """Incrementar contador de uso del usuario"""
        user.projects_used_this_month += 1
        self.db.commit()
    
    def _get_plan_from_price_id(self, price_id: str) -> str:
        """Convertir price_id de Stripe a tipo de plan"""
        price_mapping = {
            stripe_config.STRIPE_PRICE_STARTER: SubscriptionPlan.STARTER.value,
            stripe_config.STRIPE_PRICE_PRO: SubscriptionPlan.PRO.value,
            stripe_config.STRIPE_PRICE_ENTERPRISE: SubscriptionPlan.ENTERPRISE.value,
        }
        return price_mapping.get(price_id, SubscriptionPlan.FREE.value)
    
    def _get_plan_limits(self, plan_type: str) -> Dict:
        """Obtener límites basados en el plan"""
        limits = {
            SubscriptionPlan.FREE.value: {"projects": 1, "ai_requests": 10},
            SubscriptionPlan.STARTER.value: {"projects": 5, "ai_requests": 100},
            SubscriptionPlan.PRO.value: {"projects": 50, "ai_requests": 1000},
            SubscriptionPlan.ENTERPRISE.value: {"projects": 9999, "ai_requests": 99999},
        }
        return limits.get(plan_type, limits[SubscriptionPlan.FREE.value])
    
    def create_billing_record(self, user_id: str, invoice_data: Dict) -> BillingHistory:
        """Crear registro en historial de facturación"""
        billing_record = BillingHistory(
            user_id=user_id,
            stripe_invoice_id=invoice_data["id"],
            stripe_payment_intent_id=invoice_data.get("payment_intent"),
            stripe_subscription_id=invoice_data.get("subscription"),
            amount=invoice_data["amount_due"] / 100,  # Convertir de centavos a dólares
            currency=invoice_data["currency"],
            status=invoice_data["status"],
            billing_reason=invoice_data.get("billing_reason"),
            description=invoice_data.get("description"),
            invoice_pdf_url=invoice_data.get("invoice_pdf"),
            period_start=datetime.fromtimestamp(invoice_data["period_start"]),
            period_end=datetime.fromtimestamp(invoice_data["period_end"]),
        )
        
        self.db.add(billing_record)
        self.db.commit()
        return billing_record