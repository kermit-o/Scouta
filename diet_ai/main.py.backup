from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="Dieta API", version="1.0")

@app.get("/")
async def root():
    return {"message": "Dieta API v1.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/foods")
async def list_foods(category: Optional[str] = None):
    foods = [
        {"id": 1, "name": "Pollo", "category": "protein"},
        {"id": 2, "name": "Arroz", "category": "carb"},
        {"id": 3, "name": "Aguacate", "category": "fat"}
    ]
    
    if category:
        filtered = [f for f in foods if f["category"] == category]
        return {"foods": filtered}
    
    return {"foods": foods}

# Modelo para TDEE
class UserProfile(BaseModel):
    age: int
    weight_kg: float
    height_cm: float
    gender: str
    activity_level: str
    goal: str

@app.post("/calculate/tdee")
async def calculate_tdee(profile: UserProfile):
    # Fórmula simple
    if profile.gender.lower() == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161
    
    # Multiplicador actividad
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    tdee = bmr * multipliers.get(profile.activity_level.lower(), 1.2)
    
    return {
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "goal": profile.goal,
        "message": "Calculation successful"
    }

@app.get("/test")
async def test_endpoint():
    return {"test": "ok", "endpoints": ["/", "/health", "/foods", "/calculate/tdee"]}
