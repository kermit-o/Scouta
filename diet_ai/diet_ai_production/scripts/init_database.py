#!/usr/bin/env python3
"""
Initialize database tables
"""
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import engine, Base
from database.models.user import User
from database.models.diet import Diet, MealPlan
from database.models.inventory import InventoryItem, Category
from database.models.recipe import Recipe, Ingredient

async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
