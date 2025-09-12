#!/bin/bash

# =================================================================
# Script de Instalación del ETL Service en EC2
# =================================================================

set -e

echo "🚀 Instalando ETL Service en EC2..."

# =================================================================
# 1. ACTUALIZAR SISTEMA
# =================================================================
echo "📦 Actualizando sistema..."
sudo yum update -y

# =================================================================
# 2. INSTALAR DOCKER
# =================================================================
echo "🐳 Instalando Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Instalar Docker Compose
echo "🔧 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# =================================================================
# 3. INSTALAR GIT
# =================================================================
echo "📂 Instalando Git..."
sudo yum install -y git

# =================================================================
# 4. CREAR DIRECTORIO DE TRABAJO
# =================================================================
echo "📁 Creando directorio de trabajo..."
mkdir -p /home/ec2-user/etl-service
cd /home/ec2-user/etl-service

# =================================================================
# 5. CLONAR CÓDIGO (o copiar archivos)
# =================================================================
echo "📥 Configurando código del ETL Service..."
echo "NOTA: Copia manualmente los archivos del ETL Service a este directorio"
echo "Directorio actual: $(pwd)"

# =================================================================
# 6. CONFIGURAR VARIABLES DE ENTORNO
# =================================================================
echo "⚙️ Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    echo "📝 Copiando configuración de producción..."
    cp deploy/production.env .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales"
    echo "   nano .env"
fi

# =================================================================
# 7. CREAR DIRECTORIOS NECESARIOS
# =================================================================
echo "📂 Creando directorios necesarios..."
mkdir -p logs
mkdir -p data
mkdir -p configs
sudo chown -R ec2-user:ec2-user /home/ec2-user/etl-service

# =================================================================
# 8. CONFIGURAR FIREWALL (Security Groups)
# =================================================================
echo "🔒 Configuración de puertos necesarios:"
echo "   - Puerto 9000: ETL Service API"
echo "   - Puerto 9090: Prometheus (opcional)"
echo "   - Puerto 3000: Grafana (opcional)"
echo ""
echo "Configura estos puertos en el Security Group de tu instancia EC2"

# =================================================================
# 9. CONSTRUIR E INICIAR SERVICIOS
# =================================================================
echo "🏗️ Construyendo e iniciando servicios..."

# Verificar que Docker funciona
sudo docker --version
sudo docker-compose --version

echo ""
echo "✅ Instalación base completada!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Editar .env con tus credenciales reales:"
echo "   nano .env"
echo ""
echo "2. Iniciar servicios:"
echo "   sudo docker-compose -f deploy/docker-compose.prod.yml --env-file .env up -d"
echo ""
echo "3. Verificar estado:"
echo "   sudo docker-compose -f deploy/docker-compose.prod.yml ps"
echo ""
echo "4. Ver logs:"
echo "   sudo docker-compose -f deploy/docker-compose.prod.yml logs -f etl-service"
echo ""
echo "5. Verificar health check:"
echo "   curl http://localhost:9000/health"
echo ""
echo "🎉 ¡ETL Service listo para despliegue!"
