from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    obj = models.User(email=user.email, full_name=user.full_name, is_active=user.is_active)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj
