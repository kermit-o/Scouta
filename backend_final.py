from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socket

def find_available_port(start_port=8010, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
            return port
        except OSError:
            continue
    return 8010

app = FastAPI(title="Forge SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.api_route("/api/v1/ai/analyze", methods=["GET", "POST"])
async def analyze_idea(request: dict = None):
    # Manejar tanto GET como POST
    if request is None:
        return {
            "project_type": "nextjs_app", 
            "architecture": "Aplicación web moderna",
            "recommended_stack": ["react", "typescript", "nodejs"],
            "complexity": "Media", 
            "estimated_weeks": 2,
            "message": "Por favor usa POST con {'idea': 'tu idea'} para análisis completo"
        }
    
    return {
        "project_type": "nextjs_app",
        "architecture": "Aplicación web moderna", 
        "recommended_stack": ["react", "typescript", "nodejs"],
        "complexity": "Medium",
        "estimated_weeks": 2,
        "analyzed_idea": request.get("idea", "Sin idea proporcionada")
    }
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

if __name__ == "__main__":
    port = find_available_port(8010)
    print(f"🚀 BACKEND FINAL iniciando en puerto {port}")
    print("✅ Solo API - Sin archivos estáticos")
    print(f"🔗 URL: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
