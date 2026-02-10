import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Forge SaaS"
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.sqlite3")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    PRO_PRICE_ID: str | None = os.getenv("PRO_PRICE_ID")

    DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")

settings = Settings()
