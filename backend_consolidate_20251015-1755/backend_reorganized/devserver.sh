#!/usr/bin/env bash
set -e
pkill -f "uvicorn llm_driven_service:app" || true
PYTHONPATH="$(pwd)" python -m uvicorn llm_driven_service:app \
  --host 0.0.0.0 --port 8010 \
  --reload \
  --reload-exclude 'workdir/*' \
  --reload-exclude 'artifacts/*'
