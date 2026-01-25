# ---------------------------------------------------------
# Project variables
# ---------------------------------------------------------
POETRY = poetry
PYTHON = $(POETRY) run python
PYTEST = $(POETRY) run pytest
TOX = $(POETRY) run tox
COVERAGE = $(POETRY) run coverage
RUFF = $(POETRY) run ruff
BLACK = $(POETRY) run black
MYPY = $(POETRY) run mypy
PYRIGHT = $(POETRY) run pyright

# Default target
.DEFAULT_GOAL := help

# Colors for nicer output
GREEN := \033[0;32m
NC := \033[0m

# ---------------------------------------------------------
# Default target
# ---------------------------------------------------------
help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make lint           Run all linters (ruff + black check)"
	@echo "  make format         Auto-format code (ruff + black)"
	@echo "  make typecheck      Run mypy + pyright"
	@echo "  make test           Run tests across all Python versions (nox)"
	@echo "  make coverage       Run pytest with coverage"
	@echo "  make clean          Remove caches and build artifacts"

# ---------------------------------------------------------
# Installation
# ---------------------------------------------------------
install:
	@echo "$(GREEN)Installing dependencies with Poetry...$(NC)"
	$(POETRY) install --with dev

# ---------------------------------------------------------
# Linting & formatting & type checking
# ---------------------------------------------------------
lint:
	@echo "$(GREEN)Running linting (ruff + black)...$(NC)"
	nox -s lint

format:
	@echo "$(GREEN)Running formatting (black + ruff)...$(NC)"
	nox -s format

typecheck:
	@echo "$(GREEN)Running type checking (mypy + pyright)...$(NC)"
	nox -s typecheck

# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------
test:
	@echo "$(GREEN)Running tests via nox...$(NC)"
	nox -s tests

# ---------------------------------------------------------
# Build
# ---------------------------------------------------------
build:
	@echo "$(GREEN)Building package via Poetry...$(NC)"
	nox -s build

publish:
	$(POETRY) publish

# ---------------------------------------------------------
# Report
# ---------------------------------------------------------
report:
	- ${PYTHON} upload-reports.py gitleaks.json
# 	- ${PYTHON} upload-reports.py semgrep.json

# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
clean:
	@echo "$(GREEN)Cleaning project...$(NC)"
	rm -rf .nox .pytest_cache .mypy_cache .ruff_cache .coverage
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
