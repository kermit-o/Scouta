from fastapi import FastAPI

app = FastAPI(title="Generated API")

@app.get("/")
async def root():
    return {"message": "API generada automáticamente"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
