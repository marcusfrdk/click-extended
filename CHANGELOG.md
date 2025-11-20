![Banner](./assets/click-extended-changelog-banner.png)

# Changelog

## v1.0.0

### Added

- **@argument**: Added automatic type inference for `Argument` class.
- **@argument**: Added sentinel value `_MISSING` to properly distinguish between no default and `default=None`.
- **ChildNode**: Added new `context` parameter for the `ChildNode.process()` method.
- **ChildNode**: Added new `ProcessMethod` data class.
- **ChildNode**: Added `ProcessContext` helper methods: `is_tag()`, `is_option()`, `is_argument()`, `is_env()`, `get_tag_values()`.
- **ChildNode**: Added type-hint-first system for `ChildNode` with automatic type inference from `process()` method signature.
- **ChildNode**: Added `get_supported_types()` method to `ChildNode` for inspecting inferred types.
- **ChildNode**: Added `should_skip_none()` method to `ChildNode` with automatic inference from type hints.
- **ChildNode**: Added `TypeMismatchError` exception for type validation failures.
- **@option**: Added automatic type inference for `Option` class.
- **@option**: Made `is_flag` and `type` parameters exclusive for `option` decorator.
- **Testing**: Added unit tests for type inference.
- **Testing**: Added unit tests for required/optional argument behavior.
- **Testing**: Added integration tests for type validation system.
- **Validation**: Added `validation` module with `@is_positive` validator decorator.
- **Transform**: Added `transform` module with `@as_path` transformer decorator for comprehensive path validation (14 parameters: existence, parents, file/directory type, empty checks, extensions, include/exclude patterns, permissions).
- **Error handling**: Added exception hierarchy (`CatchableError`, `ValidationError`, `TransformError`, `ParameterError`) with Click-style error formatting that displays parameter context, usage information, and help hints.
- **Click Context**: Updated framework to pass Click context through wrappers to `process_children()` for enhanced error reporting.

### Updated

- **ChildNode**: Updated `process_children()` to validate child node types before processing.
- **ChildNode**: Updated `process_children()` to automatically skip `None` values based on child node's `should_skip_none()` logic.
- **ChildNode**: Updated `is_positive` validator to use type hints instead of `types` class attribute.
- **ChildNode**: Updated `TypeMismatchError` to use decorator name instead of child node name and handle UnionType.
- **@option**: Updated `Option` class to infer type from default value when not explicitly specified.
- **@argument**: Updated `Argument` class to infer type from default value when not explicitly specified.
- **@argument**: Updated `Argument` class to automatically set `required=False` when `default` is provided (including `None`).
- **@argument**: Updated `_root_node.py` to properly pass `required` parameter to Click's `argument()` function.
- **Docs**: Updated documentation for `Option` with type inference section and examples.
- **Docs**: Updated documentation for `Argument` with type inference section and examples.
- **Docs**: Updated `CHILD_NODE.md` documentation with type-hint-first approach and ProcessContext helpers.
- **Docs**: Updated `CHILD_NODE.md` with comprehensive "Error Handling" section explaining `ValidationError`, `TransformError`.
- **Docs**: Updated all code examples in `CHILD_NODE.md`, `README.md`, `TREE.md`, and `GLOBAL_NODE.md` to use `ValidationError` instead of `ValueError`.
- **Docs**: Updated `ARGUMENT.md` and `OPTION.md` with type inference sections.
- **Docs**: Updated structure of `CHANGELOG.md`.
- **@tag**: Updated tag processing to iterate through each parent node value individually.
- **Testing**: Updated unit tests for new process context parameter.
- **Testing**: Updated all validator and transformer tests to use `ValidationError` and `TransformError`.
- **pyproject.toml**: Disabled the pyright error `reportUnnecessaryIsInstance` (Disabled the warning for unnecessary isinstance checks).

### Fixed

- **@argument**: Fixed required/optional argument behavior to match Click's semantics (arguments with defaults are optional).
- **ChildNode**: Fixed issue where a `sentinel` object would be passed as a value to the `process()` method.
- **RootNode**: Fixed issue where the type-hinting system would not raise exception when types mismatch.
- **Typing**: Disabled `unidiomatic-typecheck` rule for pylint.
- **Typing**: Fixed circular import issue in type validation by using class name checks instead of isinstance.
- **Typing**: Fixed Pylance type errors by adding proper type annotations with `cast()`.
- **Typing**: Fixed error formatting to handle Python 3.10+ union types (`int | float`).
- **Validation**: Fixed `is_positive` validator to handle `None` values.
- **Error handling**: Fixed error handling so custom handler overrides Click's default.

## v0.0.4

### Added

- **Docs**: Added documentation for the `argument` decorator.
- **Docs**: Added documentation for the `option` decorator.
- **Docs**: Added documentation for the `command` decorator.
- **Docs**: Added documentation for the `env` decorator.
- **Docs**: Added documentation for the `group` decorator.
- **Docs**: Added documentation for the `tag` decorator.
- **Docs**: Added documentation for the `RootNode` class.
- **Docs**: Added documentation for the `ParentNode` class.
- **Docs**: Added documentation for the `ChildNode` class.
- **Docs**: Added documentation for the `Tree` class.
- **Docs**: Added documentation for the `GlobalNode` class.
- **Docs**: Added banner specific for documentation.
- **Docs**: Added migration guide.
- **Docs**: Added documentation for contributing.

### Updated

- **Decorators**: Help message now only uses the first line of the docstring.
- **Docs**: Updated README.md

## v0.0.3

### Added

- **GlobalNode**: Added a `GlobalNode` class with unit tests.
- **Module**: Added `debug` module with the `visualize` decorator.
- **Docs**: Created `CHANGELOG.md` document.
- **Docs**: Added banner for `CHANGELOG.md` file.

### Changed

- **Tree**: Updated unit tests for the `Tree` class.
- **Docs**: Added new sections to `README.md` file.
- **CI/CD**: Renamed `publish.yml` to `release.yml`.
- **CI/CD**: Improved release action to include relevant changelog section.
- **CI/CD**: Renamed name of `tests.yml` from `CI` to `Tests`.

## v0.0.2

### Fixed

- **@env**: Fixed error output for one or more missing environment variables.

## v0.0.1

### Added

- **@tag**: Added `tag` decorator with unit tests.
- **@option**: Added `option` decorator with unit tests.
- **@group**: Added `group` decorator with unit tests.
- **@env**: Added `env` decorator with unit tests.
- **@command**: Added `command` decorator with unit tests.
- **@argument**: Added `argument` decorator with unit tests.
- **Aliasing**: Added aliasing classes with unit tests.
- **Node**: Created `Node` class with unit tests.
- **RootNode**: Created `RootNode` class with unit tests.
- **ParentNode**: Created `ParentNode` class with unit tests.
- **ChildNode**: Created `ChildNode` class with unit tests.
- **Tree**: Created `Tree` class with unit tests.
- **Transform**: Created `Transform` class for string transformations.
- **Project**: Set up project structure and added placeholder documentation.
- **Docs**: Created `LICENSE` file.
- **Scripts**: Created `Makefile`.
- **Docs**: Created banner images for `README.md`, `AUTHORS.md` and `CONTRIBUTING.md`.
