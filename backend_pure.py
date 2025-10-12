from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Forge SaaS API - Pure")

# CORS completo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers REALES
from core.app.routers.payments import router as payments_router
from core.app.routers.ai_analysis import router as ai_analysis_router
from core.app.routers.projects import router as projects_router

app.include_router(payments_router, prefix="/api/v1")
app.include_router(ai_analysis_router, prefix="/api/v1/ai")
app.include_router(projects_router, prefix="/api/v1/projects")

@app.get("/")
async def root():
    return {"message": "Forge SaaS API - Pure Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api"}

if __name__ == "__main__":
    print("🚀 BACKEND PURE API iniciando en puerto 8001")
    print("📡 Solo endpoints API - Sin archivos estáticos")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
