"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from core.database.database import get_db
from models.user import User
from core.auth.auth import AuthManager

router = APIRouter()
security = HTTPBearer()
auth_manager = AuthManager()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(request: RegisterRequest, db=Depends(get_db)):
    """Register a new user"""
    try:
        user = auth_manager.register_user(db, request.email, request.password)
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    """Login user"""
    try:
        token = auth_manager.authenticate_user(db, request.email, request.password)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    """Get current user info"""
    try:
        user = auth_manager.get_current_user(db, credentials.credentials)
        return {"email": user.email, "id": user.id, "is_active": user.is_active}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
