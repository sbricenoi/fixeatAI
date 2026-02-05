.PHONY: help install dev-mcp run test clean docker-up docker-down docker-rebuild

help:
	@echo "🔧 FIXEAT AI - Predictor de Fallas"
	@echo "=================================="
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  📦 install          - Instalar dependencias del proyecto"
	@echo "  🚀 dev-mcp          - Levantar MCP Server (KB) en desarrollo"
	@echo "  🚀 run              - Levantar API Server en desarrollo"
	@echo "  🧪 test             - Ejecutar tests"
	@echo "  🧹 clean            - Limpiar archivos temporales"
	@echo ""
	@echo "  🐳 docker-up        - Levantar servicios con Docker Compose"
	@echo "  🐳 docker-down      - Detener servicios Docker"
	@echo "  🐳 docker-rebuild   - Rebuild completo de imágenes Docker"
	@echo "  🐳 docker-logs      - Ver logs de servicios Docker"
	@echo ""
	@echo "  📚 ingest-kb        - Ingestar documentos en KB (requiere urls.txt)"
	@echo "  🔍 search-kb        - Buscar en KB (requiere QUERY='...')"
	@echo ""

install:
	@echo "📦 Instalando dependencias..."
	pip install --upgrade pip
	pip install -e .
	@echo "✅ Dependencias instaladas"

dev-mcp:
	@echo "🚀 Levantando MCP Server (Knowledge Base)..."
	@echo "   Puerto: 7000"
	@echo "   Ctrl+C para detener"
	cd mcp && uvicorn server_demo:app --reload --port 7000

run:
	@echo "🚀 Levantando API Server (Predictor de Fallas)..."
	@echo "   Puerto: 8000"
	@echo "   Ctrl+C para detener"
	@echo "   Docs: http://localhost:8000/docs"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Ejecutando tests..."
	pytest tests/ -v

clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Limpieza completada"

# ============================================================
# Docker Commands
# ============================================================

docker-up:
	@echo "🐳 Levantando servicios con Docker Compose..."
	docker-compose up -d
	@echo "✅ Servicios levantados"
	@echo ""
	@echo "Para ver logs: make docker-logs"
	@echo "Para detener: make docker-down"

docker-down:
	@echo "🐳 Deteniendo servicios Docker..."
	docker-compose down
	@echo "✅ Servicios detenidos"

docker-rebuild:
	@echo "🐳 Rebuilding servicios Docker (sin caché)..."
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Rebuild completado"

docker-logs:
	@echo "📋 Logs de servicios Docker (Ctrl+C para salir)..."
	docker-compose logs -f --tail=100

docker-ps:
	@echo "📊 Estado de servicios Docker:"
	docker-compose ps

# ============================================================
# Knowledge Base Commands
# ============================================================

ingest-kb:
	@echo "📚 Ingesta de documentos en Knowledge Base..."
	@if [ -f urls.txt ]; then \
		python ingestar_via_api.py --urls urls.txt; \
	else \
		echo "❌ Archivo urls.txt no encontrado"; \
		echo "   Crear urls.txt con una URL por línea"; \
	fi

search-kb:
	@echo "🔍 Búsqueda en Knowledge Base..."
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Falta parámetro QUERY"; \
		echo "   Uso: make search-kb QUERY='problema bomba'"; \
	else \
		curl -X POST http://localhost:7070/tools/kb_search \
			-H 'Content-Type: application/json' \
			-d '{"query": "$(QUERY)", "top_k": 5}' | python3 -m json.tool; \
	fi

# ============================================================
# Deployment Commands
# ============================================================

deploy-prod:
	@echo "🚀 Desplegando a producción..."
	@echo "⚠️  ADVERTENCIA: Esto actualizará el servidor productivo"
	@echo ""
	@read -p "¿Continuar? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	ssh -i fixeatIA.pem ec2-user@18.220.79.28 '\
		cd fixeatAI && \
		git pull origin main && \
		docker-compose build --no-cache && \
		docker-compose up -d && \
		docker-compose ps'
	@echo "✅ Deployment completado"
	@echo "   Verificar: curl http://18.220.79.28:8000/health"

# ============================================================
# Health Checks
# ============================================================

health-local:
	@echo "🏥 Health Check Local..."
	@echo ""
	@echo "API:"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API no responde"
	@echo ""
	@echo "MCP:"
	@curl -s http://localhost:7070/health | python3 -m json.tool || echo "❌ MCP no responde"

health-prod:
	@echo "🏥 Health Check Producción..."
	@echo ""
	@echo "API:"
	@curl -s http://18.220.79.28:8000/health | python3 -m json.tool || echo "❌ API no responde"
	@echo ""
	@echo "MCP:"
	@curl -s http://18.220.79.28:7070/health | python3 -m json.tool || echo "❌ MCP no responde"
