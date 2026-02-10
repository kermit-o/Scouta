from fastapi import FastAPI
from app.config.db import engine
from app.models import Base

app = FastAPI(title="Forge SaaS (staging)")

# Dev only (stage): crear tablas si no existen
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

@app.get("/health")
def health():
    return {"status": "ok"}
