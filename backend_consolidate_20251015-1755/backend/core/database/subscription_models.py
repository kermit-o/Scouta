# 📁 core/database/subscription_models.py

from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()

class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    PAST_DUE = "past_due"
    TRIALING = "trialing"

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Información de Stripe
    stripe_subscription_id = Column(String, unique=True, index=True)
    stripe_price_id = Column(String)
    
    # Estado de suscripción
    status = Column(String, default=SubscriptionStatus.ACTIVE.value)
    plan_type = Column(String, default=SubscriptionPlan.FREE.value)
    
    # Período de facturación
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Límites específicos por suscripción
    monthly_projects_limit = Column(Integer, default=1)
    monthly_ai_requests_limit = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    user = relationship("User", back_populates="subscription")

class BillingHistory(Base):
    __tablename__ = "billing_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Información de Stripe
    stripe_invoice_id = Column(String, unique=True, index=True)
    stripe_payment_intent_id = Column(String)
    stripe_subscription_id = Column(String)
    
    # Información de facturación
    amount = Column(Numeric(10, 2))  # Monto en USD
    currency = Column(String(3), default="usd")
    status = Column(String)  # paid, failed, void
    billing_reason = Column(String)  # subscription_create, subscription_cycle, etc.
    
    # Detalles
    description = Column(Text)
    invoice_pdf_url = Column(Text)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    user = relationship("User")