
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Demo Forge",
    description="Prueba de generación",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Demo Forge",
        "description": "Prueba de generación",
        "status": "active",
        "generated_by": "LLM Driven System v5.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "LLM Driven API"}

@app.get("/api/info")
async def project_info():
    return {"name": "Demo Forge", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
