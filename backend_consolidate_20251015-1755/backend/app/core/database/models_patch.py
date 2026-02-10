"""
Patch para agregar relación de suscripción al modelo User existente
"""
from backend.app.core.database.models import User
from backend.app.core.database.subscription_models_final import UserSubscription
from sqlalchemy.orm import relationship

# Agregar la relación al modelo User
User.subscription = relationship(
    "UserSubscription", 
    back_populates="user", 
    uselist=False, 
    cascade="all, delete-orphan"
)

print("✅ Relación de suscripción agregada al modelo User")
