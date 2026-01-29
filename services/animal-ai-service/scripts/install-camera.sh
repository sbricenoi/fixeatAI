#!/bin/bash
# FixeatAI Camera - Script de Instalación Rápida
# Versión: 1.0.0
# Uso: curl -sSL https://install.fixeatai.com/camera | bash

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_VERSION="1.0.0"
INSTALL_DIR="/opt/fixeatai-camera"
CONFIG_FILE="$INSTALL_DIR/camera-config.json"
DOCKER_COMPOSE_FILE="$INSTALL_DIR/docker-compose.yml"
LOG_FILE="/var/log/fixeatai-camera-install.log"

# Configuración por defecto
DEFAULT_DISCOVERY_URL="http://192.168.1.10:8090"
DEFAULT_CAMERA_PORT="8080"

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

show_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
    ███████╗██╗██╗  ██╗███████╗ █████╗ ████████╗ █████╗ ██╗
    ██╔════╝██║╚██╗██╔╝██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██║
    █████╗  ██║ ╚███╔╝ █████╗  ███████║   ██║   ███████║██║
    ██╔══╝  ██║ ██╔██╗ ██╔══╝  ██╔══██║   ██║   ██╔══██║██║
    ██║     ██║██╔╝ ██╗███████╗██║  ██║   ██║   ██║  ██║██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝
    
    🎥 Camera Installation Script v${SCRIPT_VERSION}
    🤖 Animal Behavior Analysis System
EOF
    echo -e "${NC}"
}

detect_system() {
    echo_info "Detectando sistema operativo..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt-get"
        elif command -v yum &> /dev/null; then
            OS="centos"
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            OS="arch"
            PACKAGE_MANAGER="pacman"
        else
            echo_error "Distribución Linux no soportada"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        echo_error "Sistema operativo no soportado: $OSTYPE"
        exit 1
    fi
    
    echo_success "Sistema detectado: $OS"
}

check_requirements() {
    echo_info "Verificando requisitos del sistema..."
    
    # Verificar si es root o tiene sudo
    if [[ $EUID -ne 0 ]] && ! command -v sudo &> /dev/null; then
        echo_error "Se requieren permisos de administrador o sudo"
        exit 1
    fi
    
    # Verificar conectividad a internet
    if ! ping -c 1 google.com &> /dev/null; then
        echo_error "No hay conexión a internet"
        exit 1
    fi
    
    # Verificar espacio en disco (mínimo 2GB)
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 2097152 ]]; then
        echo_warning "Espacio en disco bajo. Se recomiendan al menos 2GB libres"
    fi
    
    echo_success "Requisitos verificados"
}

install_docker() {
    echo_info "Verificando instalación de Docker..."
    
    if command -v docker &> /dev/null; then
        echo_success "Docker ya está instalado"
        return 0
    fi
    
    echo_info "Instalando Docker..."
    
    case $OS in
        "ubuntu")
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            ;;
        "centos")
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            ;;
        "macos")
            echo_info "Por favor instala Docker Desktop desde https://docker.com/products/docker-desktop"
            echo_info "Presiona Enter cuando Docker esté instalado..."
            read
            ;;
    esac
    
    # Verificar instalación
    if command -v docker &> /dev/null; then
        echo_success "Docker instalado correctamente"
    else
        echo_error "Error instalando Docker"
        exit 1
    fi
}

install_docker_compose() {
    echo_info "Verificando Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        echo_success "Docker Compose ya está instalado"
        return 0
    fi
    
    echo_info "Instalando Docker Compose..."
    
    # Obtener última versión
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    if command -v docker-compose &> /dev/null; then
        echo_success "Docker Compose instalado correctamente"
    else
        echo_error "Error instalando Docker Compose"
        exit 1
    fi
}

setup_directories() {
    echo_info "Creando directorios de instalación..."
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo mkdir -p "$INSTALL_DIR/data"
    sudo mkdir -p "$INSTALL_DIR/logs"
    sudo mkdir -p "$INSTALL_DIR/configs"
    
    # Cambiar permisos
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    
    echo_success "Directorios creados en $INSTALL_DIR"
}

interactive_config() {
    echo_info "Configuración interactiva de la cámara"
    echo "======================================"
    
    # ID de la cámara
    while [[ -z "$CAMERA_ID" ]]; do
        read -p "🆔 ID de la cámara (ej: barn_001): " CAMERA_ID
        if [[ ! "$CAMERA_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
            echo_error "ID inválido. Use solo letras, números, guiones y guiones bajos"
            CAMERA_ID=""
        fi
    done
    
    # Nombre descriptivo
    while [[ -z "$CAMERA_NAME" ]]; do
        read -p "📝 Nombre descriptivo: " CAMERA_NAME
    done
    
    # Ubicación
    while [[ -z "$CAMERA_LOCATION" ]]; do
        read -p "📍 Ubicación (ej: Establo A): " CAMERA_LOCATION
    done
    
    # URL del stream
    while [[ -z "$CAMERA_STREAM_URL" ]]; do
        read -p "🎥 URL del stream (ej: rtsp://192.168.1.100/stream): " CAMERA_STREAM_URL
        if [[ ! "$CAMERA_STREAM_URL" =~ ^(rtsp|http|https):// ]]; then
            echo_error "URL inválida. Debe comenzar con rtsp://, http:// o https://"
            CAMERA_STREAM_URL=""
        fi
    done
    
    # Servidor de descubrimiento
    read -p "🌐 Servidor central [$DEFAULT_DISCOVERY_URL]: " DISCOVERY_URL
    DISCOVERY_URL=${DISCOVERY_URL:-$DEFAULT_DISCOVERY_URL}
    
    # Tipo de animales
    echo "🐾 Tipo de animales:"
    echo "1) Ganado bovino"
    echo "2) Ganado porcino"
    echo "3) Ganado ovino"
    echo "4) Aves de corral"
    echo "5) Otros"
    
    while [[ -z "$ANIMAL_TYPE" ]]; do
        read -p "Seleccione (1-5): " animal_choice
        case $animal_choice in
            1) ANIMAL_TYPE="bovine" ;;
            2) ANIMAL_TYPE="porcine" ;;
            3) ANIMAL_TYPE="ovine" ;;
            4) ANIMAL_TYPE="poultry" ;;
            5) ANIMAL_TYPE="other" ;;
            *) echo_error "Opción inválida" ;;
        esac
    done
    
    # Puerto local
    read -p "🔌 Puerto local [$DEFAULT_CAMERA_PORT]: " CAMERA_PORT
    CAMERA_PORT=${CAMERA_PORT:-$DEFAULT_CAMERA_PORT}
    
    echo_success "Configuración completada"
}

auto_config() {
    echo_info "Configuración automática desde parámetros"
    
    # Parsear argumentos de línea de comandos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --camera-id)
                CAMERA_ID="$2"
                shift 2
                ;;
            --name)
                CAMERA_NAME="$2"
                shift 2
                ;;
            --location)
                CAMERA_LOCATION="$2"
                shift 2
                ;;
            --stream)
                CAMERA_STREAM_URL="$2"
                shift 2
                ;;
            --server)
                DISCOVERY_URL="$2"
                shift 2
                ;;
            --animal-type)
                ANIMAL_TYPE="$2"
                shift 2
                ;;
            --port)
                CAMERA_PORT="$2"
                shift 2
                ;;
            *)
                echo_warning "Parámetro desconocido: $1"
                shift
                ;;
        esac
    done
    
    # Valores por defecto si no se proporcionaron
    CAMERA_ID=${CAMERA_ID:-"cam_$(date +%s)"}
    CAMERA_NAME=${CAMERA_NAME:-"Camera $CAMERA_ID"}
    CAMERA_LOCATION=${CAMERA_LOCATION:-"Unknown Location"}
    DISCOVERY_URL=${DISCOVERY_URL:-$DEFAULT_DISCOVERY_URL}
    ANIMAL_TYPE=${ANIMAL_TYPE:-"other"}
    CAMERA_PORT=${CAMERA_PORT:-$DEFAULT_CAMERA_PORT}
    
    if [[ -z "$CAMERA_STREAM_URL" ]]; then
        echo_error "URL del stream es requerida para configuración automática"
        echo_info "Use: --stream rtsp://192.168.1.100/stream"
        exit 1
    fi
}

create_config_file() {
    echo_info "Creando archivo de configuración..."
    
    cat > "$CONFIG_FILE" << EOF
{
    "camera_id": "$CAMERA_ID",
    "name": "$CAMERA_NAME",
    "location": "$CAMERA_LOCATION",
    "stream_url": "$CAMERA_STREAM_URL",
    "discovery_url": "$DISCOVERY_URL",
    "animal_type": "$ANIMAL_TYPE",
    "port": $CAMERA_PORT,
    "capabilities": [
        "video_analysis",
        "animal_detection",
        "movement_tracking",
        "behavior_classification"
    ],
    "hardware_info": {
        "os": "$OS",
        "arch": "$(uname -m)",
        "install_date": "$(date -Iseconds)",
        "version": "$SCRIPT_VERSION"
    },
    "settings": {
        "analysis_enabled": true,
        "recording_enabled": false,
        "movement_sensitivity": "medium",
        "confidence_threshold": 0.7,
        "max_animals_per_frame": 10
    }
}
EOF
    
    echo_success "Archivo de configuración creado: $CONFIG_FILE"
}

create_docker_compose() {
    echo_info "Creando archivo Docker Compose..."
    
    cat > "$DOCKER_COMPOSE_FILE" << EOF
version: "3.9"

services:
  camera-agent:
    image: fixeatai/camera-agent:latest
    container_name: fixeatai-camera-$CAMERA_ID
    restart: unless-stopped
    ports:
      - "$CAMERA_PORT:8080"
    environment:
      # Configuración de la cámara
      - CAMERA_ID=$CAMERA_ID
      - CAMERA_NAME=$CAMERA_NAME
      - CAMERA_LOCATION=$CAMERA_LOCATION
      - CAMERA_STREAM_URL=$CAMERA_STREAM_URL
      - CAMERA_ANIMAL_TYPE=$ANIMAL_TYPE
      
      # Servidor de descubrimiento
      - DISCOVERY_SERVICE_URL=$DISCOVERY_URL
      - AUTO_REGISTER=true
      
      # Configuración del servicio
      - ANIMAL_SERVICE_PORT=8080
      - ANIMAL_LOG_LEVEL=info
      - ANIMAL_DEBUG_MODE=false
      
      # Análisis
      - ANIMAL_ANALYSIS_ENABLED=true
      - ANIMAL_MOVEMENT_SENSITIVITY=medium
      - ANIMAL_CONFIDENCE_THRESHOLD=0.7
      
    volumes:
      # Datos persistentes
      - ./data:/app/data
      - ./logs:/app/logs
      - ./configs:/app/configs
      - $CONFIG_FILE:/app/camera-config.json:ro
      
    networks:
      - fixeatai-network
      
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  fixeatai-network:
    driver: bridge
    name: fixeatai-camera-network

volumes:
  camera-data:
    driver: local
EOF
    
    echo_success "Docker Compose creado: $DOCKER_COMPOSE_FILE"
}

pull_docker_images() {
    echo_info "Descargando imágenes Docker..."
    
    cd "$INSTALL_DIR"
    
    # Descargar imagen principal
    docker pull fixeatai/camera-agent:latest
    
    echo_success "Imágenes Docker descargadas"
}

start_services() {
    echo_info "Iniciando servicios..."
    
    cd "$INSTALL_DIR"
    
    # Iniciar servicios
    docker-compose up -d
    
    # Esperar a que los servicios estén listos
    echo_info "Esperando a que los servicios estén listos..."
    sleep 10
    
    # Verificar estado
    if docker-compose ps | grep -q "Up"; then
        echo_success "Servicios iniciados correctamente"
    else
        echo_error "Error iniciando servicios"
        docker-compose logs
        exit 1
    fi
}

register_camera() {
    echo_info "Registrando cámara en el servidor central..."
    
    # Intentar registrar la cámara
    registration_data=$(cat "$CONFIG_FILE")
    
    response=$(curl -s -X POST "$DISCOVERY_URL/api/v1/cameras/register" \
        -H "Content-Type: application/json" \
        -d "$registration_data" \
        --connect-timeout 10 \
        --max-time 30) || {
        echo_warning "No se pudo conectar al servidor central"
        echo_info "La cámara funcionará en modo standalone"
        return 0
    }
    
    if echo "$response" | grep -q "registered"; then
        echo_success "Cámara registrada exitosamente en el servidor central"
    else
        echo_warning "Respuesta inesperada del servidor: $response"
    fi
}

create_systemd_service() {
    if [[ "$OS" != "ubuntu" && "$OS" != "centos" ]]; then
        return 0
    fi
    
    echo_info "Creando servicio systemd..."
    
    sudo tee /etc/systemd/system/fixeatai-camera.service > /dev/null << EOF
[Unit]
Description=FixeatAI Camera Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable fixeatai-camera.service
    
    echo_success "Servicio systemd creado y habilitado"
}

show_installation_summary() {
    echo_success "¡Instalación completada exitosamente!"
    echo ""
    echo "📋 Resumen de la instalación:"
    echo "=============================="
    echo "🆔 ID de cámara: $CAMERA_ID"
    echo "📝 Nombre: $CAMERA_NAME"
    echo "📍 Ubicación: $CAMERA_LOCATION"
    echo "🎥 Stream: $CAMERA_STREAM_URL"
    echo "🌐 Servidor: $DISCOVERY_URL"
    echo "🔌 Puerto local: $CAMERA_PORT"
    echo "📁 Directorio: $INSTALL_DIR"
    echo ""
    echo "🌐 URLs de acceso:"
    echo "=================="
    echo "📊 Dashboard local: http://localhost:$CAMERA_PORT"
    echo "🔍 Health check: http://localhost:$CAMERA_PORT/health"
    echo "📈 Métricas: http://localhost:$CAMERA_PORT/metrics"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "=================="
    echo "Ver logs: cd $INSTALL_DIR && docker-compose logs -f"
    echo "Reiniciar: cd $INSTALL_DIR && docker-compose restart"
    echo "Detener: cd $INSTALL_DIR && docker-compose down"
    echo "Actualizar: cd $INSTALL_DIR && docker-compose pull && docker-compose up -d"
    echo ""
    echo "📚 Documentación: https://docs.fixeatai.com/camera"
    echo "🆘 Soporte: https://support.fixeatai.com"
}

cleanup_on_error() {
    echo_error "Error durante la instalación. Limpiando..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        cd "$INSTALL_DIR"
        docker-compose down 2>/dev/null || true
        cd /
        sudo rm -rf "$INSTALL_DIR"
    fi
    
    exit 1
}

main() {
    # Configurar trap para limpieza en caso de error
    trap cleanup_on_error ERR
    
    # Crear log file
    sudo touch "$LOG_FILE"
    sudo chmod 666 "$LOG_FILE"
    
    show_banner
    detect_system
    check_requirements
    install_docker
    install_docker_compose
    setup_directories
    
    # Determinar tipo de configuración
    if [[ $# -gt 0 ]]; then
        auto_config "$@"
    else
        interactive_config
    fi
    
    create_config_file
    create_docker_compose
    pull_docker_images
    start_services
    register_camera
    create_systemd_service
    show_installation_summary
    
    echo_success "🎉 ¡FixeatAI Camera instalado y funcionando!"
}

# Ejecutar función principal con todos los argumentos
main "$@"


