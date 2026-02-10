"""
Auto-generated FastAPI CRUD router for Product.

Generated from lego_backend/router_crud_fastapi.py.j2.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database.database import get_db
from schemas_product import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
)
from services_product import (
    get_product,
    list_products,
    create_product,
    update_product,
    delete_product,
)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=List[ProductRead])
def list_products_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return list_products(db=db, skip=skip, limit=limit)


@router.get("/{ id }", response_model=ProductRead)
def get_product_endpoint(
    id: int,
    db: Session = Depends(get_db),
):
    obj = get_product(db=db, id=id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return obj


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    return create_product(db=db, data=payload)


@router.put("/{ id }", response_model=ProductRead)
def update_product_endpoint(
    id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    obj = update_product(db=db, id=id, data=payload)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return obj


@router.delete("/{ id }", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    id: int,
    db: Session = Depends(get_db),
):
    ok = delete_product(db=db, id=id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return None