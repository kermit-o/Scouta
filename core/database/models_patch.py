"""
Patch para agregar relación de suscripción al modelo User existente
"""
from core.database.models import User
from core.database.subscription_models import UserSubscription
from sqlalchemy.orm import relationship

# Agregar la relación al modelo User
User.subscription = relationship(
    "UserSubscription", 
    back_populates="user", 
    uselist=False, 
    cascade="all, delete-orphan"
)

print("✅ Relación de suscripción agregada al modelo User")
