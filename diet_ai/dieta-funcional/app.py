from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "¡Funciona!"}

@app.get("/health")
def health():
    return {"status": "perfect"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
