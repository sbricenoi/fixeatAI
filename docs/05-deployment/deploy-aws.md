## Despliegue en AWS con Docker (Guía práctica)

Objetivo: ejecutar la API y el MCP en una instancia Linux (EC2) con persistencia de la KB, variables seguras y backups automáticos.

### 1) Infraestructura mínima
- EC2 Linux (Amazon Linux 2023 o Ubuntu LTS).
- Disco persistente (EBS) montado en, por ejemplo, `/srv/fixeatAI`.
- Security Group: puertos 8000 (API) y 7070 (MCP) si se exponen. Sugerido: poner detrás de ALB o permitir solo IPs internas/VPN.
- Rol IAM opcional: acceso S3 para respaldos.

### 2) Instalar Docker y Compose
```bash
sudo yum update -y || sudo apt update -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
sudo systemctl enable --now docker
sudo curl -L https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3) Persistencia de la KB (bind mount)
1. Crear carpeta en el disco persistente y dar permisos:
```bash
sudo mkdir -p /srv/fixeatAI/chroma_store
sudo chown -R $USER:$USER /srv/fixeatAI
```
2. Crear `docker-compose.override.yml` junto a `docker-compose.yml`:
```yaml
services:
  mcp:
    volumes:
      - /srv/fixeatAI/chroma_store:/data/chroma
    environment:
      - CHROMA_PATH=/data/chroma
  api:
    environment:
      - MCP_SERVER_URL=http://mcp:7000
```
3. Variables (opcional): usar `.env` o inyección por Secrets/SSM.

### 4) Variables y secretos
- En dev puedes usar `.env` en la instancia:
```bash
echo 'OPENAI_API_KEY=sk-...' | sudo tee -a /srv/fixeatAI/.env
```
- En prod, preferir AWS SSM Parameter Store o Secrets Manager + export en `docker compose` (o `env_file`).

### 5) Levantar servicios
```bash
docker compose pull || true
docker compose up -d
```
Verificar salud:
```bash
curl -s http://127.0.0.1:7070/health
curl -s http://127.0.0.1:8000/health
```

### 6) Backups automáticos de la KB a S3
1. Instalar AWS CLI (si no está) y asignar rol IAM con permisos `s3:PutObject`/`GetObject` al bucket.
```bash
sudo yum install -y awscli || sudo apt install -y awscli
```
2. Script `/usr/local/bin/fixeatai_kb_backup.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
DATA_DIR=/srv/fixeatAI/chroma_store
S3_PREFIX=s3://TU_BUCKET/fixeatAI/kb
STAMP=$(date +%F-%H%M%S)
TMP=/tmp/kb_${STAMP}.tgz
tar -czf "$TMP" -C "$DATA_DIR" .
aws s3 cp "$TMP" "$S3_PREFIX/KB_${STAMP}.tgz"
find /tmp -maxdepth 1 -name 'kb_*.tgz' -mtime +3 -delete
```
```bash
sudo chmod +x /usr/local/bin/fixeatai_kb_backup.sh
echo '0 3 * * * /usr/local/bin/fixeatai_kb_backup.sh >> /var/log/fixeatai_backup.log 2>&1' | sudo tee /etc/cron.d/fixeatai_backup
sudo systemctl restart cron || sudo systemctl restart crond
```

### 7) Restore de KB desde S3
```bash
LATEST=$(aws s3 ls s3://TU_BUCKET/fixeatAI/kb/ | sort | tail -1 | awk '{print $4}')
aws s3 cp s3://TU_BUCKET/fixeatAI/kb/$LATEST /tmp/KB_restore.tgz
docker compose stop mcp
rm -rf /srv/fixeatAI/chroma_store/*
sudo tar -xzf /tmp/KB_restore.tgz -C /srv/fixeatAI/chroma_store
docker compose start mcp
```

### 8) Buenas prácticas de producción
- Usar EBS para `/srv/fixeatAI` (snapshots programados). Evitar instance-store efímero.
- `restart: unless-stopped` en los servicios (ya presente).
- Monitorizar: espacio en disco, errores de escritura, backups y salud (`/health`).
- Seguridad: restringir puertos en SG o poner detrás de ALB; secretos en SSM/Secrets Manager.
- Escalado/HA: evaluar `pgvector` en RDS o EFS si se requiere compartir KB entre múltiples instancias.

### 9) Verificación de persistencia
1. Ingestar un documento y ver `hits`.
2. `docker compose restart mcp` y repetir `kb_search`: los `hits` deben persistir.
3. Reiniciar la instancia: los `hits` deben persistir (bind mount al disco EBS).


