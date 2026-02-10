from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas


router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[schemas.ProductRead])
def list_products(db: Session = Depends(get_db)) -> List[schemas.ProductRead]:
    return db.query(models.Product).filter(models.Product.is_active.is_(True)).all()


@router.post(
    "/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED
)
def create_product(
    payload: schemas.ProductCreate,
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    product = models.Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=schemas.ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    product = db.query(models.Product).get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    product = db.query(models.Product).get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> None:
    product = db.query(models.Product).get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None
