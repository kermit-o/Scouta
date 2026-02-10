"""
DietAI API v2.4 - Con base de datos funcionando
"""
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar conexión a base de datos
try:
    from database_simple import get_db, test_connection, execute_query
    HAS_DATABASE = True
    logger.info("✅ Módulo de base de datos cargado")
except ImportError as e:
    logger.warning(f"❌ No se pudo cargar módulo de base de datos: {e}")
    HAS_DATABASE = False

# Crear aplicación
app = FastAPI(
    title="DietAI API v2.4",
    version="2.4.0",
    description="API inteligente para gestión de dietas con PostgreSQL funcionando",
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

# ================= ENDPOINTS =================

@app.get("/")
async def root():
    """Endpoint raíz"""
    logger.info("Acceso a endpoint raíz")
    
    db_status = "checking..."
    if HAS_DATABASE:
        success, message = test_connection()
        db_status = f"✅ {message}" if success else f"❌ {message}"
    else:
        db_status = "❌ No disponible"
    
    return {
        "message": "DietAI API v2.4",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "online",
        "version": "2.4.0",
        "database": db_status,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "database": "/db/status",
            "users": "/db/users",
            "foods": "/db/foods",
            "diets": "/diets/generate",
            "test": "/db/test"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dietai-api",
        "version": "2.4.0"
    }

@app.get("/db/status")
async def db_status():
    """Estado de la base de datos"""
    if not HAS_DATABASE:
        return {
            "database": "not_available",
            "message": "Módulo de base de datos no cargado",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    success, message = test_connection()
    
    if not success:
        return {
            "database": "error",
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Obtener información de tablas
    try:
        tables = execute_query("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as columns
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables is None:
            return {
                "database": "connected",
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "tables": "No se pudieron obtener las tablas"
            }
        
        table_info = []
        for table in tables:
            table_info.append({
                "table": table[0],
                "columns": table[1]
            })
        
        return {
            "database": "connected",
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "tables": table_info,
            "total_tables": len(table_info)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de BD: {e}")
        return {
            "database": "connected",
            "message": f"{message} (Error obteniendo tablas: {str(e)})",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/db/test")
async def db_test():
    """Endpoint de prueba para base de datos"""
    if not HAS_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible"
        )
    
    # Probar consultas básicas
    tests = []
    
    # 1. Probando versión de PostgreSQL
    version = execute_query("SELECT version()")
    if version:
        tests.append({
            "test": "Conexión a PostgreSQL",
            "status": "✅",
            "result": version[0][0].split(",")[0]
        })
    else:
        tests.append({
            "test": "Conexión a PostgreSQL",
            "status": "❌",
            "result": "Falló"
        })
    
    # 2. Contar tablas
    tables = execute_query("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    if tables:
        tests.append({
            "test": "Conteo de tablas",
            "status": "✅",
            "result": f"{tables[0][0]} tablas"
        })
    else:
        tests.append({
            "test": "Conteo de tablas",
            "status": "❌",
            "result": "Falló"
        })
    
    # 3. Ver usuarios
    users = execute_query("SELECT COUNT(*) FROM users")
    if users is not None:
        tests.append({
            "test": "Conteo de usuarios",
            "status": "✅",
            "result": f"{users[0][0]} usuarios"
        })
    else:
        tests.append({
            "test": "Conteo de usuarios",
            "status": "⚠️",
            "result": "Tabla users no existe o error"
        })
    
    # 4. Ver alimentos
    foods = execute_query("SELECT COUNT(*) FROM food_items")
    if foods is not None:
        tests.append({
            "test": "Conteo de alimentos",
            "status": "✅",
            "result": f"{foods[0][0]} alimentos"
        })
    else:
        tests.append({
            "test": "Conteo de alimentos",
            "status": "⚠️",
            "result": "Tabla food_items no existe o error"
        })
    
    return {
        "database_tests": tests,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/db/foods")
async def get_foods(
    category: Optional[str] = None,
    limit: int = 20
):
    """Obtener alimentos de la base de datos"""
    if not HAS_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible"
        )
    
    try:
        query = "SELECT name, category, calories, protein_g, carbs_g, fat_g FROM food_items"
        params = {}
        
        if category:
            query += " WHERE category = :category"
            params["category"] = category
        
        query += " ORDER BY name LIMIT :limit"
        params["limit"] = limit
        
        foods = execute_query(query, params)
        
        if foods is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al ejecutar consulta"
            )
        
        return {
            "count": len(foods),
            "foods": [
                {
                    "name": f[0],
                    "category": f[1],
                    "calories": float(f[2]) if f[2] is not None else 0,
                    "protein_g": float(f[3]) if f[3] is not None else 0,
                    "carbs_g": float(f[4]) if f[4] is not None else 0,
                    "fat_g": float(f[5]) if f[5] is not None else 0
                }
                for f in foods
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo alimentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos: {str(e)}"
        )

@app.get("/db/users")
async def get_users():
    """Obtener usuarios de la base de datos"""
    if not HAS_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible"
        )
    
    try:
        users = execute_query("""
            SELECT id, email, username, is_active, created_at 
            FROM users 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        if users is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al ejecutar consulta"
            )
        
        return {
            "count": len(users),
            "users": [
                {
                    "id": u[0],
                    "email": u[1],
                    "username": u[2],
                    "is_active": u[3],
                    "created_at": u[4].isoformat() if u[4] else None
                }
                for u in users
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos: {str(e)}"
        )

@app.get("/diets/generate")
async def generate_diet(
    age: int,
    gender: str,
    height: float,
    weight: float,
    activity: str = "moderate",
    goal: str = "weight_loss"
):
    """Generar dieta personalizada usando alimentos de la base de datos"""
    logger.info(f"Generando dieta para: {age}años, {gender}, {height}cm, {weight}kg")
    
    # Validaciones básicas
    if age < 1 or age > 120:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La edad debe estar entre 1 y 120 años"
        )
    
    if height <= 0 or weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La altura y peso deben ser valores positivos"
        )
    
    # Cálculo básico de calorías
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    calories = bmr * activity_multipliers.get(activity.lower(), 1.55)
    
    # Ajuste por objetivo
    if goal == "weight_loss":
        calories -= 500
        protein_ratio = 0.35
        meals_per_day = 5
    elif goal == "muscle_gain":
        calories += 300
        protein_ratio = 0.40
        meals_per_day = 6
    else:  # maintenance
        protein_ratio = 0.30
        meals_per_day = 4
    
    carb_ratio = 0.45
    fat_ratio = 0.25
    
    # Obtener alimentos sugeridos de la base de datos
    suggested_foods = []
    if HAS_DATABASE:
        try:
            # Obtener alimentos por categoría según el objetivo
            if goal == "weight_loss":
                proteins = execute_query(
                    "SELECT name, calories, protein_g FROM food_items WHERE category = 'protein' ORDER BY protein_g DESC LIMIT 5"
                )
                if proteins:
                    suggested_foods.extend(proteins)
            elif goal == "muscle_gain":
                high_calorie = execute_query(
                    "SELECT name, calories, protein_g FROM food_items ORDER BY calories DESC LIMIT 5"
                )
                if high_calorie:
                    suggested_foods.extend(high_calorie)
            else:
                balanced = execute_query(
                    "SELECT name, category, calories FROM food_items ORDER BY RANDOM() LIMIT 8"
                )
                if balanced:
                    suggested_foods.extend(balanced)
        except Exception as e:
            logger.warning(f"No se pudieron obtener alimentos sugeridos: {e}")
    
    # Formatear alimentos sugeridos
    formatted_foods = []
    for f in suggested_foods:
        food_dict = {"name": f[0]}
        if len(f) > 1 and f[1] is not None:
            food_dict["calories"] = float(f[1])
        if len(f) > 2 and f[2] is not None:
            food_dict["protein_g"] = float(f[2])
        if len(f) > 3 and f[3] is not None:
            food_dict["category"] = f[3]
        formatted_foods.append(food_dict)
    
    return {
        "success": True,
        "calculated_values": {
            "bmr": round(bmr),
            "daily_calories": round(calories),
            "macros": {
                "protein_g": round((calories * protein_ratio) / 4),
                "carbs_g": round((calories * carb_ratio) / 4),
                "fat_g": round((calories * fat_ratio) / 9)
            },
            "meals_per_day": meals_per_day
        },
        "user_info": {
            "age": age,
            "gender": gender,
            "height_cm": height,
            "weight_kg": weight,
            "activity_level": activity,
            "goal": goal
        },
        "suggested_foods": formatted_foods,
        "recommendations": [
            f"Consume {round(calories)} calorías diarias",
            f"Objetivo: {goal.replace('_', ' ').title()}",
            f"Nivel de actividad: {activity.title()}",
            f"Distribuye en {meals_per_day} comidas al día",
            "Consulta con un profesional de la salud para un plan personalizado"
        ]
    }

# ================= INICIALIZACIÓN =================
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🚀 DietAI API v2.4 iniciando...")
    
    if HAS_DATABASE:
        logger.info("📊 Probando conexión a base de datos...")
        success, message = test_connection()
        if success:
            logger.info(f"✅ {message}")
        else:
            logger.error(f"❌ Error de conexión a base de datos: {message}")
    else:
        logger.warning("⚠️ Base de datos no configurada")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
