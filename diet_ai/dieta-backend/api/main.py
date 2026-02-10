from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Boolean, DateTime, Integer, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
import asyncpg
import redis
import uuid
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# IMPORTANTE: Usar asyncpg en la URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://dietai:dietai123@postgres:5432/dietai")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Definir Base aquí para que siempre esté disponible
Base = declarative_base()

# Definir modelos de base de datos (siempre disponibles)
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    weight_kg = Column(Integer)
    height_cm = Column(Integer)
    activity_level = Column(String(50))
    goal = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Intentar configurar conexión a base de datos
try:
    # Crear engine asíncrono con asyncpg
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True
    )
    
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True
    )
    
    DB_AVAILABLE = True
    logger.info("✅ Configuración de base de datos cargada")
    
except Exception as e:
    logger.warning(f"⚠️  No se pudo configurar la base de datos: {e}")
    logger.warning("Algunas funciones no estarán disponibles")
    engine = None
    AsyncSessionLocal = None
    DB_AVAILABLE = False

# Configurar Redis
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    REDIS_AVAILABLE = True
    logger.info("✅ Configuración de Redis cargada")
except Exception as e:
    logger.warning(f"⚠️  No se pudo configurar Redis: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# Modelos Pydantic
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    database_status: str = "unknown"
    redis_status: str = "unknown"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "2.0.0"
    services: dict

# Dependencia para obtener sesión de BD
async def get_db():
    if not DB_AVAILABLE or AsyncSessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Crear app FastAPI
app = FastAPI(
    title="Diet AI API v2",
    version="2.0.0",
    description="API optimizada para planificación dietética",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== FUNCIONES DE AYUDA ==========
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar usuario en BD
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        return user
    except SQLAlchemyError:
        raise credentials_exception

# ========== ENDPOINTS PÚBLICOS ==========
@app.get("/")
async def root():
    return {
        "message": "¡Diet AI API v2 funcionando con Docker! 🐳🚀",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "database": "available" if DB_AVAILABLE else "unavailable",
        "redis": "available" if REDIS_AVAILABLE else "unavailable",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api_v1": "/api/v1"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - Simple working version"""
    from datetime import datetime
    
    services = {
        "api": "healthy",
        "postgres": "checking",
        "redis": "checking"
    }
    
    # Always return a valid HealthResponse
    return HealthResponse(
        status="degraded",  # Default to degraded until we verify services
        timestamp=datetime.now().isoformat(),
        services=services
    )
@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar nuevo usuario"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError
        
        # Verificar si usuario ya existe
        result = await db.execute(
            select(User).where(
                (User.username == user.username) | (User.email == user.email)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserResponse(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name
        )
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/auth/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Iniciar sesión y obtener token JWT"""
    if not DB_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from sqlalchemy import select
    
    # Buscar usuario
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        database_status="available" if DB_AVAILABLE else "unavailable",
        redis_status="available" if REDIS_AVAILABLE else "unavailable"
    )

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener información del usuario actual"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name
    )

@app.get("/api/v1/diet/calculate")
async def calculate_diet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calcular dieta básica (ejemplo)"""
    return {
        "user": current_user.username,
        "calculation": "basic_diet_plan",
        "calories": 2000,
        "protein_g": 150,
        "carbs_g": 200,
        "fat_g": 67,
        "timestamp": datetime.now().isoformat()
    }
    return response_data
