"""
DietAI - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings

# Importar routers existentes
try:
    from api.main import app as existing_app
    # Si el archivo api/main.py ya tiene una app, la usamos
    app = existing_app
except ImportError:
    # Si no existe, creamos una nueva
    app = FastAPI(
        title="DietAI API",
        description="Intelligent Diet and Nutrition Management API",
        version="2.0.0"
    )
    
    @app.get("/")
    async def root():
        return {"message": "DietAI API", "version": "2.0.0"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "dietai-api"}

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
