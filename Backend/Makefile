# XNFL Fantasy API - Docker Makefile
.PHONY: help build up down logs shell db-shell clean restart build-prod up-prod

# Default environment
COMPOSE_FILE=docker-compose.yml
PROD_COMPOSE_FILE=docker-compose.prod.yml

help: ## Show this help message
	@echo "XNFL Fantasy API Docker Commands"
	@echo "================================"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Development Commands
build: ## Build development containers
	docker-compose build

up: ## Start development environment
	docker-compose up --build

up-d: ## Start development environment in detached mode
	docker-compose up --build -d

down: ## Stop and remove containers
	docker-compose down

restart: ## Restart all services
	docker-compose restart

# Production Commands
build-prod: ## Build production containers
	docker-compose -f $(PROD_COMPOSE_FILE) build

up-prod: ## Start production environment
	docker-compose -f $(PROD_COMPOSE_FILE) up --build -d

down-prod: ## Stop production environment
	docker-compose -f $(PROD_COMPOSE_FILE) down

# Utility Commands
logs: ## Show API logs
	docker-compose logs -f api

logs-db: ## Show database logs
	docker-compose logs -f postgres

shell: ## Open shell in API container
	docker-compose exec api bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d XNFL-Fantasy

# Maintenance Commands
clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

reset: ## Reset everything (clean + rebuild)
	docker-compose down -v
	docker system prune -a -f
	docker-compose up --build

# Database Commands
db-backup: ## Backup database
	docker-compose exec postgres pg_dump -U postgres XNFL-Fantasy > backup_$$(date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "Usage: make db-restore FILE=backup.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U postgres XNFL-Fantasy < $(FILE)

# Health and Status
status: ## Check container status
	docker-compose ps

health: ## Check container health
	@echo "API Health:"
	@docker inspect --format='{{.State.Health.Status}}' xnfl_api 2>/dev/null || echo "Container not running"
	@echo "Database Health:"
	@docker inspect --format='{{.State.Health.Status}}' xnfl_postgres 2>/dev/null || echo "Container not running"

stats: ## Show container resource usage
	docker stats --no-stream

# Development helpers
dev-setup: ## Initial development setup
	cp -n .env.example .env || true
	@echo "Environment file created. Please review .env before starting."

test-api: ## Test API connection
	@curl -f http://localhost:8000/docs > /dev/null 2>&1 && echo "✅ API is accessible" || echo "❌ API is not accessible"

install-deps: ## Install additional dependencies in running container
	docker-compose exec api pip install $(DEPS)

# Environment specific commands
env-dev: ## Switch to development environment
	$(eval COMPOSE_FILE=docker-compose.yml)

env-prod: ## Switch to production environment  
	$(eval COMPOSE_FILE=$(PROD_COMPOSE_FILE))