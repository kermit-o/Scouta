from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=\"Sistema de Tareas IA API\")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

@app.get(\"/\")
async def root():
    return {\"message\": \"Sistema de Tareas IA API is running\"}

@app.get(\"/health\")
async def health():
    return {\"status\": \"healthy\"}