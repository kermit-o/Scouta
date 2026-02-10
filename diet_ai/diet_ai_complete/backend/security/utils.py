"""
Utilidades de seguridad: hash de contraseñas y verificación JWT
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from .config import security_config

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=security_config.PWD_CONTEXT_SCHEMES, deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar si la contraseña plana coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Obtener hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT de acceso"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + security_config.get_token_expiry()
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, security_config.SECRET_KEY, algorithm=security_config.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, security_config.SECRET_KEY, algorithms=[security_config.ALGORITHM])
        
        # Verificar tipo de token
        if payload.get("type") != "access":
            raise JWTError("Tipo de token inválido")
        
        # Verificar expiración (jwt.decode ya lo hace, pero por si acaso)
        expire = payload.get("exp")
        if expire is None or datetime.fromtimestamp(expire) < datetime.utcnow():
            raise JWTError("Token expirado")
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str) -> Dict[str, Any]:
    """Obtener usuario actual desde token JWT"""
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: no contiene sub",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"id": user_id, "payload": payload}

def create_user_token(user_id: int, email: str, username: str, is_active: bool = True) -> str:
    """Crear token JWT para un usuario"""
    token_data = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "is_active": is_active,
        "iat": datetime.utcnow(),
    }
    
    return create_access_token(token_data)
