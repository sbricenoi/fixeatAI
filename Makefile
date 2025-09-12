.PHONY: help run mcp test clean install lint kb etl

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	pip install -e .

run: ## Ejecutar el servicio principal (API)
	@echo "🚀 Iniciando servicio principal en puerto 8000..."
	docker-compose up --build

mcp: ## Ejecutar solo el servidor MCP
	@echo "🔧 Iniciando servidor MCP en puerto 7070..."
	docker-compose up mcp --build

etl: ## Ejecutar ETL Service independiente
	@echo "⚙️ Iniciando ETL Service en puerto 9000..."
	docker-compose up etl-service --build

all: ## Ejecutar todos los servicios (API + MCP + ETL)
	@echo "🌟 Iniciando todos los servicios..."
	docker-compose up --build

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-api: ## Ver logs del servicio API
	docker-compose logs -f api

logs-mcp: ## Ver logs del servicio MCP
	docker-compose logs -f mcp

logs-etl: ## Ver logs del ETL Service
	docker-compose logs -f etl-service

stop: ## Detener todos los servicios
	docker-compose down

clean: ## Limpiar contenedores e imágenes
	docker-compose down --rmi all --volumes --remove-orphans

test: ## Ejecutar pruebas
	python -m pytest tests/ -v

lint: ## Ejecutar linting
	python -m pylint app/ services/ mcp/

# Comandos de desarrollo
dev-api: ## Ejecutar API en modo desarrollo
	cd app && python -m uvicorn main:app --reload --port 8000

dev-mcp: ## Ejecutar MCP en modo desarrollo
	cd mcp && python server_demo.py

dev-etl: ## Ejecutar ETL Service en modo desarrollo
	cd services/etl-service && python main.py

# Health checks
health: ## Verificar salud de todos los servicios
	@echo "🔍 Verificando servicios..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ API no disponible"
	@curl -s http://localhost:7070/health | jq . || echo "❌ MCP no disponible"
	@curl -s http://localhost:9000/health | jq . || echo "❌ ETL Service no disponible"