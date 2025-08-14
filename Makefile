.PHONY: help install lint mypy test clean format check dev migrate

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make lint       - Run linter"
	@echo "  make mypy       - Type check with mypy"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make help       - Show this help message"
	@echo "  make format     - Format code with ruff"
	@echo "  make check      - Run ruff check"
	@echo "  make dev        - Run development server"
	@echo "  make migrate    - Run database migrations"
	@echo "  make security   - Run security checks"

install:
	uv sync --frozen

lint:
	uv run ruff check

mypy:
	uv run mypy .

test:
	uv run pytest --cov=src --cov-report=term-missing

format:
	uv run ruff check --fix
	uv run ruff format

check:
	uv run ruff check

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

dev:
	docker compose up -d
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

security:
	uv run bandit -r src
	uv run safety check --full-report