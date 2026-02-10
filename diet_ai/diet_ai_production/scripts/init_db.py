#!/usr/bin/env python3
"""
Initialize the database with tables
"""
import os
import sys
from sqlalchemy import create_engine
from database.database import Base
from database.models.user import User
from database.models.diet import Diet, MealPlan
from database.models.inventory import InventoryItem, Category
from database.models.recipe import Recipe, Ingredient
from database.models.nutrition import NutritionInfo

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def init_database():
    """Create all tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    print(f"Creating tables in database: {settings.DATABASE_URL}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
