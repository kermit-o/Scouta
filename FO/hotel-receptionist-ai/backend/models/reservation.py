"""
Modelos de datos para reservas
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Guest(Base):
    """Modelo de huésped"""
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
    
    # Relaciones
    reservations = relationship("Reservation", back_populates="guest")
    
class Reservation(Base):
    """Modelo de reserva"""
    __tablename__ = "reservations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_id = Column(String, ForeignKey("guests.id"), nullable=False)
    room_type = Column(String(50), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    special_requests = Column(String(500))
    status = Column(String(20), default="confirmed")  # confirmed, cancelled, checked_in, checked_out
    total_price = Column(Float, nullable=False)
    payment_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    guest = relationship("Guest", back_populates="reservations")
    
class RoomType(Base):
    """Modelo de tipo de habitación"""
    __tablename__ = "room_types"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    base_price = Column(Float, nullable=False)
    max_guests = Column(Integer, nullable=False)
    amenities = Column(String(500))  # JSON como string
    available_count = Column(Integer, default=0)
    image_url = Column(String(500))
