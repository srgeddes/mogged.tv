.PHONY: dev test test-cov lint format clean check sync nuke docker-up docker-down migrate migrate-new seed-trivia

# Install dependencies
sync:
	uv sync

# Start dev server with hot reload
dev:
	uv run fastapi dev src/main.py

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=src

# Lint only (no fixes)
lint:
	uv run ruff check src/ tests/

# Format only
format:
	uv run ruff format src/ tests/

# Lint with auto-fix + format (run this after every edit)
clean:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

# Lint + format check (CI, no modifications)
check:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

# Run all migrations
migrate:
	uv run alembic upgrade head

# Create a new migration (usage: make migrate-new msg="add users table")
migrate-new:
	uv run alembic revision --autogenerate -m "$(msg)"

# Start local dev environment
docker-up:
	docker compose up -d

# Stop local dev environment
docker-down:
	docker compose down

# Seed trivia questions (fetches from OpenTDB + inserts brain rot bank)
seed-trivia:
	PYTHONPATH=src uv run python -m trivia.seed

# Remove build artifacts and caches
nuke:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/
