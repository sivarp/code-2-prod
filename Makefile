# Makefile for GitHub Gists API
.PHONY: help install test test-unit test-e2e test-all run lint format docker-build docker-run clean

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e .[dev]

test: ## Run unit tests only
	pytest tests/ -v -m "not e2e"

test-unit: ## Run unit tests only
	pytest tests/ -v -m "not e2e"

test-e2e: ## Run end-to-end tests (requires network)
	pytest tests/ -v -m e2e

test-all: ## Run all tests including e2e
	pytest tests/ -v

lint: ## Run linting (pylint and black check)
	pylint src/ tests/
	black --check src/ tests/

format: ## Format code
	black src/ tests/

run: ## Run the application
	python -m src.main

docker-build: ## Build Docker image
	docker build -t gists-api:1.0.0 .

docker-run: ## Run Docker container
	docker run -p 8081:8080 gists-api:1.0.0

clean: ## Clean up
	rm -rf .pytest_cache __pycache__ .coverage
	find . -name "*.pyc" -delete
