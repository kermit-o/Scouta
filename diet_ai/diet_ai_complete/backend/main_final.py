"""
DietAI API Final - Versión estable con autenticación
"""
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= CONFIGURACIÓN =================
SECRET_KEY = os.getenv("SECRET_KEY", "dietai-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración bcrypt (evitar error de 72 bytes)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__max_password_size=72  # Limitar tamaño de contraseña
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ================= MODELOS =================
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# ================= BASE DE DATOS SIMULADA =================
# En producción, usar PostgreSQL real
class Database:
    users = {}
    next_id = 1
    
    @classmethod
    def create_user(cls, email, username, password, full_name=None):
        user_id = cls.next_id
        cls.next_id += 1
        
        # Hash seguro de contraseña (truncar si es muy larga)
        if len(password) > 70:
            password = password[:70]
            logger.warning("Contraseña truncada por seguridad bcrypt")
        
        hashed_password = pwd_context.hash(password)
        
        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        cls.users[email] = user
        cls.users[user_id] = user
        
        # Crear usuario de prueba
        if len(cls.users) == 1:
            cls.create_user(
                email="test@example.com",
                username="testuser",
                password="test123",
                full_name="Usuario de Prueba"
            )
        
        return user
    
    @classmethod
    def get_user_by_email(cls, email):
        return cls.users.get(email)
    
    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.users.get(user_id)
    
    @classmethod
    def authenticate(cls, email, password):
        user = cls.get_user_by_email(email)
        if not user:
            return None
        
        # Verificar contraseña (truncar si es muy larga)
        if len(password) > 70:
            password = password[:70]
        
        if not pwd_context.verify(password, user["hashed_password"]):
            return None
        
        return user

# Inicializar base de datos
db = Database()

# ================= UTILIDADES JWT =================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

# ================= APLICACIÓN =================
app = FastAPI(
    title="DietAI API",
    version="3.0.0",
    description="API inteligente para gestión de dietas con autenticación JWT",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ENDPOINTS PÚBLICOS =================
@app.get("/")
async def root():
    return {
        "message": "DietAI API con Autenticación JWT",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "public": {
                "health": "GET /health",
                "diets": "GET /diets/generate"
            }
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dietai-api",
        "version": "3.0.0"
    }

@app.get("/diets/generate")
async def generate_diet(
    age: int,
    gender: str,
    height: float,
    weight: float,
    activity: str = "moderate",
    goal: str = "weight_loss"
):
    """Generador de dietas (público)"""
    # Cálculo básico
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    calories = bmr * activity_multipliers.get(activity.lower(), 1.55)
    
    if goal == "weight_loss":
        calories -= 500
        protein_ratio = 0.35
    elif goal == "muscle_gain":
        calories += 300
        protein_ratio = 0.40
    else:
        protein_ratio = 0.30
    
    return {
        "success": True,
        "calculated_values": {
            "bmr": round(bmr),
            "daily_calories": round(calories),
            "macros": {
                "protein_g": round((calories * protein_ratio) / 4),
                "carbs_g": round((calories * 0.45) / 4),
                "fat_g": round((calories * 0.25) / 9)
            }
        }
    }

# ================= AUTENTICACIÓN =================
@app.post("/auth/register", response_model=dict)
async def register(user: UserCreate):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    if db.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar username único
    for existing_user in db.users.values():
        if isinstance(existing_user, dict) and existing_user.get("username") == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
    
    # Crear usuario
    new_user = db.create_user(
        email=user.email,
        username=user.username,
        password=user.password,
        full_name=user.full_name
    )
    
    # Crear token
    token = create_access_token({"sub": user.email})
    
    return {
        "message": "Usuario registrado exitosamente",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "username": new_user["username"],
            "full_name": new_user["full_name"],
            "is_active": new_user["is_active"],
            "created_at": new_user["created_at"].isoformat()
        },
        "token": {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }

@app.post("/auth/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Iniciar sesión"""
    user = db.authenticate(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token({"sub": user["email"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        }
    }

@app.get("/auth/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"].isoformat()
    }

@app.get("/auth/validate")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validar token JWT"""
    return {
        "valid": True,
        "user": {
            "id": current_user["id"],
            "email": current_user["email"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ================= ENDPOINTS PROTEGIDOS =================
@app.get("/protected/dashboard")
async def user_dashboard(current_user: dict = Depends(get_current_user)):
    """Dashboard de usuario (protegido)"""
    return {
        "message": f"Bienvenido {current_user['username']}",
        "user_id": current_user["id"],
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Generar planes de dieta personalizados",
            "Seguimiento de progreso",
            "Recomendaciones inteligentes"
        ]
    }

@app.get("/protected/profile")
async def user_profile(current_user: dict = Depends(get_current_user)):
    """Perfil de usuario (protegido)"""
    return {
        "profile": {
            "user_id": current_user["id"],
            "email": current_user["email"],
            "username": current_user["username"],
            "full_name": current_user["full_name"],
            "member_since": current_user["created_at"].isoformat(),
            "account_status": "active" if current_user["is_active"] else "inactive"
        }
    }

# ================= INICIALIZACIÓN =================
@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    logger.info("🚀 DietAI API iniciada")
    logger.info(f"📊 Usuarios en base de datos: {len([u for u in db.users.values() if isinstance(u, dict)])}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
