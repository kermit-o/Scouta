"""
Esquemas Pydantic para autenticación
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base para esquemas de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Esquema para creación de usuario"""
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def password_strength(cls, v):
        """Validar fortaleza de la contraseña"""
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Esquema para actualización de usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    """Esquema para respuesta de usuario"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    
class TokenPayload(BaseModel):
    """Esquema para payload del token"""
    sub: str  # user_id
    email: str
    username: str
    is_active: bool
    exp: int
    iat: int

class AuthResponse(BaseModel):
    """Respuesta de autenticación"""
    user: UserResponse
    token: Token
