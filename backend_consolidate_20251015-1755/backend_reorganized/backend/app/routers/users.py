from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import models, schemas
from sqlalchemy import select, func

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserRead])
def list_users(limit: int = 50, offset: int = 0, response: Response = None, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    total = db.scalar(select(func.count(models.User.id)))
    stmt = select(models.User).order_by(models.User.id).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    response.headers["X-Total-Count"] = str(total or 0)
    return [schemas.UserRead(id=u.id, email=u.email, full_name=u.full_name, is_active=u.is_active) for u in rows]

@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(func.count()).select_from(models.User).where(models.User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = models.User(email=payload.email, full_name=payload.full_name, is_active=payload.is_active)
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.email and payload.email != user.email:
        exists = db.scalar(select(func.count()).select_from(models.User).where(models.User.email == payload.email))
        if exists:
            raise HTTPException(status_code=409, detail="Email already exists")
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
