![Banner](./assets/click-extended-contributing-banner.png)

# Contributing

Thank you for considering contributing to `click-extended`. We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code changes.

## Vision

> Build command line interfaces your way.

This library enhances Click with modern conveniences and a modular architecture. Get automatic async support, aliasing, and environment variable integration and much more straight out of the box. Through a node-based system, you can customize every aspect of your CLI, from validation and transformation to injection, without modifying the core framework. If you need a feature, you can build it. It should feel like the library works with you instead of against you.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

Be respectful, constructive, and professional in all interactions. We aim to create a welcoming environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of Click and CLI development

### Ways to Contribute

1. **Report Bugs**: Open an issue describing the bug with steps to reproduce
2. **Suggest Features**: Open an issue describing the feature and its use case
3. **Fix Issues**: Look for issues labeled "good first issue" or "help wanted"
4. **Improve Documentation**: Fix typos, clarify explanations, or add examples
5. **Add Tests**: Improve test coverage or add missing test cases

## Development Setup

### 1. Fork and Clone

Start by forking the repository on Github, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/click-extended.git
cd click-extended
```

### 2. Create Virtual Environment

```bash
make venv
source .venv/bin/activate
```

This will:

- Create a `.venv` virtual environment
- Install the package in editable mode
- Install all development dependencies (pytest, black, pylint, mypy, etc.)
- Install pre-commit hooks

### 3. Install Pre-Commit Hooks (Recommended)

```bash
pre-commit install
```

This will automatically run the following checks before each commit:

- Code formatting (black, isort)
- Linting (pylint)
- Type checking (mypy)
- Tests (pytest with coverage)
- File checks (trailing whitespace, YAML/TOML validation, etc.)

If any check fails, the commit will be blocked until you fix the issues. This ensures code quality and saves time in the review process.

### 4. Verify Setup

```bash
# Run tests to ensure everything works
make test

# Check code quality tools
make lint
make type
make format-check
```

## Development Workflow

### 1. Create a Branch

Create a descriptive branch name.

```bash
git checkout -b feature/add-new-validator
git checkout -b fix/option-parsing-bug
git checkout -b docs/improve-examples
```

### 2. Make Changes

Follow these guidelines:

- **Code Style**: Use Black formatting (80 char line length)
- **Type Hints**: All functions must have type hints
- **Docstrings**: Use the project's docstring format (a custom version of the Google-style docstrings):

  ```python
  def example(value: int) -> str:
      """
      Short description.

      Args:
        value (int):
            Description of value.
        optional (str, optional):
            This value is optional, or in other words, a
            default value is set.

      Returns:
          str:
              Description of return value.
      """
      return str(value)
  ```

- **Tests**: Add tests for new features or bug fixes
- **Documentation**: Update relevant docs in `docs/` directory

### 3. Run Quality Checks

Pre-commit hooks will automatically run these checks before each commit, but you can also run them manually:

```bash
# Run all pre-commit hooks manually
pre-commit run --all-files

# Or run individual checks:

# Format code
make format

# Run linter
make lint

# Run type checker
make type

# Run tests
make test

# Run tests with coverage
make coverage
```

### 4. Commit Changes

After staging your files, ensure your commit messages follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) format.

```bash
git commit -m "feat: Added new email validator"
git commit -m "fix: Handle empty string in argument parsing"
git commit -m "docs: Added examples for custom transformers"
```

If pre-commit hooks fail:

1. Review the error messages.
2. Fix the reported issues.
3. Stage the fixes.
4. Retry the commit.

You can also skip pre-commit hooks (highly discouraged) with:

```bash
git commit --no-verify -m "message"
```

**Commit Message Format:**

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes (formatting, etc.)
- `chore:` Maintenance tasks

## Testing

### Running Tests

```bash
# Run all tests with verbose output
make test

# Run tests with concise output
make test-short

# Run tests with coverage report
make coverage
```

### Writing Tests

Tests are located in the `tests/` directory. Follow these patterns:

```python
import pytest
from click_extended import command, option

def test_option_validation():
    """Test that option validation works correctly."""
    @command()
    @option("--count", type=int, required=True)
    def cli(count: int):
        print(count)

    # Test implementation
    runner = CliRunner()
    result = runner.invoke(cli, ["--count", "5"])
    assert result.exit_code == 0
```

**Testing Guidelines:**

- Write tests for all new features.
- Include edge cases and error conditions.
- Use descriptive test names.
- Keep tests focused on a single behavior.
- Aim for high code coverage (>90%).
- Avoid creating to many files if possible (try to include tests within the same category in the same file).

## Code Quality

All code quality checks are automatically enforced by pre-commit hooks. However, you can run them manually:

### Pre-Commit Hooks

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pylint --all-files
pre-commit run mypy --all-files
pre-commit run pytest --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

The pre-commit configuration (`.pre-commit-config.yaml`) includes:

- **Formatting**: black, isort
- **Linting**: pylint (score must be >= 10.0)
- **Type Checking**: mypy (strict mode)
- **Tests**: pytest (coverage must be >= 80%)
- **File Checks**: trailing whitespace, YAML/TOML validation, merge conflicts, etc.

### Linting

```bash
# Check code with pylint
make lint
```

Fix any issues reported. The project uses pylint with a max line length of 80 characters.

### Type Checking

```bash
# Run mypy type checker
make type
```

All code must pass strict type checking. Add type hints to all functions and classes.

### Formatting

```bash
# Format code with black and isort
make format

# Check formatting without changes
make format-check
```

Use `black` for code formatting and `isort` for import sorting.

## Documentation

### Documentation Structure

Documentation files are found in the `docs/` directory and follow the conventional screaming snake case file naming of markdown documents.

### Adding Documentation

When adding features:

1. Update relevant documentation in `docs/`.
2. Add the documentation banner to the document with the title underneath.
3. Add examples showing usage.
4. Update README.md if adding major features.
5. Use consistent formatting and style.

### Documentation Style

- Use clear, concise language.
- Include runnable code examples.
- Show both simple and advanced usage.
- Explain why, not just how.
- Add type hints to all examples.

## Submitting Changes

### 1. Push Your Branch

```bash
git push origin prefix/your-branch-name
```

### 2. Create Pull Request

1. Go to the repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:
   - **Title**: Clear, descriptive title
   - **Description**: What changed and why
   - **Related Issues**: Link any related issues
   - **Testing**: How you tested the changes
   - **Checklist**: Complete all items

### 3. PR Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] Pre-commit hooks pass (or all manual checks pass)
- [ ] All tests pass (`make test`)
- [ ] Code is properly formatted (`make format`)
- [ ] Linter passes (`make lint`)
- [ ] Type checker passes (`make type`)
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### 4. Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged

## Release Process

The release process is automatically done through Github Actions and is triggered when a new tag in the format `v*.*.*` is pushed.

### 1. Update Version

Update version in `pyproject.toml`:

```toml
version = "X.Y.Z"
```

### 2. Update Changelog

Add changes to the [CHANGELOG.md](./CHANGELOG.md) file following the existing format.

### 3. Tag Release

```bash
git tag -s vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```

## Useful Make Commands

```bash
make help           # Show all available commands
make version        # Show current package version
make venv           # Create virtual environment and install dependencies
make reset          # Reset project to clean state
make clean          # Remove caches and artifacts
make test           # Run tests with verbose output
make test-short     # Run tests with concise output
make coverage       # Run tests with coverage report
make lint           # Run pylint
make format         # Format code with black and isort
make format-check   # Check formatting without changes
make type           # Run type checking with mypy
make build          # Build distribution packages
```

## Pre-Commit Hooks

Pre-commit hooks are highly recommended for development:

```bash
# Install hooks (one-time setup)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

Hooks automatically run on commit and check:

- Code formatting and import sorting
- Linting (pylint score >= 10.0)
- Type checking (mypy strict mode)
- Tests (pytest with >= 80% coverage)
- File issues (whitespace, YAML/TOML syntax, merge conflicts, etc.)

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with reproduction steps
- **Features**: Open an issue describing the feature
- **Chat**: Comment on existing issues or PRs

## Recognition

When making changes, don't forget to add your name in the [authors file](./AUTHORS.md) if it's not already there. Thank you for your contributions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
