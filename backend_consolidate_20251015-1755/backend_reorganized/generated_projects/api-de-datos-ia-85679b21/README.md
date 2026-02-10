# API de Datos IA API

API para análisis de datos con machine learning integrado

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t API de Datos IA .
docker run -p 8000:8000 API de Datos IA
```