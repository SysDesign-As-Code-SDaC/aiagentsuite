# AI Agent Suite - Development Makefile

.PHONY: help install install-dev test test-cov lint format clean build docs docker-build docker-run

# Default target
help: ## Show this help message
	@echo "AI Agent Suite Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install the package
	pip install -e .

install-dev: ## Install with development dependencies
	pip install -e .[dev]

# Testing
test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=aiagentsuite --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	ptw

# Code Quality
lint: ## Run all linting tools
	black --check src/
	isort --check-only src/
	flake8 src/
	mypy src/

format: ## Format code with black and isort
	black src/
	isort src/

# TypeScript
ts-build: ## Build TypeScript components
	cd typescript && npm run build

ts-test: ## Run TypeScript tests
	cd typescript && npm test

ts-lint: ## Lint TypeScript code
	cd typescript && npm run lint

# Building
build: ## Build Python package
	python -m build

build-all: build ts-build ## Build both Python and TypeScript

# Documentation
docs: ## Build documentation
	sphinx-build docs/ docs/_build/html

docs-serve: docs ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

# Docker
docker-build: ## Build Docker image
	docker build -t aiagentsuite .

docker-run: ## Run Docker container
	docker run -it --rm aiagentsuite

docker-compose-up: ## Start all services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop all services
	docker-compose down

# Cleaning
clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/**/*.pyc
	rm -rf src/**/__pycache__/
	cd typescript && rm -rf dist/ node_modules/

clean-all: clean ## Clean everything including caches
	rm -rf .mypy_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development workflow
dev-setup: install-dev ## Set up development environment
	pre-commit install

dev-test: lint test-cov ## Run full development test suite

# Release
release-check: dev-test build ## Check everything before release
	twine check dist/*

# CLI shortcuts (development/debugging only)
constitution: ## Show AI agent constitution (dev tool)
	aiagentsuite constitution

protocols: ## List available protocols (dev tool)
	aiagentsuite protocols

memory: ## Show active memory context (dev tool)
	aiagentsuite memory active

# Utility
count-lines: ## Count lines of code
	find src/ -name "*.py" -exec wc -l {} + | tail -1

deps-update: ## Update dependencies
	pip install --upgrade pip-tools
	pip-compile --upgrade
	pip-sync

# Architecture Analysis
analyze: ## Run AST-based architecture analysis
	python -m src.aiagentsuite.core.architecture_analyzer src/

analyze-docs: ## Generate architecture documentation only
	python -m src.aiagentsuite.core.architecture_analyzer src/ --output-docs docs/ARCHITECTURE.md

analyze-diagrams: ## Generate architecture diagrams only
	python -m src.aiagentsuite.core.architecture_analyzer src/ --output-diagrams docs/diagrams

analyze-all: analyze-docs analyze-diagrams ## Generate both docs and diagrams
