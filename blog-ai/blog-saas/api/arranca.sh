pkill -f uvicorn || true
./.venv/bin/uvicorn app.main:app --env-file .env --host 0.0.0.0 --port 8000 &
sleep 1
curl http://localhost:8000/health
