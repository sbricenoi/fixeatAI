# ETL Service - Dockerfile independiente
FROM python:3.11-slim

# Metadata
LABEL name="ETL Service"
LABEL version="1.0.0"
LABEL description="Microservicio independiente para extracción inteligente BD → KB"

# Variables de construcción
ARG DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r etlservice && useradd -r -g etlservice etlservice

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs configs data && \
    chown -R etlservice:etlservice /app

# Configurar permisos
USER etlservice

# Variables de entorno por defecto
ENV ETL_SERVICE_PORT=9000
ENV ETL_LOG_LEVEL=INFO
ENV ETL_ENV=production
ENV ETL_SERVICE_NAME=etl-service

# Health check independiente
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${ETL_SERVICE_PORT}/health || exit 1

# Exponer puerto
EXPOSE ${ETL_SERVICE_PORT}

# Comando por defecto
CMD ["python", "main.py"]
