from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# Routers reales (ruta de paquete correcta: backend.app.api.*)
from backend.app.api import payments
from backend.app.api import ui_api
from backend.app.api import ai_analysis

# Opcionales (si existen)
try:
    from backend.app.api import auth as auth_api
except Exception:
    auth_api = None
try:
    from backend.app.api import billing as billing_api
except Exception:
    billing_api = None

app = FastAPI(
    title="Forge SaaS API",
    version="1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/openapi.json",
)

# CORS (ajusta en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_root():
    return {"status": "ok"}

@app.get("/api/health")
def health_api():
    return {"status": "ok"}

@app.middleware("http")
async def correlation(request: Request, call_next):
    rid = request.headers.get("x-request-id") or request.headers.get("x-correlation-id")
    resp = await call_next(request)
    if rid:
        resp.headers["x-request-id"] = rid
    return resp

# Montaje explícito bajo prefijos esperados por tu UI
app.include_router(payments.router,     prefix="/payments", tags=["payments"])
app.include_router(ui_api.router,       prefix="/api",      tags=["ui"])
app.include_router(ai_analysis.router,  prefix="/api",      tags=["ai"])

if auth_api:
    app.include_router(auth_api.router, prefix="/api", tags=["auth"])
if billing_api:
    app.include_router(billing_api.router, prefix="/api", tags=["billing"])

# Alias: /artifact -> /download
@app.get("/api/projects/{project_id}/artifact", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def artifact_alias(project_id: str):
    return RedirectResponse(
        url=f"/api/projects/{project_id}/download",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )

@app.exception_handler(Exception)
async def unhandled(_, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": str(exc)})
