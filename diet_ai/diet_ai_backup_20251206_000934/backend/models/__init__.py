from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Importar todos los modelos
from .user_models import User, UserProfile
from .diet_models import DietPlan, Meal, MealItem
from .food_models import FoodItem, Recipe, Ingredient
from .inventory_models import InventoryItem, ShoppingList
from .ai_models import FoodAnalysis, PhotoLog
