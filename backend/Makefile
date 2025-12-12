# InGazo Backend Makefile
# Common commands for development and deployment

.PHONY: help install dev build up down logs shell migrate makemigrations test lint format clean

# Default target
help:
	@echo "InGazo Backend - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Start development server"
	@echo "  make shell        - Open Django shell"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all containers"
	@echo "  make down         - Stop all containers"
	@echo "  make logs         - View container logs"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make superuser    - Create superuser"
	@echo ""
	@echo "Production:"
	@echo "  make build-prod   - Build production images"
	@echo "  make up-prod      - Start production containers"
	@echo "  make down-prod    - Stop production containers"

# Install dependencies
install:
	pip install -r requirements.txt

# Start development server (without Docker)
dev:
	python manage.py runserver 0.0.0.0:8000

# Build Docker images
build:
	docker-compose build

# Start all containers
up:
	docker-compose up -d

# Stop all containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Open Django shell
shell:
	docker-compose exec backend python manage.py shell

# Run migrations
migrate:
	docker-compose exec backend python manage.py migrate

# Create migrations
makemigrations:
	docker-compose exec backend python manage.py makemigrations

# Create superuser
superuser:
	docker-compose exec backend python manage.py createsuperuser

# Run tests
test:
	docker-compose exec backend pytest

# Run tests locally
test-local:
	pytest

# Run linters
lint:
	flake8 apps/ core/
	isort --check-only apps/ core/
	black --check apps/ core/

# Format code
format:
	isort apps/ core/
	black apps/ core/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete

# Production commands
build-prod:
	docker-compose -f docker-compose.prod.yml build

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

down-prod:
	docker-compose -f docker-compose.prod.yml down

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

# Database backup (production)
backup-db:
	docker-compose exec db pg_dump -U $${POSTGRES_USER} $${POSTGRES_DB} > backup_$$(date +%Y%m%d_%H%M%S).sql

# Collect static files
collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

