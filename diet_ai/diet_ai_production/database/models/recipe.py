"""
Recipe and ingredient models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cuisine = Column(String(100))  # Italian, Mexican, Asian, etc.
    difficulty = Column(String(20))  # easy, medium, hard
    preparation_time = Column(Integer)  # in minutes
    cooking_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    
    # Instructions
    instructions = Column(Text)
    tips = Column(Text)
    
    # Nutritional information (per serving)
    calories_per_serving = Column(Float)
    protein_per_serving = Column(Float)
    carbs_per_serving = Column(Float)
    fat_per_serving = Column(Float)
    
    # Metadata
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name={self.name})>"

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    name = Column(String(255), nullable=False)
    amount = Column(Float)
    unit = Column(String(50))  # g, kg, ml, L, pieces, tbsp, tsp
    notes = Column(Text)
    
    # Nutritional information for this ingredient
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name={self.name}, amount={self.amount})>"
