from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# ---------- User ----------

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Product ----------

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "EUR"
    is_active: bool = True
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    stock: Optional[int] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Order / OrderItem ----------

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderRead(BaseModel):
    id: int
    user_id: int
    total_amount: float
    currency: str
    status: str
    created_at: datetime
    items: List[OrderItemRead]

    class Config:
        from_attributes = True
