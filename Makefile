# ---------------------------------------------------------
# Project variables
# ---------------------------------------------------------
POETRY = poetry
PYTHON = $(POETRY) run python
PYTEST = $(POETRY) run pytest
COVERAGE = $(POETRY) run coverage
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
	@echo "  make clean          Remove caches and build artifacts"

# ---------------------------------------------------------
# Installation
# ---------------------------------------------------------
install:
	$(POETRY) install --with dev

# ---------------------------------------------------------
# Linting & formatting & type checking
# ---------------------------------------------------------
lint:
	$(RUFF) check src tests
	$(BLACK) --check src tests

format:
	$(RUFF) check --fix src tests
	$(BLACK) src tests

typecheck:
	$(PYRIGHT) src
	-$(MYPY) src

# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------
test:
	$(PYTEST)

coverage:
	$(PYTEST) --cov=src
	$(COVERAGE) xml

# ---------------------------------------------------------
# Build
# ---------------------------------------------------------
build:
	$(POETRY) build

publish:
	$(POETRY) publish


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------
report:
	- ${PYTHON} upload-reports.py gitleaks.json
	- ${PYTHON} upload-reports.py semgrep.json

# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
	rm -rf build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
