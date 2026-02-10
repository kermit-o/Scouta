FROM python:3.11-alpine
WORKDIR /app
COPY app.py .
RUN pip install fastapi uvicorn
CMD ["python", "app.py"]
