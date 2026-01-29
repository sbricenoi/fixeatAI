# Animal-AI Service - Dockerfile independiente
FROM python:3.11-slim

# Metadatos
LABEL maintainer="FixeatAI Team"
LABEL service="animal-ai-service"
LABEL version="1.0.0"
LABEL description="Microservicio independiente para análisis de comportamiento animal"

# Variables de entorno por defecto
ENV ANIMAL_SERVICE_PORT=8080
ENV ANIMAL_LOG_LEVEL=INFO
ENV ANIMAL_DEBUG_MODE=false
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 animalai && \
    mkdir -p /app /app/logs /app/models /app/videos /app/data && \
    chown -R animalai:animalai /app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs models videos data configs && \
    chown -R animalai:animalai /app

# Cambiar a usuario no-root
USER animalai

# Exponer puertos
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando por defecto
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


