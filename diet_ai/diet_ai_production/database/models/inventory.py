"""
Inventory and food storage models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    items = relationship("InventoryItem", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    brand = Column(String(255))
    
    # Storage information
    quantity = Column(Float, default=1.0)
    unit = Column(String(50))  # kg, g, L, ml, pieces
    expiry_date = Column(DateTime)
    
    # Location tracking
    storage_location = Column(String(100))  # pantry, fridge, freezer
    shelf = Column(String(50))
    
    # Nutritional information (per unit)
    calories_per_unit = Column(Float)
    protein_per_unit = Column(Float)
    carbs_per_unit = Column(Float)
    fat_per_unit = Column(Float)
    
    # Tracking
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    is_favorite = Column(Boolean, default=False)
    last_used = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="inventory_items")
    category = relationship("Category", back_populates="items")
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, name={self.name}, quantity={self.quantity})>"
