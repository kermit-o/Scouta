"""
DietAI API - Versión simple pero 100% funcional
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import logging

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "dietai-dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar bcrypt seguro
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__max_password_size=72
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Modelos
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# Base de datos en memoria (simplificada)
users_db = {}

# Utilidades
def hash_password(password: str) -> str:
    """Hash seguro de contraseña"""
    if len(password) > 70:
        password = password[:70]
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña"""
    if len(plain) > 70:
        plain = plain[:70]
    return pwd_context.verify(plain, hashed)

def create_token(email: str) -> str:
    """Crear token JWT"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verificar token JWT"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtener usuario actual"""
    if token is None:
        return None
    
    payload = verify_token(token)
    if payload is None:
        return None
    
    email = payload.get("sub")
    if email is None:
        return None
    
    return users_db.get(email)

# Crear aplicación
app = FastAPI(
    title="DietAI API",
    version="3.0.0",
    description="API para gestión de dietas con autenticación",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ================= ENDPOINTS PÚBLICOS =================
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "DietAI API Funcional",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "online",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login", 
            "me": "GET /auth/me",
            "health": "GET /health",
            "diets": "GET /diets/generate"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dietai-api"
    }

@app.post("/auth/register")
async def register(user: UserCreate):
    """Registrar usuario"""
    if user.email in users_db:
        raise HTTPException(400, "Email ya registrado")
    
    # Verificar username único
    for existing in users_db.values():
        if existing["username"] == user.username:
            raise HTTPException(400, "Username ya en uso")
    
    # Crear usuario
    users_db[user.email] = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.utcnow()
    }
    
    # Crear token
    token = create_token(user.email)
    
    return {
        "message": "Usuario registrado exitosamente",
        "user": {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        },
        "token": {
            "access_token": token,
            "token_type": "bearer"
        }
    }

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Iniciar sesión"""
    user = users_db.get(form_data.username)
    
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(401, "Credenciales incorrectas")
    
    token = create_token(user["email"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "username": user["username"]
        }
    }

@app.get("/auth/me")
async def get_me(current_user = Depends(get_current_user)):
    """Obtener usuario actual"""
    if current_user is None:
        raise HTTPException(401, "No autenticado")
    
    return {
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "created_at": current_user["created_at"].isoformat()
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
    """Generar dieta (público)"""
    # Cálculo simple
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    calories = bmr * 1.55  # moderate por defecto
    
    return {
        "success": True,
        "calories": round(calories),
        "recommendation": f"Consume {round(calories)} calorías diarias para {goal}"
    }

# ================= INICIALIZACIÓN =================
@app.on_event("startup")
async def startup():
    """Evento de inicio"""
    logger.info("🚀 DietAI API iniciada")
    # Crear usuario de prueba
    if "test@example.com" not in users_db:
        users_db["test@example.com"] = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Usuario de Prueba",
            "hashed_password": hash_password("test123"),
            "created_at": datetime.utcnow()
        }
    logger.info(f"📊 {len(users_db)} usuarios en base de datos")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
