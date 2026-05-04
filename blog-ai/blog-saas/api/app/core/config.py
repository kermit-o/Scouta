"""
Application configuration - VERSIÓN SIMPLIFICADA
"""
from typing import Optional

# Configuración simple sin pydantic-settings
class Settings:
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Scouta Blog AI"

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"

    # JWT — actual secret resolution + dev-default check lives in app/core/security.py
    # so the warning fires once at module load instead of on every token decode.
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # DeepSeek API (opcional)
    DEEPSEEK_API_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""             # signs /coins/stripe-webhook deliveries
    STRIPE_BILLING_WEBHOOK_SECRET: str = ""     # signs /billing/webhook deliveries
    # ^ In live mode each Stripe webhook endpoint has its own signing secret;
    # in test mode you can set just STRIPE_WEBHOOK_SECRET and we fall back to
    # it for billing too. See docs/STRIPE_LIVE_MIGRATION.md.

    def __init__(self):
        # Intentar cargar desde .env si existe
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()

            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
            self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", self.JWT_ALGORITHM)
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.ACCESS_TOKEN_EXPIRE_MINUTES)))
            self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", self.DEEPSEEK_API_KEY)
            self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", self.STRIPE_SECRET_KEY)
            self.STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", self.STRIPE_PUBLISHABLE_KEY)
            self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", self.STRIPE_WEBHOOK_SECRET)
            # If the dedicated billing secret isn't set, fall back to the shared one
            # so test mode (single Stripe endpoint) keeps working without churn.
            self.STRIPE_BILLING_WEBHOOK_SECRET = (
                os.getenv("STRIPE_BILLING_WEBHOOK_SECRET")
                or self.STRIPE_WEBHOOK_SECRET
            )
        except ImportError:
            pass  # Sin dotenv, usar valores por defecto

settings = Settings()
