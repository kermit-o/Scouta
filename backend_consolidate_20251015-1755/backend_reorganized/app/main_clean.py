"""
Forge SaaS - Main Application Entry Point
Reorganized structure for better maintainability
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from api.v1.auth import router as auth_router
from api.v1.projects import router as projects_router  
from api.v1.payments import router as payments_router
from api.v1.ai_analysis import router as ai_router
from core.database.database import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Forge SaaS API...")
    init_database()
    yield
    # Shutdown
    print("👋 Shutting down Forge SaaS API...")

# Initialize FastAPI app with modern lifespan
app = FastAPI(
    title="Forge SaaS API",
    version="1.0.0",
    description="AI-Powered Project Generation Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])

# Health check endpoints
@app.get("/")
async def root():
    return {"message": "Forge SaaS API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "forge_saas"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "forge_saas"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main_clean:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )
