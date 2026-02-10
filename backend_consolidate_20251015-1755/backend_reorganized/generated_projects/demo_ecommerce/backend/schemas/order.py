"""
Auto-generated Pydantic schemas for Order.

Generated from lego_backend/schema_pydantic.py.j2.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class OrderBase(BaseModel):
    reference: str
    total_amount: float
    status: str


class OrderCreate(OrderBase):
    """Schema used for creation."""
    pass


class OrderUpdate(BaseModel):
    """Schema used for partial updates."""
    reference: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None


class OrderRead(OrderBase):
    """Schema returned to clients."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True