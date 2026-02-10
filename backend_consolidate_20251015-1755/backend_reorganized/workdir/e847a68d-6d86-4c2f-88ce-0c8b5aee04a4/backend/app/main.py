from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health

app = FastAPI(title='Forge App', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], allow_credentials=True,
    allow_methods=['*'], allow_headers=['*'],
)
app.include_router(health.router, prefix='/api')

@app.get('/')
async def root():
    return {'status': 'ok', 'service': 'forge', 'version': '0.1.0'}
