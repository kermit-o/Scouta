# forge_saas/backend/Dockerfile
FROM python:3.11-slim AS base
WORKDIR /app

# Paso 3/5: Instalación de dependencias del sistema (Actualizado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # Dependencias de imágenes (Pillow, etc.)
    libzbar0 \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    # NUEVO: Dependencias científicas/numéricas (Numpy, Pandas)
    gfortran \
    libblas-dev \
    liblapack-dev \
    # Herramienta de control de versiones
    git \
    # Limpieza
    && rm -rf /var/lib/apt/lists/*

# Paso 4/5: Copia los requisitos
COPY requirements.txt .

# Paso 5/5: Instalación de paquetes Python
RUN pip install --no-cache-dir -r requirements.txt

# ... el resto de tu Dockerfile