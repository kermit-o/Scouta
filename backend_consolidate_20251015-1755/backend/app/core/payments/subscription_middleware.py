# 📁 core/payments/subscription_middleware.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database.models import User
from backend.app.core.payments.subscription_service import SubscriptionService

def check_subscription_access(user: User, db: Session) -> bool:
    """Verificar si el usuario tiene acceso para crear proyectos"""
    subscription_service = SubscriptionService(db)
    
    if not subscription_service.can_user_create_project(user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Límite de proyectos alcanzado. Por favor actualiza tu plan."
        )
    
    return True