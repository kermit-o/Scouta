"""
Router para autenticación y gestión de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from security.dependencies import get_current_active_user, require_auth
from schemas.auth import UserCreate, UserResponse, Token, AuthResponse, UserUpdate
from services.user_service import UserService
from database_simple import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Registrar nuevo usuario
    
    - **email**: Email válido
    - **username**: Nombre de usuario (3-50 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres, debe contener al menos un número)
    - **full_name**: Nombre completo (opcional)
    """
    result = UserService.create_user(db, user_data)
    
    return {
        "user": UserResponse(**result["user"]),
        "token": Token(
            access_token=result["token"],
            token_type="bearer",
            expires_in=60 * 60 * 24 * 7  # 7 días en segundos
        )
    }

@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Iniciar sesión
    
    - **username**: Email del usuario
    - **password**: Contraseña
    """
    result = UserService.authenticate_user(db, form_data.username, form_data.password)
    
    return {
        "user": UserResponse(**result["user"]),
        "token": Token(
            access_token=result["token"],
            token_type="bearer",
            expires_in=60 * 60 * 24 * 7  # 7 días en segundos
        )
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener información del usuario actual
    
    Requiere autenticación
    """
    user_id = current_user["id"]
    user = UserService.get_user_by_id(db, int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UserResponse(**user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualizar información del usuario actual
    
    Requiere autenticación
    """
    user_id = current_user["id"]
    updated_user = UserService.update_user(db, int(user_id), update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar"
        )
    
    return UserResponse(**updated_user)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refrescar token de acceso
    
    Requiere autenticación
    """
    user_id = current_user["id"]
    user = UserService.get_user_by_id(db, int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Crear nuevo token
    token = create_user_token(
        user_id=user["id"],
        email=user["email"],
        username=user["username"],
        is_active=user["is_active"]
    )
    
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=60 * 60 * 24 * 7  # 7 días en segundos
    )

@router.get("/validate")
async def validate_token(
    current_user: dict = Depends(optional_auth)
) -> Any:
    """
    Validar token JWT
    
    - Si el token es válido: retorna información del usuario
    - Si no hay token o es inválido: retorna estado no autenticado
    """
    if current_user is None:
        return {"authenticated": False, "message": "No autenticado"}
    
    return {
        "authenticated": True,
        "user_id": current_user["id"],
        "email": current_user["payload"].get("email"),
        "username": current_user["payload"].get("username"),
        "expires_at": current_user["payload"].get("exp")
    }
