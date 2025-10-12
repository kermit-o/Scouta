"""
Main simplificado para probar solo el sistema de pagos
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Crear app
app = FastAPI(title="Forge SaaS - Payments Test", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir solo los routers esenciales
from core.app.routers import auth, payments

app.include_router(auth.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Forge SaaS Payments API", "status": "running"}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "forge-saas-payments"}

if __name__ == "__main__":
    uvicorn.run("main_payments_test:app", host="0.0.0.0", port=8000, reload=True)
