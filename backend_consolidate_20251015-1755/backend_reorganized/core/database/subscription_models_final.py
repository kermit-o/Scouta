"""
Modelos de suscripción para Forge SaaS
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Base se importará desde el módulo principal
Base = None

def init_models(base):
    """Inicializar modelos con la base proporcionada"""
    global Base
    Base = base
    
class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
        
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    stripe_subscription_id = Column(String, unique=True)
    stripe_price_id = Column(String)
    status = Column(String, default='active')
    plan_type = Column(String, default='free')
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    monthly_projects_limit = Column(Integer, default=1)
    monthly_ai_requests_limit = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SuscriptionPlan(Base):
    __tablename__ = 'suscription_plans'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='usd')
    monthly_projects_limit = Column(Integer, default=1)
    monthly_ai_requests_limit = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
    user = relationship("User", back_populates="subscription")
    
class BillingHistory(Base):
    __tablename__ = 'billing_history'
        
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    stripe_invoice_id = Column(String, unique=True)
    stripe_payment_intent_id = Column(String)
    stripe_subscription_id = Column(String)
    amount = Column(Numeric(10, 2))
    currency = Column(String(3), default='usd')
    status = Column(String)
    billing_reason = Column(String)
    description = Column(Text)
    invoice_pdf_url = Column(Text)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
        
    user = relationship("User")

# Enums para planes y estados
class SubscriptionPlan:
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus:
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
