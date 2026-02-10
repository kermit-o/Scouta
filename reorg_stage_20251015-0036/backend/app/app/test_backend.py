from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Forge Test API")

# CORS esencial
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "✅ Test Backend FUNCIONANDO", "status": "ok"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "forge-test"}

@app.get("/api/projects")
def list_projects():
    return [{"id": "test-1", "name": "Proyecto Test", "status": "active"}]

@app.post("/api/projects")
def create_project():
    return {"id": "new-project", "status": "created", "message": "✅ Proyecto creado exitosamente"}

if __name__ == "__main__":
    print("🚀 Iniciando Test Backend en puerto 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
