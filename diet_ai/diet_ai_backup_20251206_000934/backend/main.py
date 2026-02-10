from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api import auth, diets, recipes, inventory, ai_analysis
from core.database import engine, Base
from core.config import settings

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DietAI API",
    description="API inteligente para gestión de dietas y nutrición",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(diets.router, prefix="/api/v1/diets", tags=["diets"])
app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["recipes"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(ai_analysis.router, prefix="/api/v1/ai", tags=["ai"])

@app.get("/")
async def root():
    return {
        "message": "DietAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "diets": "/api/v1/diets",
            "recipes": "/api/v1/recipes",
            "inventory": "/api/v1/inventory",
            "ai": "/api/v1/ai"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dietai-api"}
