"""
Servicio para gestión de usuarios
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from security.utils import get_password_hash, verify_password, create_user_token
from schemas.auth import UserCreate, UserUpdate, UserResponse, Token

logger = logging.getLogger(__name__)

class UserService:
    """Servicio para operaciones de usuario"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            existing_user = db.execute(
                "SELECT id FROM users WHERE email = :email OR username = :username",
                {"email": user_data.email, "username": user_data.username}
            ).fetchone()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email o nombre de usuario ya está registrado"
                )
            
            # Hash de la contraseña
            hashed_password = get_password_hash(user_data.password)
            
            # Insertar usuario
            result = db.execute(
                """
                INSERT INTO users (email, username, hashed_password, full_name, is_active)
                VALUES (:email, :username, :password, :full_name, :is_active)
                RETURNING id, email, username, full_name, is_active, created_at
                """,
                {
                    "email": user_data.email,
                    "username": user_data.username,
                    "password": hashed_password,
                    "full_name": user_data.full_name,
                    "is_active": True
                }
            )
            
            db.commit()
            new_user = result.fetchone()
            
            if not new_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear usuario"
                )
            
            # Crear token para el nuevo usuario
            token = create_user_token(
                user_id=new_user[0],
                email=new_user[1],
                username=new_user[2],
                is_active=new_user[4]
            )
            
            return {
                "user": {
                    "id": new_user[0],
                    "email": new_user[1],
                    "username": new_user[2],
                    "full_name": new_user[3],
                    "is_active": new_user[4],
                    "created_at": new_user[5]
                },
                "token": token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Dict[str, Any]:
        """Autenticar usuario con email y contraseña"""
        try:
            # Buscar usuario
            user = db.execute(
                """
                SELECT id, email, username, full_name, hashed_password, is_active, created_at
                FROM users 
                WHERE email = :email
                """,
                {"email": email}
            ).fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verificar contraseña
            if not verify_password(password, user[4]):  # hashed_password está en índice 4
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verificar que el usuario esté activo
            if not user[5]:  # is_active está en índice 5
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario inactivo",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Crear token
            token = create_user_token(
                user_id=user[0],
                email=user[1],
                username=user[2],
                is_active=user[5]
            )
            
            return {
                "user": {
                    "id": user[0],
                    "email": user[1],
                    "username": user[2],
                    "full_name": user[3],
                    "is_active": user[5],
                    "created_at": user[6]
                },
                "token": token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID"""
        try:
            user = db.execute(
                """
                SELECT id, email, username, full_name, is_active, created_at, updated_at
                FROM users 
                WHERE id = :user_id
                """,
                {"user_id": user_id}
            ).fetchone()
            
            if not user:
                return None
            
            return {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "full_name": user[3],
                "is_active": user[4],
                "created_at": user[5],
                "updated_at": user[6]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por email"""
        try:
            user = db.execute(
                """
                SELECT id, email, username, full_name, is_active, created_at, updated_at
                FROM users 
                WHERE email = :email
                """,
                {"email": email}
            ).fetchone()
            
            if not user:
                return None
            
            return {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "full_name": user[3],
                "is_active": user[4],
                "created_at": user[5],
                "updated_at": user[6]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            return None
    
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """Actualizar usuario"""
        try:
            # Construir query dinámica
            updates = []
            params = {"user_id": user_id}
            
            if update_data.username is not None:
                updates.append("username = :username")
                params["username"] = update_data.username
            
            if update_data.full_name is not None:
                updates.append("full_name = :full_name")
                params["full_name"] = update_data.full_name
            
            if update_data.password is not None:
                updates.append("hashed_password = :password")
                params["password"] = get_password_hash(update_data.password)
            
            if not updates:
                return None
            
            # Agregar updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            query = f"""
                UPDATE users 
                SET {', '.join(updates)}
                WHERE id = :user_id
                RETURNING id, email, username, full_name, is_active, created_at, updated_at
            """
            
            result = db.execute(query, params)
            db.commit()
            
            updated_user = result.fetchone()
            
            if not updated_user:
                return None
            
            return {
                "id": updated_user[0],
                "email": updated_user[1],
                "username": updated_user[2],
                "full_name": updated_user[3],
                "is_active": updated_user[4],
                "created_at": updated_user[5],
                "updated_at": updated_user[6]
            }
            
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
