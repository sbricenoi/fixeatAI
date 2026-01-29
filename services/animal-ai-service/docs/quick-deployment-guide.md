# 🚀 Guía de Despliegue Rápido - Sistema Multi-Cámara

## 🎯 **3 Formas de Instalar Cámaras en Minutos**

---

## 🔥 **Opción 1: Instalación Express (< 3 minutos)**

### **Una Sola Línea de Comando**
```bash
# Instalación automática con parámetros
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --camera-id="barn_001" \
  --name="Cámara Establo A" \
  --location="Establo A - Zona Norte" \
  --stream="rtsp://192.168.1.100/stream" \
  --server="http://192.168.1.10:8090" \
  --animal-type="bovine"
```

### **¿Qué hace este comando?**
1. ✅ **Detecta** el sistema operativo
2. ✅ **Instala** Docker automáticamente
3. ✅ **Configura** la cámara con los parámetros
4. ✅ **Descarga** y ejecuta el servicio Animal-AI
5. ✅ **Registra** la cámara en el servidor central
6. ✅ **Inicia** el análisis automáticamente

---

## 📱 **Opción 2: Instalación con QR Code (< 5 minutos)**

### **Paso 1: Generar QR Code**
```bash
# En el servidor central, generar QR para nueva cámara
curl -X POST "http://your-server:8090/api/v1/qr/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "barn_002",
    "location": "Establo B",
    "preset": "livestock_monitoring",
    "discovery_url": "http://192.168.1.10:8090"
  }' \
  --output camera_barn_002.png
```

### **Paso 2: Escanear con App Móvil**
1. 📱 Descargar **FixeatAI Camera App**
2. 📷 Escanear el QR code generado
3. 📶 La app configura WiFi y cámara automáticamente
4. ✅ Confirmación: "Cámara lista!"

### **Paso 3: Verificar**
```bash
# Verificar que la cámara está registrada
curl "http://192.168.1.10:8090/api/v1/cameras"
```

---

## 🖥️ **Opción 3: Instalación Interactiva (< 10 minutos)**

### **Paso 1: Descargar Script**
```bash
# Descargar script de instalación
curl -O https://install.fixeatai.com/install-camera.sh
chmod +x install-camera.sh
```

### **Paso 2: Ejecutar Instalación Interactiva**
```bash
# Ejecutar sin parámetros para modo interactivo
./install-camera.sh
```

### **Paso 3: Seguir el Asistente**
```
🎥 FixeatAI Camera Installation Script v1.0.0
🤖 Animal Behavior Analysis System

[INFO] Detectando sistema operativo...
[SUCCESS] Sistema detectado: ubuntu

🔧 Configuración interactiva de la cámara
======================================

🆔 ID de la cámara (ej: barn_001): barn_003
📝 Nombre descriptivo: Cámara Pastura C
📍 Ubicación (ej: Establo A): Pastura C - Zona Sur
🎥 URL del stream (ej: rtsp://192.168.1.100/stream): rtsp://192.168.1.103/stream
🌐 Servidor central [http://192.168.1.10:8090]: 

🐾 Tipo de animales:
1) Ganado bovino
2) Ganado porcino
3) Ganado ovino
4) Aves de corral
5) Otros
Seleccione (1-5): 1

🔌 Puerto local [8080]: 8083

[SUCCESS] Configuración completada
[INFO] Creando archivo de configuración...
[SUCCESS] Archivo de configuración creado
[INFO] Descargando imágenes Docker...
[SUCCESS] Imágenes Docker descargadas
[INFO] Iniciando servicios...
[SUCCESS] Servicios iniciados correctamente
[INFO] Registrando cámara en el servidor central...
[SUCCESS] Cámara registrada exitosamente

🎉 ¡FixeatAI Camera instalado y funcionando!
```

---

## 🏗️ **Configuración del Servidor Central**

### **Paso 1: Desplegar Discovery Service**
```bash
# Clonar repositorio
git clone https://github.com/fixeatai/animal-ai-service.git
cd animal-ai-service

# Configurar variables de entorno
cp env.example .env
nano .env  # Editar configuración

# Desplegar servidor central
docker-compose -f docker-compose.camera-discovery.yml up -d
```

### **Paso 2: Verificar Servicios**
```bash
# Verificar que todos los servicios estén corriendo
docker-compose -f docker-compose.camera-discovery.yml ps

# Acceder al dashboard
open http://localhost:8090
```

### **Paso 3: Configurar Red**
```bash
# Crear red compartida para todas las cámaras
docker network create animal-ai-network
```

---

## 📊 **Dashboard Multi-Cámara**

### **Acceso al Dashboard Central**
```
🌐 URLs de Acceso:
==================
📊 Dashboard Principal: http://your-server:8090
🎥 Gestión de Cámaras: http://your-server:8090/cameras
📈 Métricas: http://your-server:9091
📊 Grafana: http://your-server:3001
🔧 Admin Panel: http://your-server:8090/admin
```

### **Funcionalidades del Dashboard**
- ✅ **Vista en tiempo real** de todas las cámaras
- ✅ **Estadísticas** de animales y movimientos
- ✅ **Alertas** automáticas
- ✅ **Configuración remota** de cámaras
- ✅ **Generación de QR** para nuevas instalaciones
- ✅ **Monitoreo de salud** de todas las instancias

---

## 🔧 **Configuraciones Rápidas por Tipo**

### **Granja de Ganado Bovino**
```bash
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --camera-id="cow_barn_01" \
  --name="Establo Principal" \
  --location="Establo 1" \
  --stream="rtsp://192.168.1.100/stream" \
  --server="http://192.168.1.10:8090" \
  --animal-type="bovine"
```

### **Granja Porcina**
```bash
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --camera-id="pig_pen_01" \
  --name="Corral de Cerdos A" \
  --location="Corral A" \
  --stream="rtsp://192.168.1.101/stream" \
  --server="http://192.168.1.10:8090" \
  --animal-type="porcine"
```

### **Gallinero**
```bash
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --camera-id="chicken_coop_01" \
  --name="Gallinero Principal" \
  --location="Gallinero 1" \
  --stream="rtsp://192.168.1.102/stream" \
  --server="http://192.168.1.10:8090" \
  --animal-type="poultry"
```

---

## 🔍 **Verificación y Troubleshooting**

### **Verificar Estado de Cámara**
```bash
# Health check de cámara individual
curl http://camera-ip:8080/health

# Ver logs de la cámara
docker logs fixeatai-camera-CAMERA_ID

# Verificar conexión con servidor central
curl http://your-server:8090/api/v1/cameras/CAMERA_ID
```

### **Comandos de Mantenimiento**
```bash
# Reiniciar cámara
cd /opt/fixeatai-camera && docker-compose restart

# Actualizar a última versión
cd /opt/fixeatai-camera && docker-compose pull && docker-compose up -d

# Ver estadísticas en tiempo real
curl http://camera-ip:8080/api/v1/admin/dashboard

# Desinstalar cámara
cd /opt/fixeatai-camera && docker-compose down && sudo rm -rf /opt/fixeatai-camera
```

### **Solución de Problemas Comunes**

#### **Problema: Cámara no se conecta al stream**
```bash
# Verificar conectividad
ping camera-ip
telnet camera-ip 554  # Para RTSP

# Probar stream manualmente
ffplay rtsp://camera-ip/stream
```

#### **Problema: No se registra en servidor central**
```bash
# Verificar conectividad con servidor
curl http://server-ip:8090/health

# Verificar configuración
cat /opt/fixeatai-camera/camera-config.json

# Registrar manualmente
curl -X POST "http://server-ip:8090/api/v1/cameras/register" \
  -H "Content-Type: application/json" \
  -d @/opt/fixeatai-camera/camera-config.json
```

#### **Problema: Alto uso de CPU/Memoria**
```bash
# Verificar recursos
docker stats fixeatai-camera-CAMERA_ID

# Ajustar configuración de análisis
curl -X PUT "http://camera-ip:8080/api/v1/config" \
  -H "Content-Type: application/json" \
  -d '{
    "config_section": "analysis",
    "config_data": {
      "movement_sensitivity": "low",
      "analysis_interval_seconds": 2
    }
  }'
```

---

## 📱 **App Móvil para Gestión**

### **Funcionalidades de la App**
- 📷 **Escaneo de QR** para instalación automática
- 📊 **Monitoreo** de cámaras en tiempo real
- 🔧 **Configuración remota** de parámetros
- 🚨 **Alertas push** para eventos importantes
- 📈 **Estadísticas** y reportes
- 🎥 **Vista en vivo** de todas las cámaras

### **Descarga**
```
📱 iOS: App Store - "FixeatAI Camera Manager"
🤖 Android: Google Play - "FixeatAI Camera Manager"
🌐 Web App: https://app.fixeatai.com
```

---

## 🎯 **Casos de Uso Rápidos**

### **Instalación Masiva (10+ Cámaras)**
```bash
#!/bin/bash
# install-multiple-cameras.sh

CAMERAS=(
  "barn_01,Establo 1,192.168.1.100"
  "barn_02,Establo 2,192.168.1.101"
  "pasture_01,Pastura A,192.168.1.102"
  "feeding_01,Área Alimentación,192.168.1.103"
)

for camera in "${CAMERAS[@]}"; do
  IFS=',' read -r id name ip <<< "$camera"
  
  echo "Instalando cámara: $name"
  curl -sSL https://install.fixeatai.com/camera | bash -s -- \
    --camera-id="$id" \
    --name="$name" \
    --location="$name" \
    --stream="rtsp://$ip/stream" \
    --server="http://192.168.1.10:8090" \
    --animal-type="bovine"
    
  sleep 30  # Esperar entre instalaciones
done

echo "✅ Todas las cámaras instaladas!"
```

### **Monitoreo Distribuido**
```bash
# Instalar en diferentes ubicaciones geográficas
# Granja Norte
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --server="http://central-server.farm.com:8090"

# Granja Sur  
curl -sSL https://install.fixeatai.com/camera | bash -s -- \
  --server="http://central-server.farm.com:8090"

# Todas reportan al mismo servidor central
```

---

## ✅ **Checklist de Instalación**

### **Antes de Instalar**
- [ ] Verificar conectividad de red
- [ ] Confirmar URL del stream de cámara
- [ ] Tener IP del servidor central
- [ ] Verificar puertos disponibles (8080-8099)
- [ ] Confirmar permisos de administrador

### **Durante la Instalación**
- [ ] Ejecutar script de instalación
- [ ] Verificar descarga de imágenes Docker
- [ ] Confirmar registro en servidor central
- [ ] Probar acceso al dashboard local

### **Después de Instalar**
- [ ] Verificar análisis en tiempo real
- [ ] Confirmar detección de animales
- [ ] Probar alertas y notificaciones
- [ ] Configurar backup y monitoreo
- [ ] Documentar configuración

---

**¡Con estas opciones puedes tener un sistema completo de monitoreo animal funcionando en menos de 10 minutos!** 🎥🐾🚀


