"""
Dependencias de FastAPI para autenticación
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from .utils import get_current_user, verify_token

# Esquema OAuth2 para extraer token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False  # Permite endpoints públicos y protegidos
)

async def get_current_active_user(token: Optional[str] = Depends(oauth2_scheme)):
    """Dependencia para obtener usuario actual activo"""
    if token is None:
        # Permitir acceso anónimo pero marcar como no autenticado
        return None
    
    try:
        user_data = get_current_user(token)
        
        # Verificar que el usuario esté activo
        if not user_data.get("payload", {}).get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_auth(current_user = Depends(get_current_active_user)):
    """Dependencia que requiere autenticación"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def optional_auth(current_user = Depends(get_current_active_user)):
    """Dependencia que permite autenticación opcional"""
    return current_user
