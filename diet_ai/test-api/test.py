from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test directo"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Iniciando en http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
