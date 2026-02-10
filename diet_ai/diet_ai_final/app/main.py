"""
DietAI - API Principal
Una aplicación completa para gestión de dietas con IA
"""
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import jwt
from passlib.context import CryptContext
import json
import numpy as np
from PIL import Image
import io
import base64

# ================= CONFIGURACIÓN =================
class Config:
    SECRET_KEY = "dietai-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DATABASE_URL = "sqlite:///./dietai.db"  # Temporal, luego PostgreSQL

# ================= APLICACIÓN =================
app = FastAPI(
    title="DietAI API",
    description="Sistema inteligente para gestión de dietas y nutrición",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= SEGURIDAD =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ================= MODELOS =================
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Goal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[Gender] = None

class UserProfile(BaseModel):
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    goal: Goal
    activity_level: ActivityLevel
    dietary_restrictions: List[str] = []
    allergies: List[str] = []
    workout_days_per_week: int = Field(3, ge=0, le=7)

class DietRequest(BaseModel):
    profile: UserProfile

class FoodAnalysisRequest(BaseModel):
    image_base64: Optional[str] = None

class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    expiry_date: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    is_active: bool

class DietPlanResponse(BaseModel):
    daily_calories: int
    macros: Dict[str, float]
    meals_per_day: int
    sample_meals: List[str]
    shopping_list: List[str]
    recommendations: List[str]

class FoodAnalysisResponse(BaseModel):
    detected_foods: List[str]
    confidence_scores: List[float]
    estimated_calories: int
    estimated_macros: Dict[str, float]
    ingredients: List[str]
    health_score: float
    suggestions: List[str]

# ================= BASE DE DATOS EN MEMORIA (TEMPORAL) =================
class Database:
    users = {}
    profiles = {}
    diet_plans = {}
    food_analyses = {}
    inventory = {}
    
    user_counter = 1
    
    @classmethod
    def create_user(cls, user_data: dict):
        user_id = cls.user_counter
        cls.user_counter += 1
        
        user = {
            "id": user_id,
            "email": user_data["email"],
            "username": user_data["username"],
            "hashed_password": pwd_context.hash(user_data["password"]),
            "full_name": user_data.get("full_name"),
            "age": user_data.get("age"),
            "gender": user_data.get("gender"),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        cls.users[user_id] = user
        return user
    
    @classmethod
    def get_user_by_email(cls, email: str):
        for user in cls.users.values():
            if user["email"] == email:
                return user
        return None

# ================= UTILIDADES =================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # En producción usar: jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    encoded_jwt = f"token_{data.get('sub', 'user')}_{int(datetime.utcnow().timestamp())}"
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def calculate_calories(profile: UserProfile, gender: Optional[str] = "male", age: Optional[int] = 30):
    # Fórmula de Mifflin-St Jeor
    if gender == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * age - 161
    
    # Multiplicador de actividad
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    calories = bmr * activity_multipliers.get(profile.activity_level, 1.55)
    
    # Ajustar por objetivo
    if profile.goal == "weight_loss":
        calories -= 500
    elif profile.goal == "muscle_gain":
        calories += 300
    
    return round(calories)

def calculate_macros(calories: int, goal: Goal):
    if goal == Goal.WEIGHT_LOSS:
        protein_ratio = 0.35
        carb_ratio = 0.40
        fat_ratio = 0.25
    elif goal == Goal.MUSCLE_GAIN:
        protein_ratio = 0.30
        carb_ratio = 0.50
        fat_ratio = 0.20
    else:  # maintenance
        protein_ratio = 0.25
        carb_ratio = 0.50
        fat_ratio = 0.25
    
    return {
        "protein_g": round((calories * protein_ratio) / 4),
        "carbs_g": round((calories * carb_ratio) / 4),
        "fat_g": round((calories * fat_ratio) / 9)
    }

def analyze_food_image(image_data: bytes):
    """Análisis simulado de imagen de comida"""
    # En producción, aquí iría un modelo ML real
    return {
        "detected_foods": ["chicken", "rice", "broccoli", "carrots"],
        "confidence_scores": [0.85, 0.90, 0.75, 0.70],
        "estimated_calories": 650,
        "estimated_macros": {
            "protein_g": 45,
            "carbs_g": 75,
            "fat_g": 20
        },
        "ingredients": ["chicken breast", "white rice", "broccoli", "carrots", "garlic", "olive oil"],
        "health_score": 8.5,
        "suggestions": [
            "Excelente fuente de proteína magra",
            "Considera agregar más vegetales coloridos",
            "Porción adecuada para una comida principal",
            "El arroz integral sería una opción más saludable"
        ]
    }

def generate_shopping_list(meals: List[str]):
    """Generar lista de compras basada en comidas"""
    base_items = [
        "Pechuga de pollo", "Salmón", "Huevos", "Yogur griego",
        "Avena", "Arroz integral", "Quinoa", "Pan integral",
        "Brócoli", "Espinacas", "Zanahorias", "Tomates",
        "Aguacate", "Aceite de oliva", "Ajo", "Cebolla",
        "Frutos secos", "Plátanos", "Manzanas", "Limones"
    ]
    
    return base_items[:10]

# ================= ENDPOINTS =================
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "DietAI API",
        "version": "2.0.0",
        "description": "Sistema inteligente para gestión de dietas y nutrición",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth/register, /auth/login, /auth/me",
            "diets": "/diets/generate",
            "ai": "/ai/analyze-food, /ai/analyze-inventory",
            "inventory": "/inventory/items"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dietai-api",
        "version": "2.0.0"
    }

# ================= AUTENTICACIÓN =================
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Registro de usuario"""
    # Verificar si el usuario ya existe
    if Database.get_user_by_email(user.email):
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    db_user = Database.create_user({
        "email": user.email,
        "username": user.username,
        "password": user.password,
        "full_name": user.full_name,
        "age": user.age,
        "gender": user.gender.value if user.gender else None
    })
    
    return UserResponse(**db_user)

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login de usuario"""
    user = Database.get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return Token(access_token=access_token, token_type="bearer")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtener información del usuario actual"""
    # En producción, verificaríamos el token JWT
    # Por ahora, simulamos un usuario
    return UserResponse(
        id=1,
        email="usuario@ejemplo.com",
        username="usuario_ejemplo",
        full_name="Usuario Ejemplo",
        age=30,
        gender="male",
        is_active=True
    )

# ================= DIETAS =================
@app.post("/diets/generate", response_model=DietPlanResponse)
async def generate_diet_plan(request: DietRequest, current_user: dict = Depends(get_current_user)):
    """Generar plan de dieta personalizado"""
    
    # Calcular calorías
    daily_calories = calculate_calories(
        request.profile,
        gender=current_user.gender,
        age=current_user.age or 30
    )
    
    # Calcular macros
    macros = calculate_macros(daily_calories, request.profile.goal)
    
    # Generar comidas de ejemplo basadas en el perfil
    meals_per_day = 5 if request.profile.goal == Goal.WEIGHT_LOSS else 6
    
    sample_meals = [
        "Desayuno: Avena con frutas y huevos revueltos",
        "Media mañana: Yogur griego con nueces",
        "Almuerzo: Pollo a la plancha con arroz integral y ensalada",
        "Merienda: Batido de proteínas con plátano",
        "Cena: Salmón al horno con vegetales asados",
        "Post-cena (opcional): Requesón con canela"
    ][:meals_per_day]
    
    # Generar lista de compras
    shopping_list = generate_shopping_list(sample_meals)
    
    # Recomendaciones personalizadas
    recommendations = [
        f"Objetivo: {request.profile.goal.replace('_', ' ').title()}",
        f"Actividad: {request.profile.activity_level.replace('_', ' ').title()}",
        f"Entrenamientos: {request.profile.workout_days_per_week} días/semana",
        "Bebe al menos 2 litros de agua al día",
        "Considera dividir tus comidas en 5-6 tiempos"
    ]
    
    if request.profile.dietary_restrictions:
        recommendations.append(
            f"Restricciones dietéticas: {', '.join(request.profile.dietary_restrictions)}"
        )
    
    return DietPlanResponse(
        daily_calories=daily_calories,
        macros=macros,
        meals_per_day=meals_per_day,
        sample_meals=sample_meals,
        shopping_list=shopping_list,
        recommendations=recommendations
    )

# ================= IA - ANÁLISIS DE COMIDA =================
@app.post("/ai/analyze-food", response_model=FoodAnalysisResponse)
async def analyze_food(
    file: UploadFile = File(None),
    image_base64: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Analizar imagen de comida usando IA"""
    
    image_data = None
    
    if file:
        # Procesar archivo subido
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        image_data = await file.read()
        
    elif image_base64:
        # Procesar imagen en base64
        try:
            if "base64," in image_base64:
                image_base64 = image_base64.split("base64,")[1]
            image_data = base64.b64decode(image_base64)
        except:
            raise HTTPException(status_code=400, detail="Formato base64 inválido")
    
    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar una imagen o base64")
    
    # Analizar la imagen
    analysis = analyze_food_image(image_data)
    
    return FoodAnalysisResponse(**analysis)

@app.post("/ai/analyze-inventory")
async def analyze_inventory_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Analizar imagen de inventario/despensa"""
    
    # Simulación de análisis de inventario
    return {
        "detected_items": [
            {"item": "Manzanas", "quantity": 5, "unit": "unidades", "confidence": 0.95},
            {"item": "Huevos", "quantity": 12, "unit": "unidades", "confidence": 0.90},
            {"item": "Pan integral", "quantity": 1, "unit": "paquete", "confidence": 0.85},
            {"item": "Leche", "quantity": 1, "unit": "litro", "confidence": 0.80},
            {"item": "Pollo", "quantity": 2, "unit": "pechugas", "confidence": 0.75}
        ],
        "expiry_alerts": [
            "La leche expira en 3 días",
            "Los huevos expiran en 7 días"
        ],
        "shopping_suggestions": [
            "Considera comprar más vegetales verdes",
            "Necesitarás más frutas para la semana"
        ]
    }

# ================= INVENTARIO =================
@app.get("/inventory/items")
async def get_inventory_items(current_user: dict = Depends(get_current_user)):
    """Obtener items del inventario"""
    # Datos de ejemplo
    return [
        {
            "id": 1,
            "name": "Manzanas",
            "category": "Frutas",
            "quantity": 5,
            "unit": "unidades",
            "expiry_date": "2024-12-15",
            "photo_url": None
        },
        {
            "id": 2,
            "name": "Huevos",
            "category": "Proteínas",
            "quantity": 12,
            "unit": "unidades",
            "expiry_date": "2024-12-10",
            "photo_url": None
        },
        {
            "id": 3,
            "name": "Arroz integral",
            "category": "Granos",
            "quantity": 1,
            "unit": "kg",
            "expiry_date": "2025-06-01",
            "photo_url": None
        }
    ]

@app.post("/inventory/items")
async def add_inventory_item(
    item: InventoryItem,
    current_user: dict = Depends(get_current_user)
):
    """Agregar item al inventario"""
    return {
        "message": "Item agregado al inventario",
        "item": item.dict(),
        "id": 123,
        "created_at": datetime.utcnow().isoformat()
    }

# ================= EJECUCIÓN =================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
