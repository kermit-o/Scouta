from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas


router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post(
    "/", response_model=schemas.OrderRead, status_code=status.HTTP_201_CREATED
)
def create_order(
    payload: schemas.OrderCreate,
    db: Session = Depends(get_db),
) -> schemas.OrderRead:
    # Load products and compute total
    product_ids = [item.product_id for item in payload.items]
    products = (
        db.query(models.Product)
        .filter(models.Product.id.in_(product_ids), models.Product.is_active.is_(True))
        .all()
    )
    products_map = {p.id: p for p in products}

    if len(products_map) != len(product_ids):
        raise HTTPException(status_code=400, detail="One or more products not found")

    total = 0.0
    order_items: list[models.OrderItem] = []

    for item in payload.items:
        product = products_map[item.product_id]
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.id}",
            )
        unit_price = float(product.price)
        total += unit_price * item.quantity

        order_items.append(
            models.OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=unit_price,
            )
        )
        product.stock -= item.quantity

    order = models.Order(
        user_id=payload.user_id,
        total_amount=total,
        currency="EUR",
        status="pending",
        items=order_items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[schemas.OrderRead])
def list_orders(db: Session = Depends(get_db)) -> List[schemas.OrderRead]:
    return db.query(models.Order).all()


@router.get("/{order_id}", response_model=schemas.OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> schemas.OrderRead:
    order = db.query(models.Order).get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
