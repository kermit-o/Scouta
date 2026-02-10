# API de Gestión API

API REST para sistema de gestión

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t API de Gestión .
docker run -p 8000:8000 API de Gestión
```