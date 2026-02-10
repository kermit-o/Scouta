# backend/api/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# Routers explícitos que ya existen
from app.api import payments  # /payments
from backend.app.api import auth as auth_api  # /api/auth (si existe)
from backend.app.api import billing as billing_api  # /api/billing (si existe)

from backend.app.api import ui_api
from backend.app.api import ai_analysis

# Auto-montaje
from backend.app.utils.auto_routes import include_routers

# DB bootstrap (dev-only safe)
try:
    from backend.app.config.db import engine
    from backend.app.models import Base
except Exception:
    engine = None
    Base = None

app = FastAPI(
    title="Forge SaaS API",
    version="1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/openapi.json",  # deja /openapi.json como estándard
)

# --- CORS: en prod limita a tus dominios ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restringir en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health (mantén ambos por compatibilidad) ---
@app.get("/health")
def health_root():
    return {"status": "ok"}

@app.get("/api/health")
def health_api():
    return {"status": "ok"}

# --- Middleware simple de correlación/logging ---
@app.middleware("http")
async def add_correlation(request: Request, call_next):
    rid = request.headers.get("x-request-id") or request.headers.get("x-correlation-id")
    response = await call_next(request)
    if rid:
        response.headers["x-request-id"] = rid
    return response

# --- Montaje explícito ya probado en runtime actual ---
app.include_router(payments.router, prefix="/payments", tags=["payments"])
try:
    app.include_router(auth_api.router, prefix="/api", tags=["auth"])
except Exception:
    pass
try:
    app.include_router(billing_api.router, prefix="/api", tags=["billing"])
except Exception:
    pass

# --- Auto-include routers desde app.api.* bajo /api ---
#     y desde app.core.* bajo /api (evitando duplicados /payments ya montado)
try:
    import backend.app.api as api_pkg
    include_routers(app, api_pkg, base_prefix="/api", exclude_modules={"app.api.payments"})
except Exception:
    pass

try:
    import backend.app.core as core_pkg
    include_routers(app, core_pkg, base_prefix="/api")
except Exception:
    pass

# --- Alias: /api/projects/{id}/artifact -> /api/projects/{id}/download (si existe) ---
@app.get("/api/projects/{project_id}/artifact", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def artifact_alias(project_id: str):
    return RedirectResponse(
        url=f"/api/projects/{project_id}/download",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )

# --- Manejador de errores uniforme ---
@app.exception_handler(Exception)
async def unhandled_exc(_, exc: Exception):
    # Nota: en prod, no devuelvas str(exc) completo si puede filtrar internals
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": str(exc)})

# --- (Dev only) crear tablas si no existen ---
if Base and engine:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

# --- Relaciones post-carga (seguras si existen) ---
try:
    from backend.app.core.database.models_patch_safe import apply_relations_safe
    apply_relations_safe()
except Exception:
    pass

app.include_router(payments.router, prefix="/payments")  # ya estaba
app.include_router(ui_api.router, prefix="/api")
app.include_router(ai_analysis.router, prefix="/api")