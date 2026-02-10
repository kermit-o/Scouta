from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dietai-api",
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    return {
        "message": "DietAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "health": "/health",
            "diets": "/diets",
            "ai": "/ai"
        }
    }
