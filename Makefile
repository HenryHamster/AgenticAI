# AgenticAI Development Makefile
# Docker-based development setup for FastAPI backend and Next.js frontend

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Docker compose file
COMPOSE_FILE := docker-compose.yml

# Service names
BACKEND_SERVICE := backend
FRONTEND_SERVICE := frontend

# Default ports
BACKEND_PORT := 8000
FRONTEND_PORT := 3000

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)AgenticAI Docker Development Commands$(NC)"
	@echo "=========================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup targets
.PHONY: setup
setup: ## Setup Docker development environment
	@echo "$(GREEN)Setting up Docker development environment...$(NC)"
	@echo "$(YELLOW)Building Docker images...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✅ Docker environment ready!$(NC)"
	@echo "$(BLUE)Run 'make dev' to start both services$(NC)"

# Development targets
.PHONY: dev
dev: ## Start both backend and frontend in development mode
	@echo "$(GREEN)Starting development servers with Docker...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:$(BACKEND_PORT)/docs$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop both services$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up

.PHONY: dev-detached
dev-detached: ## Start both services in detached mode (background)
	@echo "$(GREEN)Starting development servers in background...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Services started in background$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo "$(BLUE)Use 'make logs' to view logs$(NC)"
	@echo "$(BLUE)Use 'make stop' to stop services$(NC)"

# Individual service targets
.PHONY: backend
backend: ## Start only the backend server
	@echo "$(GREEN)Starting backend server...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up $(BACKEND_SERVICE)

.PHONY: frontend
frontend: ## Start only the frontend server
	@echo "$(GREEN)Starting frontend server...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up $(FRONTEND_SERVICE)

# Build targets
.PHONY: build
build: ## Build all Docker images
	@echo "$(YELLOW)Building Docker images...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✅ All images built successfully$(NC)"

.PHONY: build-no-cache
build-no-cache: ## Build all Docker images without cache (latest versions)
	@echo "$(YELLOW)Building Docker images with latest versions (no cache)...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "$(GREEN)✅ All images built successfully with latest versions$(NC)"

.PHONY: build-backend
build-backend: ## Build only backend image
	@echo "$(YELLOW)Building backend image...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build $(BACKEND_SERVICE)
	@echo "$(GREEN)✅ Backend image built$(NC)"

.PHONY: build-frontend
build-frontend: ## Build only frontend image
	@echo "$(YELLOW)Building frontend image...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build $(FRONTEND_SERVICE)
	@echo "$(GREEN)✅ Frontend image built$(NC)"

# Service management
.PHONY: stop
stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ All services stopped$(NC)"

.PHONY: restart
restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

.PHONY: logs
logs: ## View logs from all services
	@docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f $(BACKEND_SERVICE)

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f $(FRONTEND_SERVICE)

# Testing targets
.PHONY: test
test: ## Run all tests
	@echo "$(YELLOW)Running backend tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec $(BACKEND_SERVICE) python testing/main_test.py
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec $(FRONTEND_SERVICE) npm run lint || echo "$(RED)No lint script found$(NC)"

.PHONY: test-backend
test-backend: ## Run backend tests
	@echo "$(YELLOW)Running backend tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec $(BACKEND_SERVICE) python testing/main_test.py

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec $(FRONTEND_SERVICE) npm run lint || echo "$(RED)No lint script found$(NC)"

# Shell access
.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	@docker-compose -f $(COMPOSE_FILE) exec $(BACKEND_SERVICE) /bin/bash

.PHONY: shell-frontend
shell-frontend: ## Open shell in frontend container
	@docker-compose -f $(COMPOSE_FILE) exec $(FRONTEND_SERVICE) /bin/sh

# Cleanup targets
.PHONY: clean
clean: clean-containers clean-images clean-volumes ## Clean all Docker resources

.PHONY: clean-containers
clean-containers: ## Remove all containers
	@echo "$(YELLOW)Removing containers...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	@echo "$(GREEN)✅ Containers removed$(NC)"

.PHONY: clean-images
clean-images: ## Remove all images
	@echo "$(YELLOW)Removing images...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down --rmi all
	@echo "$(GREEN)✅ Images removed$(NC)"

.PHONY: clean-volumes
clean-volumes: ## Remove all volumes
	@echo "$(YELLOW)Removing volumes...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(GREEN)✅ Volumes removed$(NC)"

.PHONY: clean-all
clean-all: ## Remove everything (containers, images, volumes, networks)
	@echo "$(YELLOW)Cleaning all Docker resources...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down --rmi all -v --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)✅ All Docker resources cleaned$(NC)"

# Status targets
.PHONY: status
status: ## Check status of all services
	@echo "$(YELLOW)Checking service status...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

.PHONY: health
health: ## Check health of services
	@echo "$(YELLOW)Checking service health...$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@curl -s http://localhost:$(BACKEND_PORT)/api/v1/health > /dev/null && \
		echo "$(GREEN)  ✅ Backend is running$(NC)" || \
		echo "$(RED)  ❌ Backend is not running$(NC)"
	@echo "$(YELLOW)Frontend:$(NC)"
	@curl -s http://localhost:$(FRONTEND_PORT) > /dev/null && \
		echo "$(GREEN)  ✅ Frontend is running$(NC)" || \
		echo "$(RED)  ❌ Frontend is not running$(NC)"

# Production targets
.PHONY: prod
prod: ## Build and start production containers
	@echo "$(YELLOW)Building production images...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build
	@echo "$(YELLOW)Starting production services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Production services started$(NC)"

# Database targets (if needed)
.PHONY: db-reset
db-reset: ## Reset database (placeholder for future database operations)
	@echo "$(YELLOW)Database reset not implemented yet$(NC)"

# Default target
.DEFAULT_GOAL := help