#!/bin/bash
set +e
set +u

API_DIR="/workspaces/Scouta/blog-ai/blog-saas/api"
FRONT_DIR="/workspaces/Scouta/blog-ai/blog-saas/frontend"

echo "[API] Arrancando..."
pkill -f uvicorn 2>/dev/null || true
sleep 1
nohup bash -c "cd $API_DIR && ./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" > /tmp/api.log 2>&1 &
sleep 6
curl -sS http://localhost:8000/health && echo " <- API OK" || echo "[API] ERROR"

echo "[SCHEDULER] Arrancando..."
pkill -f "spawn_loop" 2>/dev/null || true
sleep 1
nohup bash -c "cd $API_DIR && ./.venv/bin/python -u -m app.jobs.spawn_loop" > /tmp/debate_loop.log 2>&1 &
echo "[SCHEDULER] PID=$!"
sleep 3
tail -n 3 /tmp/debate_loop.log

echo "[NEXT] Arrancando..."
pkill -f "next dev" 2>/dev/null || true
sleep 1
nohup bash -c "cd $FRONT_DIR && npm run dev" > /tmp/next.log 2>&1 &
echo "[NEXT] PID=$!"
sleep 20
tail -n 3 /tmp/next.log
curl -sS -o /dev/null -w "[NEXT] HTTP %{http_code}\n" http://localhost:3000 || true

echo ""
echo "Stack listo"
echo "   API       -> http://localhost:8000/docs"
echo "   Blog      -> http://localhost:3000/posts"
echo "   Scheduler -> tail -f /tmp/debate_loop.log"
echo "   API log   -> tail -f /tmp/api.log"

# Para producción usar:
# cd api && nohup ./.venv/bin/gunicorn app.main:app -c gunicorn.conf.py > /tmp/api.log 2>&1 &

# Hacer puerto 8000 público automáticamente
gh codespace ports visibility 8000:public 2>/dev/null && echo "[PORTS] Puerto 8000 → público" || true
