from fastapi import FastAPI
from .routers.health import router as health_router
from .routers.users import router as users_router

app = FastAPI(title="Forge App")
app.include_router(health_router)
app.include_router(users_router)
