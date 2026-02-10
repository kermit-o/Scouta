# Demo Forge

Prueba de generación

Generado con analisis de IA

## Instalacion y Ejecucion

```bash
python -m venv .venv
source .venv/bin/activate    # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Ejecutar con Uvicorn (opcional)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `GET /` — Información básica del proyecto
- `GET /api/health` — Comprobación de salud
- `GET /api/info` — Nombre y versión

## Estructura generada

- `main.py` — Servicio FastAPI mínimo
- `requirements.txt` — Dependencias
- `README.md` — Esta guía

---
Generado por **LLM Driven System v5.0**
