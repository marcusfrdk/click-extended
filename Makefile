.PHONY: help version venv reset clean install test test-short coverage lint lint-check format format-check type build publish-test publish

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
	@echo "    make reset               Reset the project to the original state"
	@echo "    make clean               Clean the project and remove caches and other artifacts"
	@echo "    make install             Install the package dependencies"
	@echo ""
	@echo "  Testing:"
	@echo "    make test                Run tests with verbose output"
	@echo "    make test-short          Run tests with concise output"
	@echo "    make coverage            Run tests with coverage report and open in browser"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make lint                Run pylint on source code"
	@echo "    make lint-check          Check code with pylint (same as lint)"
	@echo "    make format              Format code with black and sort imports with isort"
	@echo "    make format-check        Check formatting and import sorting without changes"
	@echo "    make type                Run type checking with mypy"
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
		echo "Activate the virtual environment with 'source $(VENV_DIR)/bin/activate'"; \
	fi

reset:
	rm -rf $(VENV_DIR) venv
	rm -rf *.egg-info
	rm -rf dist build
	rm -rf htmlcov .coverage
	rm -rf .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "To exit the deleted virtual environment, run 'deactivate'"; \
	fi

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -r .pytest_cache .mypy_cache

install:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "You are not in a virtual environment."; \
	else \
		$(PIP) install -e ".[dev,build]"; \
	fi

# Testing
test:
	@$(VENV_DIR)/bin/pytest -v

test-short:
	@$(VENV_DIR)/bin/pytest

coverage:
	@$(VENV_DIR)/bin/pytest --cov=$(SRC_DIR) --cov-report=term-missing

# Linting
lint:
	@$(VENV_DIR)/bin/pylint $(SRC_DIR)

lint-check:
	@$(VENV_DIR)/bin/pylint $(SRC_DIR)

# Formatting
format:
	@$(VENV_DIR)/bin/isort $(SRC_DIR)
	@$(VENV_DIR)/bin/black $(SRC_DIR)

format-check:
	@$(VENV_DIR)/bin/isort --check-only $(SRC_DIR)
	@$(VENV_DIR)/bin/black --check $(SRC_DIR)

# Type checking
type:
	@$(VENV_DIR)/bin/mypy $(SRC_DIR)

# Deployment
build:
	@$(PYTHON) -m build

publish-test:
	@$(VENV_DIR)/bin/twine upload --repository testpypi dist/*

publish:
	@$(VENV_DIR)/bin/twine upload dist/*
