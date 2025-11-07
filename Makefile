.PHONY: help version venv clean install setup test coverage tox tox-lint tox-type lint lint-check format format-check type pre-commit pre-commit-install pre-commit-update check build publish-test publish

.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV_DIR := .venv
SRC_DIR := click_extended
PIP := $(VENV_DIR)/bin/pip

# Overview
version:
	@echo "Package version: $$(grep '^version =' pyproject.toml | cut -d'"' -f2)"

help:
	@echo "Available commands:"
	@echo ""
	@echo "  General:"
	@echo "    make help                Show this help message"
	@echo "    make version             Show current package version"
	@echo ""
	@echo "  Environment:"
	@echo "    make venv                Create virtual environment and install dependencies"
	@echo "    make clean               Remove virtual environment and build artifacts"
	@echo "    make install             Install the package dependencies"
	@echo ""
	@echo "  Testing:"
	@echo "    make test                Run tests with verbose output"
	@echo "    make coverage            Run tests with coverage report and open in browser"
	@echo "    make tox                 Run tests across all Python versions"
	@echo "    make tox-lint            Run linting with tox"
	@echo "    make tox-type            Run type checking with tox"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make lint                Auto-fix issues with ruff"
	@echo "    make lint-check          Check code with ruff (no auto-fix)"
	@echo "    make format              Format code with ruff"
	@echo "    make format-check        Check code formatting without changes"
	@echo "    make type                Run type checking with mypy"
	@echo ""
	@echo "  Pre-commit:"
	@echo "    make pre-commit          Run all pre-commit hooks"
	@echo "    make pre-commit-install  Install pre-commit hooks"
	@echo "    make pre-commit-update   Update pre-commit hooks"
	@echo ""
	@echo "  Combined Checks:"
	@echo "    make check               Run all checks (lint, format, type, test)"
	@echo ""
	@echo "  Deployment:"
	@echo "    make build               Build distribution packages"
	@echo "    make publish-test        Publish to Test PyPI"
	@echo "    make publish             Publish to PyPI"
	@echo ""

# Environment
venv:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
	else \
		echo "Checking Python version..."; \
		$(PYTHON) --version | grep -qE "Python 3\.(1[0-9]|[2-9][0-9])" || \
			(echo "Error: Python 3.10 or higher is required" && exit 1); \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Installing dependencies..."; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -e ".[dev,build]"; \
		echo "Installation complete."; \
		echo "Activate the virtual environment with 'source $(VENV_DIR)/bin/activate'"; \
	fi

clean:
	rm -rf $(VENV_DIR) venv
	rm -rf *.egg-info
	rm -rf dist build
	rm -rf htmlcov .coverage
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "To exit the deleted virtual environment, run 'deactivate'"; \
	fi

install:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "You are not in a virtual environment."; \
	else \
		$(PIP) install -e ".[dev,build]"; \
	fi

# Testing
test:
	@echo "Running tests with coverage..."
	@$(VENV_DIR)/bin/pytest -v

coverage:
	@$(VENV_DIR)/bin/pytest --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@$(PYTHON) -m webbrowser htmlcov/index.html || open htmlcov/index.html || xdg-open htmlcov/index.html

tox:
	@$(VENV_DIR)/bin/tox

tox-lint:
	@$(VENV_DIR)/bin/tox -e lint

tox-type:
	@$(VENV_DIR)/bin/tox -e type

# Linting
lint:
	@$(VENV_DIR)/bin/ruff check --fix .

lint-check:
	@$(VENV_DIR)/bin/ruff check .

# Formatting
format:
	@$(VENV_DIR)/bin/ruff format .

format-check:
	@$(VENV_DIR)/bin/ruff format --check .

# Type checking
type:
	@$(VENV_DIR)/bin/mypy $(SRC_DIR)

# Pre-commit
pre-commit:
	@echo "Running pre-commit hooks..."
	@$(VENV_DIR)/bin/pre-commit run --all-files

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@$(VENV_DIR)/bin/pre-commit install

pre-commit-update:
	@echo "Updating pre-commit hooks..."
	@$(VENV_DIR)/bin/pre-commit autoupdate

# Pipelines
check: lint format type test

# Deployment
build:
	@$(PYTHON) -m build

publish-test:
	@echo "Publishing to Test PyPI..."
	@$(VENV_DIR)/bin/twine upload --repository testpypi dist/*

publish:
	@echo "Publishing to PyPI..."
	@$(VENV_DIR)/bin/twine upload dist/*
