from fastapi import FastAPI

app = FastAPI(title=\"API de Datos IA API\")

@app.get(\"/\")
async def root():
    return {\"message\": \"API de Datos IA API is running\"}

@app.get(\"/health\")
async def health():
    return {\"status\": \"healthy\"}