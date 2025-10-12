import os
from typing import List

class Settings:
    APP_NAME: str = "Forge SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/forge_saas")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    SUPPORTED_PROJECT_TYPES: List[str] = [
        "react_web_app", "nextjs_app", "vue_app", "fastapi_service",
        "react_native_mobile", "electron_desktop", "chrome_extension", 
        "ai_agent", "blockchain_dapp"
    ]
    FRONTEND_STACKS: List[str] = ["react", "vue", "angular", "svelte", "nextjs"]
    BACKEND_STACKS: List[str] = ["fastapi", "nodejs", "django", "flask", "spring"]
    DATABASE_STACKS: List[str] = ["postgresql", "mongodb", "mysql", "sqlite", "redis"]
    DEPLOYMENT_TARGETS: List[str] = ["vercel", "netlify", "heroku", "aws", "docker"]

settings = Settings()
