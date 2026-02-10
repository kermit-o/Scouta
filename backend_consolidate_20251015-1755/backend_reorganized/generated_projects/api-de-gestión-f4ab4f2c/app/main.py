from fastapi import FastAPI

app = FastAPI(title=\"API de Gestión API\")

@app.get(\"/\")
async def root():
    return {\"message\": \"API de Gestión API is running\"}

@app.get(\"/health\")
async def health():
    return {\"status\": \"healthy\"}