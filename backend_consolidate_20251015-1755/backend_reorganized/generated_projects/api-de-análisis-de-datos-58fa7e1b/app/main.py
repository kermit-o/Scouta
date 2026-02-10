from fastapi import FastAPI

app = FastAPI(title=\"API de Análisis de Datos API\")

@app.get(\"/\")
async def root():
    return {\"message\": \"API de Análisis de Datos API is running\"}

@app.get(\"/health\")
async def health():
    return {\"status\": \"healthy\"}