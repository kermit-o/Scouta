# backend/models/reservation.py
"""
Modelos de datos para reservas
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.core.database import Base  # <- USAR LA BASE ÚNICA

class Guest(Base):
    __tablename__ = "guests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    country = Column(String(100))
    language_preference = Column(String(10), default="es")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reservations = relationship("Reservation", back_populates="guest")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_id = Column(String, ForeignKey("guests.id"), nullable=True)

    room_type = Column(String(50), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    special_requests = Column(String, nullable=True)

    status = Column(String(20), default="confirmed")
    total_price = Column(Float, nullable=False)
    payment_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    guest = relationship("Guest", back_populates="reservations")
