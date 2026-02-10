"""
Endpoints de Autenticación - Versión corregida
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importaciones corregidas
from backend.app.core.database.database import get_db
from backend.app.core.database.models import User
from backend.app.auth import AuthManager
from backend.app.user_manager import UserManager

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    user_manager = UserManager(db)
    
    try:
        user = user_manager.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        access_token = AuthManager.create_access_token(user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "plan": user.plan
            }
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    user_manager = UserManager(db)
    
    user = user_manager.authenticate_user(
        email=login_data.email,
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = AuthManager.create_access_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan
        }
    }

@router.get("/me")
async def get_current_user(current_user: User = Depends(AuthManager.get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "plan": current_user.plan,
        "projects_used_this_month": current_user.projects_used_this_month,
        "max_projects_per_month": current_user.max_projects_per_month
    }
