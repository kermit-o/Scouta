# 📁 core/database/__init__.py

"""
Módulo de base de datos - Resuelve imports circulares
"""
from .models import Base, User, Project, Job, AgentRun, APIKey, UserSession
from .subscription_models import UserSubscription, BillingHistory

# Ahora que todos los modelos están definidos, podemos establecer las relaciones
from sqlalchemy.orm import relationship

# Establecer relación en User
User.subscription = relationship(
    "UserSubscription", 
    back_populates="user", 
    uselist=False, 
    cascade="all, delete-orphan"
)

# Establecer relación en UserSubscription (necesita import tardío)
def setup_relationships():
    """Configurar relaciones después de que todos los modelos estén definidos"""
    from .subscription_models import UserSubscription, BillingHistory
    
    # UserSubscription ya tiene la relación definida en su clase
    # Solo necesitamos asegurar que use la misma Base
    UserSubscription.metadata = Base.metadata
    BillingHistory.metadata = Base.metadata

# Ejecutar setup
setup_relationships()

# Exportar todos los modelos
__all__ = [
    'Base', 
    'User', 
    'Project', 
    'Job', 
    'AgentRun', 
    'APIKey', 
    'UserSession',
    'UserSubscription', 
    'BillingHistory'
]