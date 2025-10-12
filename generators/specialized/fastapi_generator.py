import os
import json

class FastAPIGenerator:
    def generate(self, project_name, description, features, technologies):
        project_path = f"generated_projects/{project_name}"
        
        # Limpiar si existe
        if os.path.exists(project_path):
            import shutil
            shutil.rmtree(project_path)
        
        os.makedirs(project_path, exist_ok=True)
        
        print(f"🚀 Generando proyecto FastAPI: {project_name}")
        
        try:
            # 1. requirements.txt
            self._create_requirements(project_path, features)
            
            # 2. Estructura de la aplicación
            self._create_app_structure(project_path, project_name, description, features)
            
            # 3. Configuraciones
            self._create_config_files(project_path, features)
            
            # 4. Docker y deployment
            self._create_deployment_files(project_path, features)
            
            print(f"✅ FastAPI project '{project_name}' generado exitosamente!")
            
            return {
                "success": True,
                "project_path": project_path,
                "type": "fastapi_service",
                "features": features,
                "technologies": technologies,
                "next_steps": [
                    f"cd {project_path}",
                    "pip install -r requirements.txt",
                    "uvicorn app.main:app --reload",
                    "Abre http://localhost:8000/docs"
                ]
            }
            
        except Exception as e:
            print(f"❌ Error generando FastAPI project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_requirements(self, project_path, features):
        requirements = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "pydantic==2.5.0",
            "python-multipart==0.0.6"
        ]
        
        # Dependencias basadas en features
        if "auth" in features:
            requirements.extend([
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6"
            ])
        
        if any(db in ["postgresql", "mysql"] for db in features):
            requirements.extend([
                "sqlalchemy==2.0.23",
                "alembic==1.12.1",
                "psycopg2-binary==2.9.9" if "postgresql" in features else "",
                "pymysql==1.1.0" if "mysql" in features else ""
            ])
        
        if "payment" in features:
            requirements.append("stripe==5.5.0")
        
        # Filtrar elementos vacíos
        requirements = [req for req in requirements if req]
        
        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write("\n".join(requirements))
    
    def _create_app_structure(self, project_path, project_name, description, features):
        # Crear estructura de directorios
        app_dir = os.path.join(project_path, "app")
        api_dir = os.path.join(app_dir, "api")
        models_dir = os.path.join(app_dir, "models")
        database_dir = os.path.join(app_dir, "database")
        
        for directory in [app_dir, api_dir, models_dir, database_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # __init__.py files
        for init_dir in [app_dir, api_dir, models_dir, database_dir]:
            with open(os.path.join(init_dir, "__init__.py"), "w") as f:
                f.write('')
        
        # main.py principal
        main_content = f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting {project_name}...")
    yield
    # Shutdown
    print("👋 Shutting down {project_name}...")

app = FastAPI(
    title="{project_name}",
    description="{description}",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {{
        "message": "Welcome to {project_name}",
        "description": "{description}",
        "version": "1.0.0",
        "generated_by": "Forge SaaS - Más potente que lovable.dev"
    }}

@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "service": "{project_name}",
        "timestamp": "2024-01-01T00:00:00Z"
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        with open(os.path.join(app_dir, "main.py"), "w") as f:
            f.write(main_content)
        
        # Router principal
        api_router_content = '''from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def api_root():
    return {"message": "API is working!"}
'''
        with open(os.path.join(api_dir, "__init__.py"), "w") as f:
            f.write(api_router_content)
        
        # Añadir endpoints basados en features
        if "auth" in features:
            auth_content = '''from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
async def register(user_data: UserCreate):
    # TODO: Implement registration logic
    return {
        "message": "User registration endpoint ready",
        "user": {
            "email": user_data.email,
            "name": user_data.name
        }
    }

@router.post("/login")
async def login(login_data: UserLogin):
    # TODO: Implement login logic
    return {
        "message": "User login endpoint ready",
        "access_token": "demo_token_12345"
    }

@router.get("/me")
async def get_current_user():
    # TODO: Implement current user logic
    return {
        "user": {
            "id": 1,
            "email": "demo@example.com",
            "name": "Demo User"
        }
    }
'''
            with open(os.path.join(api_dir, "auth.py"), "w") as f:
                f.write(auth_content)
            
            # Actualizar router para incluir auth
            with open(os.path.join(api_dir, "__init__.py"), "a") as f:
                f.write('\nfrom . import auth\nrouter.include_router(auth.router)\n')
        
        if "payment" in features:
            payment_content = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentIntentCreate(BaseModel):
    amount: int
    currency: str = "usd"

class PaymentIntent(BaseModel):
    id: str
    client_secret: str
    amount: int

@router.post("/create-payment-intent")
async def create_payment_intent(payment_data: PaymentIntentCreate):
    # TODO: Integrate with Stripe
    return {
        "message": "Payment endpoint ready",
        "payment_intent": {
            "id": "pi_demo_12345",
            "client_secret": "pi_demo_secret_12345",
            "amount": payment_data.amount
        }
    }

@router.get("/methods")
async def get_payment_methods():
    return {
        "payment_methods": [
            {"type": "card", "name": "Credit Card"},
            {"type": "paypal", "name": "PayPal"}
        ]
    }
'''
            with open(os.path.join(api_dir, "payments.py"), "w") as f:
                f.write(payment_content)
            
            with open(os.path.join(api_dir, "__init__.py"), "a") as f:
                f.write('\nfrom . import payments\nrouter.include_router(payments.router)\n')
    
    def _create_config_files(self, project_path, features):
        # .env.example
        env_content = '''# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment (if using Stripe)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
'''
        with open(os.path.join(project_path, ".env.example"), "w") as f:
            f.write(env_content)
        
        # Configuración de la aplicación
        config_content = '''import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Application"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
        with open(os.path.join(project_path, "app", "config.py"), "w") as f:
            f.write(config_content)
    
    def _create_deployment_files(self, project_path, features):
        # Dockerfile
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        with open(os.path.join(project_path, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml para desarrollo
        compose_content = '''version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        with open(os.path.join(project_path, "docker-compose.yml"), "w") as f:
            f.write(compose_content)
