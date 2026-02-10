from fastapi import FastAPI

from api.v1 import (
    ai_analysis,
    auth,
    billing,
    lego_backend,
    lego_backend_modules,
    lego_planner,
    lego_status,
    payments,
    projects,
    ui_api,
    lego_projects,
)
from services.lego_runtime_loader import include_generated_routers
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import]

app = FastAPI(
    title="Forge Backend (Lego Demo)",
    version="0.1.0",
)

# --- Montar todos los routers core bajo /api ---
core_routers = [
    ai_analysis.router,
    auth.router,
    billing.router,
    lego_backend.router,
    lego_backend_modules.router,
    lego_planner.router,
    lego_status.router,
    payments.router,
    projects.router,
    ui_api.router,
    lego_projects.router,  # <- aquí va el router de proyectos/descarga
]

for r in core_routers:
    app.include_router(r, prefix="/api")

# --- Montar routers generados dinámicamente (Lego) ---
include_generated_routers(app, base_prefix="/api")

# --- CORS para frontend Next.js (DEV) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # endurecer en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
