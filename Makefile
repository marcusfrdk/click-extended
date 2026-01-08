.PHONY: help version venv reset clean install test test-short coverage lint format type build publish-test publish test-all coverage-all lint-all format-all type-all

.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PYTHON_VERSIONS := 310 311 312 313 314
VENV_DIR := $(shell if [ -n "$$VIRTUAL_ENV" ]; then echo "$$VIRTUAL_ENV"; else echo ".venv"; fi)
VENV_BASE := $(basename $(VENV_DIR))
SRC_DIR := click_extended
TESTS_DIR := tests
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
	@echo "    make install-all         Install the package dependencies for all versions"
	@echo ""
	@echo "  Testing:"
	@echo "    make test                Run tests with verbose output (active venv)"
	@echo "    make test-short          Run tests with concise output (active venv)"
	@echo "    make coverage            Run tests with coverage report (active venv)"
	@echo "    make test-all            Run tests on all Python versions"
	@echo "    make coverage-all        Run coverage on all Python versions"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make lint                Run pylint on source code (active venv)"
	@echo "    make lint-all            Run pylint on all Python versions"
	@echo "    make format              Format code with black and sort imports with isort (active venv)"
	@echo "    make format-all          Format code on all Python versions"
	@echo "    make type                Run type checking with mypy (active venv)"
	@echo "    make type-all            Run type checking on all Python versions"
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

install-all:
	for version in $(PYTHON_VERSIONS); do \
		"$(VENV_BASE).$$version/bin/pip" install -e ".[dev,build]"; \
	done

# Testing
test:
	@$(VENV_DIR)/bin/pytest -v

test-short:
	@$(VENV_DIR)/bin/pytest

coverage:
	@$(VENV_DIR)/bin/pytest --cov=$(SRC_DIR) --cov-report=term-missing

test-all:
	@failed=""; \
	for version in $(PYTHON_VERSIONS); do \
		if [ -d "$(VENV_BASE).$$version" ]; then \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Running tests..."; \
			if ! $(VENV_BASE).$$version/bin/pytest -q; then \
				failed="$$failed $$ver_display"; \
			fi; \
		else \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Skipped (venv not found)"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then \
		echo "Tests failed for Python:$$failed"; \
		exit 1; \
	else \
		echo "All tests passed"; \
	fi

coverage-all:
	@failed=""; \
	for version in $(PYTHON_VERSIONS); do \
		if [ -d "$(VENV_BASE).$$version" ]; then \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Running coverage..."; \
			if ! $(VENV_BASE).$$version/bin/pytest --cov=$(SRC_DIR) --cov-report=term --cov-report=html -q; then \
				failed="$$failed $$ver_display"; \
			fi; \
		else \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Skipped (venv not found)"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then \
		echo "Coverage failed for Python:$$failed"; \
		exit 1; \
	else \
		echo "All coverage complete"; \
	fi

# Linting
lint:
	@$(VENV_DIR)/bin/pylint $(SRC_DIR)

lint-all:
	@failed=""; \
	for version in $(PYTHON_VERSIONS); do \
		if [ -d "$(VENV_BASE).$$version" ]; then \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Linting..."; \
			if ! $(VENV_BASE).$$version/bin/pylint $(SRC_DIR) -q; then \
				failed="$$failed $$ver_display"; \
			fi; \
		else \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Skipped (venv not found)"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then \
		echo "Linting failed for Python:$$failed"; \
		exit 1; \
	else \
		echo "All linting passed"; \
	fi

# Formatting
format:
	@$(VENV_DIR)/bin/isort $(SRC_DIR)
	@$(VENV_DIR)/bin/black $(SRC_DIR)

format-all:
	@failed=""; \
	for version in $(PYTHON_VERSIONS); do \
		if [ -d "$(VENV_BASE).$$version" ]; then \
			echo "[Python 3.$$version] Formatting..."; \
			if ! $(VENV_BASE).$$version/bin/isort $(SRC_DIR) -q; then \
				failed="$$failed 3.$$version"; \
			fi; \
			if ! $(VENV_BASE).$$version/bin/black $(SRC_DIR) -q; then \
				failed="$$failed 3.$$version"; \
			fi; \
		else \
			echo "[Python 3.$$version] Skipped (venv not found)"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then \
		echo "Formatting failed for Python:$$failed"; \
		exit 1; \
	else \
		echo "All formatting complete"; \
	fi

# Type checking
type:
	@$(VENV_DIR)/bin/mypy $(SRC_DIR) $(TESTS_DIR)

type-all:
	@failed=""; \
	for version in $(PYTHON_VERSIONS); do \
		if [ -d "$(VENV_BASE).$$version" ]; then \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Type checking..."; \
			if ! $(VENV_BASE).$$version/bin/mypy $(SRC_DIR) $(TESTS_DIR) --no-error-summary; then \
				failed="$$failed $$ver_display"; \
			fi; \
		else \
			ver_display=$$(echo $$version | sed 's/^\([0-9]\)\([0-9]\+\)$$/\1.\2/'); \
			echo "[Python $$ver_display] Skipped (venv not found)"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then \
		echo "Type checking failed for Python:$$failed"; \
		exit 1; \
	else \
		echo "All type checking passed"; \
	fi

# Deployment
build:
	@$(PYTHON) -m build

publish-test:
	@$(VENV_DIR)/bin/twine upload --repository testpypi dist/*

publish:
	@$(VENV_DIR)/bin/twine upload dist/*
