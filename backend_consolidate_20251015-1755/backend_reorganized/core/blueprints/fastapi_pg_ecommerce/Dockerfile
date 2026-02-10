FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# 1) Dependencias
COPY backend/app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt alembic psycopg2-binary

# 2) Código de la app y migraciones
COPY backend /app/backend
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

EXPOSE 8081

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8081"]
