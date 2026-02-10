# API de Análisis de Datos API

API REST para análisis de datos con machine learning

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t API de Análisis de Datos .
docker run -p 8000:8000 API de Análisis de Datos
```