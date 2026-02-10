"""
Auto-generated CRUD service for Product.

Generated from lego_backend/service_crud.py.j2.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models_product import Product
from schemas_product import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
)


def get_product(db: Session, id: int) -> Optional[Product]:
    return (
        db.query(Product)
        .filter(Product.id == id)
        .first()
    )


def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, data: ProductCreate) -> Product:
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_product(
    db: Session,
    id: int,
    data: ProductUpdate,
) -> Optional[Product]:
    obj = get_product(db, id)
    if not obj:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_product(db: Session, id: int) -> bool:
    obj = get_product(db, id)
    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True