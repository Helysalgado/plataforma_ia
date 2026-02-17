.PHONY: help dev dev-backend dev-frontend test test-backend test-frontend test-e2e lint format migrate makemigrations seed clean reset-db

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_EXEC = $(DOCKER_COMPOSE) exec

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

##@ Help

help: ## Show this help message
	@echo '$(GREEN)BioAI Hub — Makefile Commands$(NC)'
	@echo ''
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

dev: ## Start all services (frontend + backend + db)
	@echo '$(GREEN)Starting all services...$(NC)'
	$(DOCKER_COMPOSE) up --build

dev-detached: ## Start all services in background
	@echo '$(GREEN)Starting all services in background...$(NC)'
	$(DOCKER_COMPOSE) up --build -d

dev-backend: ## Start only backend + database
	@echo '$(GREEN)Starting backend services...$(NC)'
	$(DOCKER_COMPOSE) up backend db

dev-frontend: ## Start only frontend
	@echo '$(GREEN)Starting frontend...$(NC)'
	$(DOCKER_COMPOSE) up frontend

stop: ## Stop all services
	@echo '$(YELLOW)Stopping all services...$(NC)'
	$(DOCKER_COMPOSE) stop

down: ## Stop and remove containers
	@echo '$(YELLOW)Stopping and removing containers...$(NC)'
	$(DOCKER_COMPOSE) down

##@ Database

migrate: ## Run Django migrations
	@echo '$(GREEN)Running migrations...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend python manage.py migrate

makemigrations: ## Create Django migrations
	@echo '$(GREEN)Creating migrations...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend python manage.py makemigrations

seed: ## Seed initial data (roles, test users, resources)
	@echo '$(GREEN)Seeding database...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend python manage.py seed_roles
	$(DOCKER_COMPOSE_EXEC) backend python manage.py seed_data

reset-db: ## Reset database (WARNING: deletes all data)
	@echo '$(YELLOW)Resetting database...$(NC)'
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d db
	@sleep 5
	$(DOCKER_COMPOSE) up -d backend
	@sleep 5
	$(MAKE) migrate
	$(MAKE) seed
	@echo '$(GREEN)Database reset complete!$(NC)'

##@ Testing

test: ## Run all tests (backend + frontend)
	@echo '$(GREEN)Running all tests...$(NC)'
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend: ## Run backend tests (pytest)
	@echo '$(GREEN)Running backend tests...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend pytest --cov=apps --cov-report=term --cov-report=html

test-backend-unit: ## Run backend unit tests only
	@echo '$(GREEN)Running backend unit tests...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend pytest apps/ -m "not integration"

test-backend-integration: ## Run backend integration tests only
	@echo '$(GREEN)Running backend integration tests...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend pytest apps/ -m integration

test-frontend: ## Run frontend tests (Jest)
	@echo '$(GREEN)Running frontend tests...$(NC)'
	$(DOCKER_COMPOSE_EXEC) frontend npm test -- --coverage --watchAll=false

test-e2e: ## Run E2E tests (Playwright)
	@echo '$(GREEN)Running E2E tests...$(NC)'
	cd frontend && npm run test:e2e

test-e2e-ui: ## Run E2E tests with UI (debugging)
	@echo '$(GREEN)Running E2E tests with UI...$(NC)'
	cd frontend && npm run test:e2e:ui

##@ Code Quality

lint: ## Lint backend + frontend
	@echo '$(GREEN)Linting code...$(NC)'
	$(MAKE) lint-backend
	$(MAKE) lint-frontend

lint-backend: ## Lint backend (flake8)
	@echo '$(GREEN)Linting backend...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend flake8 apps/ config/

lint-frontend: ## Lint frontend (ESLint)
	@echo '$(GREEN)Linting frontend...$(NC)'
	$(DOCKER_COMPOSE_EXEC) frontend npm run lint

format: ## Format code (black + prettier)
	@echo '$(GREEN)Formatting code...$(NC)'
	$(MAKE) format-backend
	$(MAKE) format-frontend

format-backend: ## Format backend (black)
	@echo '$(GREEN)Formatting backend...$(NC)'
	$(DOCKER_COMPOSE_EXEC) backend black apps/ config/

format-frontend: ## Format frontend (prettier)
	@echo '$(GREEN)Formatting frontend...$(NC)'
	$(DOCKER_COMPOSE_EXEC) frontend npm run format

##@ Django Management

shell: ## Open Django shell
	$(DOCKER_COMPOSE_EXEC) backend python manage.py shell

createsuperuser: ## Create Django superuser
	$(DOCKER_COMPOSE_EXEC) backend python manage.py createsuperuser

collectstatic: ## Collect static files
	$(DOCKER_COMPOSE_EXEC) backend python manage.py collectstatic --noinput

##@ Logs

logs: ## Show logs for all services
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Show backend logs
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Show frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Show database logs
	$(DOCKER_COMPOSE) logs -f db

##@ Cleanup

clean: ## Remove containers, volumes, and images
	@echo '$(YELLOW)Cleaning up...$(NC)'
	$(DOCKER_COMPOSE) down -v --rmi local
	rm -rf backend/__pycache__
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	@echo '$(GREEN)Cleanup complete!$(NC)'

clean-cache: ## Clean Python cache and Next.js cache
	@echo '$(YELLOW)Cleaning cache...$(NC)'
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next
	@echo '$(GREEN)Cache cleaned!$(NC)'

##@ Installation (Local without Docker)

install-backend: ## Install backend dependencies locally
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies locally
	cd frontend && npm install

install: ## Install all dependencies locally
	$(MAKE) install-backend
	$(MAKE) install-frontend

##@ CI/CD

ci: ## Run full CI pipeline (lint + test)
	@echo '$(GREEN)Running CI pipeline...$(NC)'
	$(MAKE) lint
	$(MAKE) test
	@echo '$(GREEN)CI pipeline complete!$(NC)'

##@ Production

build-prod: ## Build production images
	@echo '$(GREEN)Building production images...$(NC)'
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml build

deploy-staging: ## Deploy to staging
	@echo '$(YELLOW)Deploying to staging...$(NC)'
	# TODO: Add staging deployment commands

deploy-production: ## Deploy to production
	@echo '$(YELLOW)Deploying to production...$(NC)'
	# TODO: Add production deployment commands

##@ Info

ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

status: ## Show project status
	@echo '$(GREEN)Project Status:$(NC)'
	@echo ''
	@echo 'Services:'
	@$(DOCKER_COMPOSE) ps
	@echo ''
	@echo 'Disk usage:'
	@docker system df
