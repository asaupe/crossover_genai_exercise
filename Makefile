# Makefile for GenAI Email Processing System

.PHONY: help install dev-install test test-coverage lint format clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

test:  ## Run tests
	pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:  ## Run all linting tools
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

run:  ## Run the application
	python -m src.main

run-dev:  ## Run the application in development mode
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

docker-build:  ## Build Docker image
	docker build -t genai-email-processor .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env genai-email-processor

setup-env:  ## Copy environment template
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

check-env:  ## Check if required environment variables are set
	@python -c "import os; missing = [v for v in ['OPENAI_API_KEY'] if not os.getenv(v)]; print('Missing env vars:', missing) if missing else print('All required env vars set')"
