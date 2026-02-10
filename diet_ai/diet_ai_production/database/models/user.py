"""
User model for authentication and profiles
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Profile information
    age = Column(Integer)
    weight = Column(Float)  # in kg
    height = Column(Float)  # in cm
    gender = Column(String(10))  # male, female, other
    activity_level = Column(String(50))  # sedentary, light, moderate, active, very_active
    goal = Column(String(50))  # lose_weight, gain_muscle, maintain, improve_health
    target_weight = Column(Float)
    allergies = Column(Text)  # JSON string or comma separated
    dietary_preferences = Column(Text)  # vegetarian, vegan, keto, etc.
    daily_calorie_target = Column(Integer)
    
    # Relationships
    diets = relationship("Diet", back_populates="user")
    inventory_items = relationship("InventoryItem", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
