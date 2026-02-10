# core/auth/user_manager.py
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.core.database.models import User, Subscription
from backend.app.core.database.subscription_models_final import PlanType
from backend.app.core.database.models import Project

class UserManager:
    @staticmethod
    def can_create_project(user: User, db: Session) -> bool:
        """Verifica si el usuario puede crear más proyectos según su plan"""
        if user.subscription.plan_type == PlanType.FREE.value:
            # Contar proyectos este mes
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            project_count = db.query(Project).filter(
                Project.user_id == user.id,
                Project.created_at >= start_of_month
            ).count()
            return project_count < 1
        elif user.subscription.plan_type == PlanType.STARTER.value:
            # Límite de 5 proyectos/mes
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            project_count = db.query(Project).filter(
                Project.user_id == user.id,
                Project.created_at >= start_of_month
            ).count()
            return project_count < 5
        # Pro y Enterprise: ilimitados
        return True