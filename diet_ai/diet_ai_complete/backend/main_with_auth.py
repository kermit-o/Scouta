"""
DietAI API v3.0 - Con autenticación JWT completa
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar módulos de seguridad
try:
    from security.config import security_config
    security_config.verify_secret_key()
    HAS_SECURITY = True
    logger.info("✅ Módulo de seguridad cargado")
except ImportError as e:
    logger.warning(f"❌ No se pudo cargar módulo de seguridad: {e}")
    HAS_SECURITY = False

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
    title="DietAI API v3.0",
    version="3.0.0",
    description="API inteligente para gestión de dietas con autenticación JWT",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operaciones de autenticación y gestión de usuarios"
        },
        {
            "name": "diets",
            "description": "Generación y gestión de planes de dieta"
        },
        {
            "name": "foods",
            "description": "Gestión de alimentos y nutrición"
        },
        {
            "name": "health",
            "description": "Health checks y monitoreo"
        }
    ]
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= IMPORTAR ROUTERS =================

# Health router (siempre disponible)
try:
    from api.routers.health import router as health_router
    app.include_router(health_router)
    logger.info("✅ Router de health cargado")
except ImportError as e:
    logger.warning(f"❌ No se pudo cargar router de health: {e}")

# Auth router (si hay seguridad)
if HAS_SECURITY:
    try:
        from api.routers.auth_router import router as auth_router
        app.include_router(auth_router)
        logger.info("✅ Router de autenticación cargado")
    except ImportError as e:
        logger.warning(f"❌ No se pudo cargar router de autenticación: {e}")

# Diets router
try:
    from api.routers.diets import router as diets_router
    app.include_router(diets_router)
    logger.info("✅ Router de dietas cargado")
except ImportError as e:
    logger.warning(f"❌ No se pudo cargar router de dietas: {e}")

# Foods router (si hay base de datos)
if HAS_DATABASE:
    try:
        # Crear router de alimentos dinámicamente
        from fastapi import APIRouter, HTTPException, Depends
        from security.dependencies import optional_auth
        from typing import Optional
        
        foods_router = APIRouter(prefix="/foods", tags=["foods"])
        
        @foods_router.get("/")
        async def get_foods(
            category: Optional[str] = None,
            limit: int = 20,
            current_user = Depends(optional_auth)
        ):
            """Obtener alimentos de la base de datos"""
            if not HAS_DATABASE:
                raise HTTPException(status_code=503, detail="Base de datos no disponible")
            
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
                    raise HTTPException(status_code=500, detail="Error al ejecutar consulta")
                
                # Información de autenticación (si aplica)
                auth_info = {}
                if current_user:
                    auth_info["authenticated"] = True
                    auth_info["user_id"] = current_user["id"]
                else:
                    auth_info["authenticated"] = False
                
                return {
                    "count": len(foods),
                    "auth": auth_info,
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
                
            except Exception as e:
                logger.error(f"Error obteniendo alimentos: {e}")
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
        
        app.include_router(foods_router)
        logger.info("✅ Router de alimentos cargado")
    except ImportError as e:
        logger.warning(f"❌ No se pudo cargar router de alimentos: {e}")

# ================= ENDPOINTS RAÍZ Y HEALTH =================

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
    
    security_status = "✅ Configurada" if HAS_SECURITY else "❌ No disponible"
    
    endpoints = {
        "docs": "/docs",
        "health": "/health",
        "authentication": "/auth" if HAS_SECURITY else "No disponible",
        "diets": "/diets",
        "foods": "/foods" if HAS_DATABASE else "No disponible"
    }
    
    return {
        "message": "DietAI API v3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "online",
        "version": "3.0.0",
        "database": db_status,
        "security": security_status,
        "endpoints": endpoints
    }

@app.get("/health")
async def health():
    """Health check"""
    checks = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0"
    }
    
    if HAS_DATABASE:
        success, message = test_connection()
        checks["database"] = "healthy" if success else "unhealthy"
        checks["database_message"] = message
    else:
        checks["database"] = "not_configured"
    
    if HAS_SECURITY:
        checks["security"] = "configured"
    else:
        checks["security"] = "not_configured"
    
    return checks

# ================= INICIALIZACIÓN =================
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🚀 DietAI API v3.0 iniciando...")
    
    if HAS_DATABASE:
        logger.info("📊 Probando conexión a base de datos...")
        success, message = test_connection()
        if success:
            logger.info(f"✅ {message}")
        else:
            logger.error(f"❌ Error de conexión a base de datos: {message}")
    
    if HAS_SECURITY:
        logger.info("🔐 Sistema de seguridad JWT configurado")
    else:
        logger.warning("⚠️ Sistema de seguridad no configurado")
    
    logger.info("✅ API lista para recibir solicitudes")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de apagado de la aplicación"""
    logger.info("🛑 DietAI API deteniéndose...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
