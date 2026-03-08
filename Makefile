.PHONY: install dev lint fmt typecheck test build

install:
	uv sync

dev:
	uv sync --group dev

lint:
	uv run ruff check src/

fmt:
	uv run ruff format src/

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/

build:
	uv build
