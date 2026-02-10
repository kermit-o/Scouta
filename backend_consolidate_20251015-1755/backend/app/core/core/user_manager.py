"""
Manager de Usuarios - Sistema de autenticación y gestión
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# IMPORTACIONES CORREGIDAS
from backend.app.core.database.models import User
from backend.app.core.core.auth import AuthManager

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email: str, password: str, full_name: str = None) -> User:
        """Crear nuevo usuario con plan free"""
        # Verificar si el usuario ya existe
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User already exists")
        
        # Crear usuario
        user = User(
            email=email,
            hashed_password=AuthManager.get_password_hash(password),
            full_name=full_name,
            plan="free",
            max_projects_per_month=3,  # Plan free: 3 proyectos/mes (como en auth.py)
            projects_used_this_month=0,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthManager.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def can_create_project(self, user: User) -> Dict[str, Any]:
        """Verificar si el usuario puede crear un nuevo proyecto"""
        # Reset mensual del contador (si es nuevo mes)
        current_month = datetime.utcnow().month
        user_month = user.created_at.month if user.created_at else current_month
        
        if user_month != current_month:
            user.projects_used_this_month = 0
            self.db.commit()
        
        can_create = (
            user.max_projects_per_month == -1 or  # Ilimitado
            user.projects_used_this_month < user.max_projects_per_month
        )
        
        return {
            "can_create": can_create,
            "used": user.projects_used_this_month,
            "allowed": user.max_projects_per_month,
            "plan": user.plan
        }
    
    def increment_project_count(self, user: User) -> None:
        """Incrementar contador de proyectos del usuario"""
        user.projects_used_this_month += 1
        self.db.commit()
    
    def update_user_plan(self, user: User, new_plan: str) -> User:
        """Actualizar plan del usuario"""
        plan_limits = {
            "free": 3,
            "pro": 50,
            "enterprise": -1  # Ilimitado
        }
        
        user.plan = new_plan
        user.max_projects_per_month = plan_limits.get(new_plan, 3)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_stats(self, user: User) -> Dict[str, Any]:
        """Obtener estadísticas del usuario"""
        # Por ahora, solo stats básicas hasta que conectemos con proyectos
        return {
            "plan_usage": {
                "used": user.projects_used_this_month,
                "allowed": user.max_projects_per_month,
                "remaining": (
                    user.max_projects_per_month - user.projects_used_this_month
                    if user.max_projects_per_month != -1
                    else "unlimited"
                )
            },
            "plan": user.plan,
            "is_verified": user.is_verified,
            "is_active": user.is_active
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
