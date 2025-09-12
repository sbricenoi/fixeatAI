# 🚀 Guía de Despliegue - ETL Service en AWS EC2

## 📋 **Requisitos Previos**

### **🖥️ Instancia EC2:**
- **Tipo recomendado**: t3.medium (2 vCPU, 4 GB RAM) o superior
- **OS**: Amazon Linux 2 o Ubuntu 20.04+
- **Storage**: 20 GB EBS (SSD) mínimo
- **Security Group**: Puertos 22 (SSH), 9000 (ETL Service), 9090 (Prometheus), 3000 (Grafana)

### **🔐 Credenciales Necesarias:**
- ✅ Credenciales MySQL RDS (host, user, password, database)
- ✅ OpenAI API Key (o LLM local configurado)
- ✅ SSH Key para acceder a EC2

## 🛠️ **Método 1: Despliegue Automático**

### **Paso 1: Conectar a EC2**
```bash
ssh -i tu-key.pem ec2-user@tu-ec2-ip
```

### **Paso 2: Copiar Archivos**
```bash
# Subir código del ETL Service a la instancia
scp -i tu-key.pem -r services/etl-service/ ec2-user@tu-ec2-ip:/home/ec2-user/
```

### **Paso 3: Ejecutar Script de Instalación**
```bash
cd /home/ec2-user/etl-service
bash deploy/install-etl-service.sh
```

### **Paso 4: Configurar Variables de Entorno**
```bash
nano .env
```

Editar con tus credenciales reales:
```bash
# Base de datos
ETL_DB_HOST=tu-rds-endpoint.amazonaws.com
ETL_DB_USER=tu-usuario
ETL_DB_PASSWORD=tu-password
ETL_DB_DATABASE=tu-database

# LLM
ETL_LLM_API_KEY=tu-openai-api-key
```

### **Paso 5: Iniciar Servicios**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml --env-file .env up -d
```

## 🛠️ **Método 2: Despliegue Manual**

### **1. Instalar Docker**
```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **2. Clonar/Copiar Código**
```bash
mkdir -p /home/ec2-user/etl-service
cd /home/ec2-user/etl-service
# Copiar todos los archivos del ETL Service aquí
```

### **3. Configurar Environment**
```bash
cp deploy/production.env .env
nano .env
# Editar con credenciales reales
```

### **4. Iniciar Servicios**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml --env-file .env up -d
```

## 🔧 **Configuración del Security Group**

En la consola de AWS EC2:

| Puerto | Protocolo | Origen | Descripción |
|--------|-----------|---------|-------------|
| 22 | TCP | Tu IP | SSH |
| 9000 | TCP | 0.0.0.0/0 | ETL Service API |
| 9090 | TCP | Tu IP | Prometheus (opcional) |
| 3000 | TCP | Tu IP | Grafana (opcional) |

## 📊 **Verificación del Despliegue**

### **1. Verificar Contenedores**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml ps
```

### **2. Health Check**
```bash
curl http://localhost:9000/health
```

### **3. Ver Logs**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml logs -f etl-service
```

### **4. Test de Conexión BD**
```bash
curl "http://localhost:9000/api/v1/info"
```

### **5. Test de Documentación**
```bash
curl "http://localhost:9000/api/v1/validate-documentation/requisicion_db"
```

## 🔄 **Comandos de Gestión**

### **Iniciar Servicios**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml --env-file .env up -d
```

### **Detener Servicios**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml down
```

### **Reiniciar Servicios**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml restart
```

### **Ver Logs en Tiempo Real**
```bash
sudo docker-compose -f deploy/docker-compose.prod.yml logs -f etl-service
```

### **Actualizar Código**
```bash
# Copiar nuevos archivos
sudo docker-compose -f deploy/docker-compose.prod.yml down
sudo docker-compose -f deploy/docker-compose.prod.yml build --no-cache
sudo docker-compose -f deploy/docker-compose.prod.yml --env-file .env up -d
```

## 📈 **Monitoreo**

### **ETL Service API**
- **Health Check**: `http://tu-ec2-ip:9000/health`
- **Info**: `http://tu-ec2-ip:9000/api/v1/info`
- **Métricas**: `http://tu-ec2-ip:9000/metrics`

### **Prometheus (opcional)**
- **URL**: `http://tu-ec2-ip:9090`
- **Targets**: ETL Service metrics

### **Grafana (opcional)**
- **URL**: `http://tu-ec2-ip:3000`
- **Login**: admin / (password del .env)

## 🔒 **Persistencia de Datos**

Los siguientes datos se persisten automáticamente:

- **Logs**: `/var/lib/docker/volumes/etl_logs`
- **Configuraciones ETL**: `/var/lib/docker/volumes/etl_configs`
- **Datos KB local**: `/var/lib/docker/volumes/etl_data`

### **Backup Manual**
```bash
# Backup de configuraciones
sudo docker run --rm -v etl_configs:/backup -v $(pwd):/host alpine tar czf /host/etl-configs-backup.tar.gz -C /backup .

# Backup de logs
sudo docker run --rm -v etl_logs:/backup -v $(pwd):/host alpine tar czf /host/etl-logs-backup.tar.gz -C /backup .
```

## 🐛 **Troubleshooting**

### **Error de Conexión BD**
```bash
# Verificar conectividad
telnet tu-rds-endpoint 3306

# Verificar variables de entorno
sudo docker-compose -f deploy/docker-compose.prod.yml exec etl-service env | grep ETL_DB
```

### **Error de LLM**
```bash
# Verificar API key
sudo docker-compose -f deploy/docker-compose.prod.yml exec etl-service env | grep ETL_LLM

# Test manual
curl -X POST "http://localhost:9000/api/v1/discover-schema" -H "Content-Type: application/json" -d '{"databases": ["default"]}'
```

### **Contenedor No Inicia**
```bash
# Ver logs detallados
sudo docker-compose -f deploy/docker-compose.prod.yml logs etl-service

# Verificar recursos
df -h
free -h
```

## 🎯 **URLs de Acceso**

Una vez desplegado:

- **ETL Service API**: `http://tu-ec2-ip:9000`
- **Health Check**: `http://tu-ec2-ip:9000/health`
- **Documentation**: `http://tu-ec2-ip:9000/docs`
- **Prometheus**: `http://tu-ec2-ip:9090` (opcional)
- **Grafana**: `http://tu-ec2-ip:3000` (opcional)

## ✅ **Checklist de Despliegue**

- [ ] Instancia EC2 creada y configurada
- [ ] Security Group con puertos correctos
- [ ] Docker y Docker Compose instalados
- [ ] Código del ETL Service copiado
- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Servicios iniciados con docker-compose
- [ ] Health check respondiendo correctamente
- [ ] Conexión a BD verificada
- [ ] Documentación cargada exitosamente
- [ ] Análisis IA funcionando

🎉 **¡ETL Service desplegado y listo para usar!**
