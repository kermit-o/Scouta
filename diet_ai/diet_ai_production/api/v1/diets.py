from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.database import get_db

router = APIRouter(prefix="/diets", tags=["diets"])

# Modelos
class DietPlan(BaseModel):
    id: int
    name: str
    type: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    meals_per_day: int

class GenerateDietRequest(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str
    dietary_restrictions: List[str] = []

@router.get("/", response_model=List[DietPlan])
async def get_diet_plans(db: Session = Depends(get_db)):
    """Obtener planes de dieta disponibles"""
    # Por ahora devolvemos datos dummy
    return [
        {
            "id": 1,
            "name": "Pérdida de peso",
            "type": "weight_loss",
            "calories": 1800,
            "protein_g": 140,
            "carbs_g": 180,
            "fat_g": 60,
            "meals_per_day": 5
        },
        {
            "id": 2,
            "name": "Ganancia muscular",
            "type": "muscle_gain",
            "calories": 2500,
            "protein_g": 180,
            "carbs_g": 280,
            "fat_g": 80,
            "meals_per_day": 6
        }
    ]

@router.post("/generate")
async def generate_diet_plan(request: GenerateDietRequest):
    """Generar plan de dieta personalizado"""
    
    # Cálculo básico de calorías (fórmula simplificada)
    if request.gender.lower() == "male":
        bmr = 10 * request.weight_kg + 6.25 * request.height_cm - 5 * request.age + 5
    else:
        bmr = 10 * request.weight_kg + 6.25 * request.height_cm - 5 * request.age - 161
    
    # Multiplicador de actividad
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    daily_calories = bmr * activity_multipliers.get(request.activity_level, 1.2)
    
    # Ajustar por objetivo
    if request.goal == "weight_loss":
        daily_calories -= 500
    elif request.goal == "muscle_gain":
        daily_calories += 300
    
    # Calcular macros
    if request.goal == "weight_loss":
        protein_ratio = 0.35
        carb_ratio = 0.40
        fat_ratio = 0.25
    elif request.goal == "muscle_gain":
        protein_ratio = 0.30
        carb_ratio = 0.50
        fat_ratio = 0.20
    else:  # maintenance
        protein_ratio = 0.25
        carb_ratio = 0.50
        fat_ratio = 0.25
    
    return {
        "daily_calories": round(daily_calories),
        "macros": {
            "protein_g": round((daily_calories * protein_ratio) / 4),
            "carbs_g": round((daily_calories * carb_ratio) / 4),
            "fat_g": round((daily_calories * fat_ratio) / 9)
        },
        "recommended_meals_per_day": 5 if request.goal == "weight_loss" else 6,
        "goal": request.goal,
        "restrictions": request.dietary_restrictions,
        "sample_meals": [
            "Desayuno: Avena con frutas y huevos",
            "Almuerzo: Pollo con arroz y vegetales",
            "Cena: Pescado con ensalada",
            "Snacks: Frutas, yogur, nueces"
        ]
    }
