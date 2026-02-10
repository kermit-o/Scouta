from __future__ import annotations

from fastapi import FastAPI

from .routers import health, products, orders


def create_app() -> FastAPI:
    app = FastAPI(title="Forge E-commerce API")

    app.include_router(health.router)
    app.include_router(products.router)
    app.include_router(orders.router)

    return app


app = create_app()
