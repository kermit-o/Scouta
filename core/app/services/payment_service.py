from typing import Dict, Any
from enum import Enum

class PlanType(Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class PaymentService:
    """Basic payment and plan management"""
    
    PLANS = {
        PlanType.FREE: {
            "name": "Free",
            "price": 0,
            "projects_per_month": 3,
            "features": [
                "Proyectos básicos",
                "Soporte comunitario",
                "Generación estándar"
            ]
        },
        PlanType.PRO: {
            "name": "Pro", 
            "price": 29,
            "projects_per_month": 50,
            "features": [
                "Proyectos complejos",
                "Soporte prioritario",
                "Templates premium",
                "Generación rápida"
            ]
        },
        PlanType.ENTERPRISE: {
            "name": "Enterprise",
            "price": 99, 
            "projects_per_month": -1,  # Unlimited
            "features": [
                "Proyectos ilimitados",
                "Personalización completa",
                "Soporte 24/7",
                "API access",
                "White-label"
            ]
        }
    }
    
    def check_project_limit(self, user_plan: PlanType, projects_this_month: int) -> bool:
        """Check if user can create more projects based on their plan"""
        plan = self.PLANS[user_plan]
        if plan["projects_per_month"] == -1:  # Unlimited
            return True
        return projects_this_month < plan["projects_per_month"]
    
    def get_plan_features(self, plan_type: PlanType) -> Dict[str, Any]:
        """Get features for a specific plan"""
        return self.PLANS[plan_type]

