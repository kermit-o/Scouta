"""
Auto-generated Pydantic schemas for Product.

Generated from lego_backend/schema_pydantic.py.j2.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None
    price: float
    is_active: bool


class ProductCreate(ProductBase):
    """Schema used for creation."""
    pass


class ProductUpdate(BaseModel):
    """Schema used for partial updates."""
    name: Optional[str] = None
    description: Optional[str | None] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class ProductRead(ProductBase):
    """Schema returned to clients."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True