from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

# Intentar importar config, sino usar valores por defecto
try:
    from core.config import settings
except ImportError:
    class SimpleSettings:
        secret_key = "dummy-secret-key-for-development"
        algorithm = "HS256"
    
    settings = SimpleSettings()

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Modelos Pydantic
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    email: str
    username: str
    is_active: bool

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Registro de usuario simplificado"""
    return UserResponse(
        email=user.email,
        username=user.username,
        is_active=True
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login simplificado"""
    token_data = {
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    dummy_token = "dummy_jwt_token_for_now"
    
    return Token(
        access_token=dummy_token,
        token_type="bearer"
    )

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtener usuario actual"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }
