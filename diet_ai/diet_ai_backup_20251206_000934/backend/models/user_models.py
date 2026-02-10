# diet_ai/backend/models/user_models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Datos personales
    full_name = Column(String)
    age = Column(Integer)
    gender = Column(String)  # 'male', 'female', 'other'
    height_cm = Column(Float)
    weight_kg = Column(Float)
    
    # Objetivos
    goal = Column(String)  # 'weight_loss', 'muscle_gain', 'maintenance', 'performance'
    target_weight = Column(Float)
    weekly_goal = Column(String)  # 'lose_0.5kg', 'gain_0.5kg', 'maintain'
    
    # Actividad
    activity_level = Column(String)  # 'sedentary', 'light', 'moderate', 'active', 'very_active'
    workout_days = Column(Integer)  # días por semana
    workout_intensity = Column(String)  # 'low', 'medium', 'high'
    
    # Preferencias
    dietary_restrictions = Column(JSON)  # ['vegetarian', 'vegan', 'gluten-free', etc.]
    allergies = Column(JSON)  # ['peanuts', 'dairy', 'shellfish', etc.]
    disliked_foods = Column(JSON)
    preferred_cuisines = Column(JSON)
    
    # Macronutrientes objetivo (calculados)
    daily_calories = Column(Float)
    daily_protein_g = Column(Float)
    daily_carbs_g = Column(Float)
    daily_fat_g = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())