"""
Configuración de relaciones entre modelos - Para evitar import circulares
"""
from sqlalchemy.orm import relationship

def setup_relationships():
    """Configurar todas las relaciones después de que los modelos estén definidos"""
    from .models import User, Project, Job, AgentRun, APIKey, UserSession
    from .subscription_models_final import UserSubscription, BillingHistory
    
    # Configurar relaciones de User
    User.projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    User.api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan") 
    User.sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    User.subscription = relationship("UserSubscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    User.billing_history = relationship("BillingHistory", back_populates="user", cascade="all, delete-orphan")
    
    # Configurar back-populates
    Project.user = relationship("User", back_populates="projects")
    APIKey.user = relationship("User", back_populates="api_keys")
    UserSession.user = relationship("User", back_populates="sessions")
    UserSubscription.user = relationship("User", back_populates="subscription")
    BillingHistory.user = relationship("User", back_populates="billing_history")
    
    # Configurar otras relaciones
    Project.job = relationship("Job", back_populates="project", uselist=False, foreign_keys=[Project.job_id])
    Job.project = relationship("Project", back_populates="job", foreign_keys=[Job.project_id])
    Job.agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan")
    AgentRun.job = relationship("Job", back_populates="agent_runs")
    
    print("✅ Relaciones configuradas correctamente")

# Ejecutar configuración
setup_relationships()
