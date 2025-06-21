# Pulse Fitness Makefile

.PHONY: help build up down logs clean restart status

# Default target
help:
	@echo "Pulse Fitness - Available commands:"
	@echo "  build    - Build all Docker images"
	@echo "  up       - Start all services"
	@echo "  down     - Stop all services"
	@echo "  logs     - Show logs from all services"
	@echo "  clean    - Remove all containers, networks, and volumes"
	@echo "  restart  - Restart all services"
	@echo "  status   - Show status of all services"
	@echo "  backend  - Show backend logs only"
	@echo "  ml       - Show ML service logs only"
	@echo "  frontend - Show frontend logs only"
	@echo "  db       - Show database logs only"
	@echo "  test     - Run all tests"
	@echo "  test-backend - Run backend tests only"
	@echo "  test-ml  - Run ML service tests only"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Show logs from all services
logs:
	docker-compose logs -f

# Clean everything
clean:
	docker-compose down -v --rmi all --remove-orphans

# Restart all services
restart:
	docker-compose restart

# Show status
status:
	docker-compose ps

# Show specific service logs
backend:
	docker-compose logs -f backend

ml:
	docker-compose logs -f ml-service

frontend:
	docker-compose logs -f frontend

db:
	docker-compose logs -f db

# Development commands
dev-build:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

dev-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production commands
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Database commands
db-migrate:
	docker-compose exec backend alembic upgrade head

db-rollback:
	docker-compose exec backend alembic downgrade -1

db-reset:
	docker-compose down -v
	docker-compose up -d db
	sleep 10
	docker-compose up -d

# ML Service commands
ml-train:
	docker-compose exec ml-service curl -X POST http://localhost:8001/models/train

# Testing commands
test:
	@echo "Running all tests..."
	@make test-backend
	@make test-ml

test-backend:
	@echo "Running backend tests..."
	docker-compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

test-ml:
	@echo "Running ML service tests..."
	docker-compose exec ml-service pytest tests/ -v --cov=app --cov-report=term-missing

test-backend-local:
	@echo "Running backend tests locally..."
	cd src/backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-ml-local:
	@echo "Running ML service tests locally..."
	cd src/ml_service && pytest tests/ -v --cov=app --cov-report=term-missing

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost/health || echo "Backend health check failed"
	@curl -f http://localhost/ml-health || echo "ML service health check failed"
	@curl -f http://localhost || echo "Frontend health check failed" 