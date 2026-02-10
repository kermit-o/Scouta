"""
Main API router that includes all version 1 endpoints
"""
from fastapi import APIRouter

from . import auth, diets, health, ai_analysis

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(diets.router, prefix="/diets", tags=["diets"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ai_analysis.router, prefix="/ai", tags=["ai-analysis"])
