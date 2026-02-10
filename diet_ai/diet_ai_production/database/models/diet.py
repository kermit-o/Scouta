"""
Diet and meal planning models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class Diet(Base):
    __tablename__ = "diets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    goal = Column(String(50))  # lose_weight, gain_muscle, maintain, improve_health
    difficulty = Column(String(20))  # easy, medium, hard
    duration_days = Column(Integer)  # Duration in days
    daily_calories = Column(Integer)
    
    # Macronutrient targets
    protein_percentage = Column(Float)  # 20-35%
    carbs_percentage = Column(Float)    # 45-65%
    fat_percentage = Column(Float)      # 20-35%
    
    # Restrictions
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_lactose_free = Column(Boolean, default=False)
    allergies = Column(Text)  # JSON string
    
    # Metadata
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="diets")
    meal_plans = relationship("MealPlan", back_populates="diet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Diet(id={self.id}, name={self.name}, goal={self.goal})>"

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    diet_id = Column(Integer, ForeignKey("diets.id"))
    day_number = Column(Integer)  # Day 1, 2, 3, etc.
    meal_type = Column(String(50))  # breakfast, lunch, dinner, snack
    meal_time = Column(String(50))  # Morning, Noon, Evening, Night
    
    # Meal details
    meal_name = Column(String(255))
    description = Column(Text)
    preparation_time = Column(Integer)  # in minutes
    calories = Column(Integer)
    
    # Macronutrients
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    
    # Instructions
    instructions = Column(Text)
    tips = Column(Text)
    
    # Relationships
    diet = relationship("Diet", back_populates="meal_plans")
    
    def __repr__(self):
        return f"<MealPlan(id={self.id}, day={self.day_number}, meal={self.meal_type})>"
