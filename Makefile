# ---------------------------------------------------------
# Project variables
# ---------------------------------------------------------
POETRY = poetry
PYTHON = $(POETRY) run python
PYTEST = $(POETRY) run pytest
RUFF = $(POETRY) run ruff
BLACK = $(POETRY) run black
MYPY = $(POETRY) run mypy
PYRIGHT = $(POETRY) run pyright

# ---------------------------------------------------------
# Default target
# ---------------------------------------------------------
help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make lint           Run all linters (ruff + black check)"
	@echo "  make format         Auto-format code (ruff + black)"
	@echo "  make typecheck      Run mypy + pyright"
	@echo "  make test           Run pytest"
	@echo "  make coverage       Run pytest with coverage"
	@echo "  make docs           Build Sphinx documentation"
	@echo "  make clean          Remove caches and build artifacts"

# ---------------------------------------------------------
# Installation
# ---------------------------------------------------------
install:
	$(POETRY) install --with dev

# ---------------------------------------------------------
# Linting & formatting
# ---------------------------------------------------------
lint:
	$(RUFF) check src tests
	$(BLACK) --check src tests

format:
	$(RUFF) check --fix src tests
	$(BLACK) src tests

# ---------------------------------------------------------
# Type checking
# ---------------------------------------------------------
typecheck:
	$(MYPY) src
	$(PYRIGHT)

# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------
test:
	$(PYTEST)

coverage:
	$(PYTEST) --cov=src

# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
	rm -rf build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
