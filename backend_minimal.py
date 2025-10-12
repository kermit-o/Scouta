from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Forge SaaS API - Minimal")

# CORS completo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos SIN imports problemáticos
@app.get("/api/v1/payments/plans")
async def get_plans():
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": ["1 proyecto/mes", "Soporte básico"],
                "limits": {"projects": 1, "ai_requests": 10}
            },
            {
                "id": "starter", 
                "name": "Starter",
                "price": 29,
                "features": ["5 proyectos/mes", "Soporte prioritario", "Todos los generadores"],
                "limits": {"projects": 5, "ai_requests": 100}
            },
            {
                "id": "pro",
                "name": "Pro", 
                "price": 79,
                "features": ["Proyectos ilimitados", "Soporte 24/7", "Deployment automático"],
                "limits": {"projects": 999, "ai_requests": 1000}
            }
        ]
    }

@app.get("/api/v1/payments/health")
async def health():
    return {"status": "healthy", "service": "payments"}

@app.post("/api/v1/ai/analyze")
async def analyze_idea(idea: dict):
    return {
        "project_type": "nextjs_app",
        "architecture": "Aplicación web moderna",
        "recommended_stack": ["react", "typescript", "nodejs"],
        "complexity": "Media",
        "estimated_weeks": 2
    }

@app.get("/api/v1/projects")
async def get_projects():
    return []

@app.get("/")
async def root():
    return {"message": "Forge SaaS API - Minimal Backend"}

if __name__ == "__main__":
    print("🚀 BACKEND MINIMAL iniciando en puerto 8001")
    print("✅ Solo API - Sin archivos estáticos")
    print("🔗 URL: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
