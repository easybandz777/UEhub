# UE Hub Development Makefile

.PHONY: help install dev build test clean api migrate seed worker sdk

# Default target
help:
	@echo "UE Hub Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install all dependencies"
	@echo "  dev         Start all development servers"
	@echo ""
	@echo "Backend:"
	@echo "  api         Start backend API server"
	@echo "  migrate     Run database migrations"
	@echo "  seed        Seed database with initial data"
	@echo "  worker      Start background worker"
	@echo ""
	@echo "Frontend:"
	@echo "  frontend    Start frontend development server"
	@echo "  sdk         Generate TypeScript SDK from OpenAPI"
	@echo ""
	@echo "Development:"
	@echo "  build       Build all packages"
	@echo "  test        Run all tests"
	@echo "  lint        Run linting"
	@echo "  clean       Clean build artifacts"

# Installation
install:
	pnpm install

# Development servers
dev:
	pnpm dev

api:
	cd backend && python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && pnpm dev

worker:
	cd worker && python main.py

# Database
migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(name)"

migrate-rollback:
	cd backend && alembic downgrade -1

seed:
	cd backend && python -m app.scripts.seed

# SDK Generation
sdk:
	cd backend && python -m app.scripts.generate_sdk

# Build and test
build:
	pnpm build

test:
	pnpm test

test-backend:
	cd backend && python -m pytest

test-frontend:
	cd frontend && pnpm test

lint:
	pnpm lint

# Cleanup
clean:
	pnpm clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +

# Docker
docker-build:
	docker build -f infra/Dockerfile.backend -t ue-hub-backend .

docker-dev:
	docker-compose -f infra/docker-compose.dev.yml up

docker-down:
	docker-compose -f infra/docker-compose.dev.yml down

# Database utilities
db-reset:
	cd backend && alembic downgrade base && alembic upgrade head

db-shell:
	cd backend && python -c "from app.core.db import get_sync_db; from sqlalchemy import text; db = next(get_sync_db()); print('Database shell ready. Use db.execute(text(\"SELECT 1\")) to test.'); import IPython; IPython.embed()"

# Deployment
deploy-backend:
	fly deploy --config infra/fly.toml

# Development utilities
logs-backend:
	fly logs --config infra/fly.toml

logs-worker:
	# Add worker log command when implemented

check-deps:
	pnpm audit
	cd backend && pip-audit

format:
	cd backend && black app/ && isort app/
	pnpm format

# Environment setup
env-example:
	cp backend/.env.example backend/.env
	@echo "Please edit backend/.env with your configuration"

# Health checks
health:
	curl -f http://localhost:8000/health || echo "Backend not running"
	curl -f http://localhost:3000 || echo "Frontend not running"

# Module scaffolding
create-module:
	@if [ -z "$(name)" ]; then echo "Usage: make create-module name=module_name"; exit 1; fi
	@echo "Creating module: $(name)"
	mkdir -p backend/app/modules/$(name)
	touch backend/app/modules/$(name)/__init__.py
	touch backend/app/modules/$(name)/router.py
	touch backend/app/modules/$(name)/service.py
	touch backend/app/modules/$(name)/repository.py
	touch backend/app/modules/$(name)/schemas.py
	mkdir -p frontend/src/features/$(name)
	@echo "Module $(name) created. Don't forget to:"
	@echo "1. Add router to backend/app/api.py"
	@echo "2. Create Alembic migration"
	@echo "3. Add feature flag if needed"
