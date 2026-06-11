set dotenv-load := false

default:
    @just --list

python := "python3"
python_versions := "310 311 312 313 314"
venv_dir := ".venv"
src_dir := "click_extended"
tests_dir := "tests"
pip := venv_dir + "/bin/pip"

# Show available commands
help:
    @just --list

# Show current package version
version:
    @grep '^version =' pyproject.toml | cut -d'"' -f2 | sed 's/^/Package version: /'

# Create virtual environment and install dependencies
venv:
    @if [ -d "{{ venv_dir }}" ]; then \
        echo "Virtual environment already exists at {{ venv_dir }}"; \
    else \
        echo "Checking Python version..."; \
        {{ python }} --version | grep -qE "Python 3\.(1[0-9]|[2-9][0-9])" || \
            (echo "Error: Python 3.10 or higher is required" && exit 1); \
        echo "Creating virtual environment..."; \
        {{ python }} -m venv "{{ venv_dir }}"; \
        echo "Installing dependencies..."; \
        "{{ pip }}" install --upgrade pip; \
        "{{ pip }}" install -e ".[dev,build]"; \
        echo "Activate the virtual environment with 'source {{ venv_dir }}/bin/activate'"; \
    fi

# Reset the project to the original state
reset:
    rm -rf .venv venv
    @for version in {{ python_versions }}; do \
        rm -rf ".$version"; \
    done
    rm -rf *.egg-info
    rm -rf dist build
    rm -rf htmlcov .coverage
    rm -rf .pytest_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    @if [ -z "$VIRTUAL_ENV" ]; then \
        echo "To exit the deleted virtual environment, run 'deactivate'"; \
    fi

# Clean caches and generated artifacts
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -r .pytest_cache

# Create virtual environment with the current Python and install dependencies
install:
    @if [ -d "{{ venv_dir }}" ]; then \
        echo "Virtual environment already exists at {{ venv_dir }}"; \
    else \
        echo "Checking Python version..."; \
        {{ python }} --version | grep -qE "Python 3\.(1[0-9]|[2-9][0-9])" || \
            (echo "Error: Python 3.10 or higher is required" && exit 1); \
        echo "Creating virtual environment with current Python at {{ venv_dir }}..."; \
        {{ python }} -m venv "{{ venv_dir }}"; \
    fi; \
    echo "Installing dependencies..."; \
    "{{ venv_dir }}/bin/python" -m pip install --upgrade pip; \
    "{{ venv_dir }}/bin/python" -m pip install -e ".[dev,build]"; \
    echo "Activate the virtual environment with 'source {{ venv_dir }}/bin/activate'"

# Install latest pyenv patch versions and create per-version virtual environments
install-all:
    @command -v pyenv >/dev/null 2>&1 || (echo "Error: pyenv is required for install-all" && exit 1); \
    if [ -d "{{ venv_dir }}" ]; then \
        echo "Virtual environment already exists at {{ venv_dir }}"; \
    else \
        echo "Checking Python version..."; \
        {{ python }} --version | grep -qE "Python 3\.(1[0-9]|[2-9][0-9])" || \
            (echo "Error: Python 3.10 or higher is required" && exit 1); \
        echo "Creating virtual environment with current Python at {{ venv_dir }}..."; \
        {{ python }} -m venv "{{ venv_dir }}"; \
    fi; \
    echo "Installing dependencies into {{ venv_dir }}..."; \
    "{{ venv_dir }}/bin/python" -m pip install --upgrade pip; \
    "{{ venv_dir }}/bin/python" -m pip install -e ".[dev,build]"; \
    for version in {{ python_versions }}; do \
        major=$(printf '%s' "$version" | cut -c1); \
        minor=$(printf '%s' "$version" | cut -c2-); \
        prefix="$major.$minor"; \
        latest=$(pyenv latest --known "$prefix"); \
        venv_dir=".$version"; \
        echo "[Python $latest] Installing interpreter if needed..."; \
        pyenv install --skip-existing "$latest"; \
        pyenv rehash; \
        if [ -d "$venv_dir" ]; then \
            echo "[Python $latest] Virtual environment already exists at $venv_dir"; \
        else \
            echo "[Python $latest] Creating virtual environment at $venv_dir"; \
            PYENV_VERSION="$latest" pyenv exec python -m venv "$venv_dir"; \
        fi; \
        echo "[Python $latest] Installing dependencies..."; \
        "$venv_dir/bin/python" -m pip install --upgrade pip; \
        "$venv_dir/bin/python" -m pip install -e ".[dev,build]"; \
    done

# Run tests with verbose output
test:
    @"{{ venv_dir }}/bin/pytest" -v

# Run tests with concise output
test-short:
    @"{{ venv_dir }}/bin/pytest"

# Run tests with coverage report
coverage:
    @"{{ venv_dir }}/bin/pytest" --cov={{ src_dir }} --cov-report=term-missing

# Run tests on all Python versions
test-all:
    @failed=""; \
    for version in {{ python_versions }}; do \
        if [ -d ".${version}" ]; then \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Running tests..."; \
            if ! ".${version}/bin/pytest" -q; then \
                failed="$failed $ver_display"; \
            fi; \
        else \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Skipped (venv not found)"; \
        fi; \
    done; \
    if [ -n "$failed" ]; then \
        echo "Tests failed for Python:$failed"; \
        exit 1; \
    else \
        echo "All tests passed"; \
    fi

# Run coverage on all Python versions
coverage-all:
    @failed=""; \
    for version in {{ python_versions }}; do \
        if [ -d ".${version}" ]; then \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Running coverage..."; \
            if ! ".${version}/bin/pytest" --cov={{ src_dir }} --cov-report=term --cov-report=html -q; then \
                failed="$failed $ver_display"; \
            fi; \
        else \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Skipped (venv not found)"; \
        fi; \
    done; \
    if [ -n "$failed" ]; then \
        echo "Coverage failed for Python:$failed"; \
        exit 1; \
    else \
        echo "All coverage complete"; \
    fi

# Run pylint on source code
lint:
    @"{{ venv_dir }}/bin/pylint" {{ src_dir }}

# Run pylint on all Python versions
lint-all:
    @failed=""; \
    for version in {{ python_versions }}; do \
        if [ -d ".${version}" ]; then \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Linting..."; \
            if ! ".${version}/bin/pylint" {{ src_dir }} -q; then \
                failed="$failed $ver_display"; \
            fi; \
        else \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Skipped (venv not found)"; \
        fi; \
    done; \
    if [ -n "$failed" ]; then \
        echo "Linting failed for Python:$failed"; \
        exit 1; \
    else \
        echo "All linting passed"; \
    fi

# Format code with black and sort imports with isort
format:
    @"{{ venv_dir }}/bin/isort" {{ src_dir }}
    @"{{ venv_dir }}/bin/black" {{ src_dir }}

# Check formatting without changing files
format-check:
    @"{{ venv_dir }}/bin/isort" --check-only {{ src_dir }}
    @"{{ venv_dir }}/bin/black" --check {{ src_dir }}

# Format code on all Python versions
format-all:
    @failed=""; \
    for version in {{ python_versions }}; do \
        if [ -d ".${version}" ]; then \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Formatting..."; \
            if ! ".${version}/bin/isort" {{ src_dir }} -q; then \
                failed="$failed $ver_display"; \
            fi; \
            if ! ".${version}/bin/black" {{ src_dir }} -q; then \
                failed="$failed $ver_display"; \
            fi; \
        else \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Skipped (venv not found)"; \
        fi; \
    done; \
    if [ -n "$failed" ]; then \
        echo "Formatting failed for Python:$failed"; \
        exit 1; \
    else \
        echo "All formatting complete"; \
    fi

# Run type checking with basedpyright
type:
    @"{{ venv_dir }}/bin/basedpyright" --pythonpath "{{ venv_dir }}/bin/python" {{ src_dir }} {{ tests_dir }}

# Run type checking on all Python versions
type-all:
    @failed=""; \
    for version in {{ python_versions }}; do \
        if [ -d ".${version}" ]; then \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Type checking..."; \
            if ! ".${version}/bin/basedpyright" --pythonpath ".${version}/bin/python" {{ src_dir }} {{ tests_dir }}; then \
                failed="$failed $ver_display"; \
            fi; \
        else \
            ver_display=$(printf '%s' "$version" | sed 's/^\(.\)\(.*\)$/\1.\2/'); \
            echo "[Python $ver_display] Skipped (venv not found)"; \
        fi; \
    done; \
    if [ -n "$failed" ]; then \
        echo "Type checking failed for Python:$failed"; \
        exit 1; \
    else \
        echo "All type checking passed"; \
    fi

# Build distribution packages
build:
    @{{ python }} -m build

# Publish to Test PyPI
publish-test:
    @"{{ venv_dir }}/bin/twine" upload --repository testpypi dist/*

# Publish to PyPI
publish:
    @"{{ venv_dir }}/bin/twine" upload dist/*
