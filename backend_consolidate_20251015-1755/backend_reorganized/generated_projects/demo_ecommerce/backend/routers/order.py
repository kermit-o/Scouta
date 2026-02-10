"""
Auto-generated FastAPI CRUD router for Order.

Generated from lego_backend/router_crud_fastapi.py.j2.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database.database import get_db
from schemas_order import (
    OrderCreate,
    OrderUpdate,
    OrderRead,
)
from services_order import (
    get_order,
    list_orders,
    create_order,
    update_order,
    delete_order,
)


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", response_model=List[OrderRead])
def list_orders_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return list_orders(db=db, skip=skip, limit=limit)


@router.get("/{ id }", response_model=OrderRead)
def get_order_endpoint(
    id: int,
    db: Session = Depends(get_db),
):
    obj = get_order(db=db, id=id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return obj


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    payload: OrderCreate,
    db: Session = Depends(get_db),
):
    return create_order(db=db, data=payload)


@router.put("/{ id }", response_model=OrderRead)
def update_order_endpoint(
    id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
):
    obj = update_order(db=db, id=id, data=payload)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return obj


@router.delete("/{ id }", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_endpoint(
    id: int,
    db: Session = Depends(get_db),
):
    ok = delete_order(db=db, id=id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return None