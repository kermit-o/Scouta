import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/forge_db")
    
    # App Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    MAX_PROJECT_SIZE = int(os.getenv("MAX_PROJECT_SIZE", "10485760"))
