from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forge SaaS API", version="1.0.0")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Forge SaaS API"}

@app.get("/")
async def root():
    return {"message": "Forge SaaS API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
