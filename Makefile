.PHONY: help install dev-install format lint type-check test test-cov security clean all

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	uv sync

dev-install:  ## Install development dependencies
	uv sync --all-extras

format:  ## Format code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

lint:  ## Lint code with ruff
	ruff check src/ tests/

type-check:  ## Run type checking with mypy and pyright
	mypy src/
	pyright src/

security:  ## Run security checks with bandit
	bandit -r src/

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=src/uacs --cov-report=term-missing --cov-report=html

test-parallel:  ## Run tests in parallel
	pytest tests/ -n auto

test-watch:  ## Run tests in watch mode
	pytest-watch

all: format lint type-check security test  ## Run all checks

clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	uv build

publish-test:  ## Publish to TestPyPI
	uv publish --repository testpypi

publish:  ## Publish to PyPI
	uv publish

pre-commit-install:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files
