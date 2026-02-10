"""
Configuración de relaciones entre modelos - Para evitar import circulares
"""
from sqlalchemy.orm import relationship

def configure_relationships():
    """Configurar todas las relaciones después de que los modelos estén definidos"""
    from .models_fixed import User, Project, Job, AgentRun, APIKey, UserSession
    from .subscription_models_final import UserSubscription, BillingHistory
    
    # Configurar relación User -> Projects
    User.projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    Project.user = relationship("User", back_populates="projects")
    
    # Configurar relación User -> APIKeys
    User.api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    APIKey.user = relationship("User", back_populates="api_keys")
    
    # Configurar relación User -> UserSubscription
    User.subscription = relationship("UserSubscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    UserSubscription.user = relationship("User", back_populates="subscription")
    
    # Configurar relación User -> UserSessions
    User.sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    UserSession.user = relationship("User", back_populates="sessions")
    
    # Configurar relación Project -> Job
    Project.job = relationship("Job", back_populates="project", uselist=False, foreign_keys=[Project.job_id])
    Job.project = relationship("Project", back_populates="job", foreign_keys=[Job.project_id])
    
    # Configurar relación Job -> AgentRuns
    Job.agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan")
    AgentRun.job = relationship("Job", back_populates="agent_runs")
    
    # Configurar relación User -> BillingHistory
    User.billing_history = relationship("BillingHistory", back_populates="user", cascade="all, delete-orphan")
    BillingHistory.user = relationship("User", back_populates="billing_history")
    
    print("✅ Relaciones configuradas correctamente")

# Ejecutar configuración al importar
configure_relationships()
