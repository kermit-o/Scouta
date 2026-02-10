"""
DietAI API - Versión minimalista para debugging
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="DietAI API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "DietAI API funcionando!",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "online"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "dietai"}

@app.get("/test")
async def test():
    return {"test": "ok", "python_version": "3.11"}

@app.post("/auth/register")
async def register(email: str, username: str, password: str):
    return {
        "message": "Usuario registrado (simulado)",
        "user": {"email": email, "username": username}
    }

@app.post("/diets/generate")
async def generate_diet(
    age: int,
    gender: str,
    height: float,
    weight: float,
    activity: str = "moderate",
    goal: str = "weight_loss"
):
    # Cálculo simple
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    calories = bmr * 1.55  # moderate activity
    
    return {
        "daily_calories": round(calories),
        "macros": {
            "protein_g": round(calories * 0.3 / 4),
            "carbs_g": round(calories * 0.5 / 4),
            "fat_g": round(calories * 0.2 / 9)
        },
        "goal": goal,
        "message": "Dieta generada exitosamente"
    }
