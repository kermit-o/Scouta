from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"healthy": True}

@app.post("/auth/test")
def test_auth():
    return {"message": "Auth endpoint works"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
