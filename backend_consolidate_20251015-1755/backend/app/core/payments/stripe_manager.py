# core/payments/stripe_manager.py
import stripe
from fastapi import HTTPException
from backend.app.config.settings import settings

class StripeManager:
    def __init__(self):
        self.stripe_api_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = self.stripe_api_key
    
    async def create_checkout_session(self, user_id: str, price_id: str):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                client_reference_id=user_id,
            )
            return session
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# core/payments/subscription_service.py
from datetime import datetime, timedelta
from enum import Enum

class PlanType(Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionService:
    PLANS = {
        PlanType.FREE: {
            "monthly_price": 0,
            "yearly_price": 0,
            "projects_per_month": 1,
            "features": ["basic_generators", "community_support"]
        },
        PlanType.STARTER: {
            "monthly_price": 29,
            "yearly_price": 290,  # 2 meses gratis
            "projects_per_month": 5,
            "features": ["all_generators", "priority_support", "auto_deployment"]
        },
        PlanType.PRO: {
            "monthly_price": 79,
            "yearly_price": 790,  # 2 meses gratis
            "projects_per_month": -1,  # Ilimitado
            "features": ["advanced_generators", "24_7_support", "team_collaboration"]
        }
    }