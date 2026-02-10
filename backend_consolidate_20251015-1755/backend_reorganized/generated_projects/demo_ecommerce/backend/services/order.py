"""
Auto-generated CRUD service for Order.

Generated from lego_backend/service_crud.py.j2.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models_order import Order
from schemas_order import (
    OrderCreate,
    OrderUpdate,
    OrderRead,
)


def get_order(db: Session, id: int) -> Optional[Order]:
    return (
        db.query(Order)
        .filter(Order.id == id)
        .first()
    )


def list_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).offset(skip).limit(limit).all()


def create_order(db: Session, data: OrderCreate) -> Order:
    obj = Order(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_order(
    db: Session,
    id: int,
    data: OrderUpdate,
) -> Optional[Order]:
    obj = get_order(db, id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_order(db: Session, id: int) -> bool:
    obj = get_order(db, id)
    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True