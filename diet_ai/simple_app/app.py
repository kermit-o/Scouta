from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(title="DietAI Simple", version="1.0.0")

class User(BaseModel):
    email: str
    username: str
    password: str

class DietRequest(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    activity: str = "moderate"
    goal: str = "weight_loss"

@app.get("/")
async def root():
    return {"message": "DietAI API Simple", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/register")
async def register(user: User):
    return {
        "message": "Usuario registrado",
        "user": {
            "email": user.email,
            "username": user.username,
            "id": 1
        }
    }

@app.post("/generate-diet")
async def generate_diet(request: DietRequest):
    # Cálculo básico
    if request.gender.lower() == "male":
        bmr = 10 * request.weight + 6.25 * request.height - 5 * request.age + 5
    else:
        bmr = 10 * request.weight + 6.25 * request.height - 5 * request.age - 161
    
    calories = bmr * 1.55
    
    return {
        "success": True,
        "data": {
            "calories": round(calories),
            "protein_g": round(calories * 0.3 / 4),
            "carbs_g": round(calories * 0.5 / 4),
            "fat_g": round(calories * 0.2 / 9),
            "meals_per_day": 5,
            "goal": request.goal
        }
    }

@app.post("/analyze-food")
async def analyze_food(image: UploadFile = File(...)):
    return {
        "filename": image.filename,
        "analysis": {
            "detected_foods": ["pollo", "arroz", "vegetales"],
            "calories": 650,
            "healthy_score": 8
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
