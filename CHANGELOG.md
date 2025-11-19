![Banner](./assets/click-extended-changelog-banner.png)

# Changelog

## v1.0.0

### Added

#### Argument

- Added automatic type inference for `Argument` class.
- Added sentinel value `_MISSING` to properly distinguish between no default and `default=None`.

#### ChildNode

- Added new `context` parameter for the `ChildNode.process()` method.
- Added new `ProcessMethod` data class.
- Added `ProcessContext` helper methods: `is_tag()`, `is_option()`, `is_argument()`, `is_env()`, `get_tag_values()`.
- Added type-hint-first system for `ChildNode` with automatic type inference from `process()` method signature.
- Added `get_supported_types()` method to `ChildNode` for inspecting inferred types.
- Added `should_skip_none()` method to `ChildNode` with automatic inference from type hints.
- Added `TypeMismatchError` exception for type validation failures.

#### Option

- Added automatic type inference for `Option` class.
- Made `is_flag` and `type` parameters exclusive for `option` decorator.

#### Testing

- Added unit tests for type inference.
- Added unit tests for required/optional argument behavior.
- Added integration tests for type validation system.

#### Validation

- Added `validation` module.
- Added `validation.is_positive` decorator with unit tests.

### Updated

#### ChildNode

- Updated `process_children()` to validate child node types before processing.
- Updated `process_children()` to automatically skip `None` values based on child node's `should_skip_none()` logic.
- Updated `is_positive` validator to use type hints instead of `types` class attribute.
- Updated `TypeMismatchError` to use decorator name instead of child node name and handle UnionType.

#### Option

- Updated `Option` class to infer type from default value when not explicitly specified.

#### Argument

- Updated `Argument` class to infer type from default value when not explicitly specified.
- Updated `Argument` class to automatically set `required=False` when `default` is provided (including `None`).
- Updated `_root_node.py` to properly pass `required` parameter to Click's `argument()` function.

#### Documentation

- Updated documentation for `Option` with type inference section and examples.
- Updated documentation for `Argument` with type inference section and examples.
- Updated `CHILD_NODE.md` documentation with type-hint-first approach and ProcessContext helpers.
- Updated `ARGUMENT.md` and `OPTION.md` with type inference sections.

#### Tag

- Updated tag processing to iterate through each parent node value individually.

#### Testing

- Updated unit tests for new process context parameter.

### Fixed

#### Argument

- Fixed required/optional argument behavior to match Click's semantics (arguments with defaults are optional).

#### ChildNode

- Fixed issue where a `sentinel` object would be passed as a value to the `process()` method.

#### Typing

- Disabled `unidiomatic-typecheck` rule for pylint.
- Fixed circular import issue in type validation by using class name checks instead of isinstance.
- Fixed Pylance type errors by adding proper type annotations with `cast()`.
- Fixed error formatting to handle Python 3.10+ union types (`int | float`).

#### Validation

- Fixed `is_positive` validator to handle `None` values.

## v0.0.4

### Added

- Added documentation for the `argument` decorator.
- Added documentation for the `option` decorator.
- Added documentation for the `command` decorator.
- Added documentation for the `env` decorator.
- Added documentation for the `group` decorator.
- Added documentation for the `tag` decorator.
- Added documentation for the `RootNode` class.
- Added documentation for the `ParentNode` class.
- Added documentation for the `ChildNode` class.
- Added documentation for the `Tree` class.
- Added documentation for the `GlobalNode` class.
- Added banner specific for documentation.
- Added migration guide.
- Added documentation for contributing.

### Updated

- Help message now only uses the first line of the docstring.
- Updated README.md

## v0.0.3

### Added

- Added a `GlobalNode` class with unit tests.
- Added `debug` module with the `visualize` decorator.
- Created `CHANGELOG.md` document.
- Added banner for `CHANGELOG.md` file.

### Changed

- Updated unit tests for the `Tree` class.
- Added new sections to `README.md` file.
- Renamed `publish.yml` to `release.yml`.
- Improved release action to include relevant changelog section.
- Renamed name of `tests.yml` from `CI` to `Tests`.

## v0.0.2

### Fixed

- Fixed error output for one or more missing environment variables.

## v0.0.1

### Added

- Added `tag` decorator with unit tests.
- Added `option` decorator with unit tests.
- Added `group` decorator with unit tests.
- Added `env` decorator with unit tests.
- Added `command` decorator with unit tests.
- Added `argument` decorator with unit tests.
- Added aliasing classes with unit tests.
- Created `Node` class with unit tests.
- Created `RootNode` class with unit tests.
- Created `ParentNode` class with unit tests.
- Created `ChildNode` class with unit tests.
- Created `Tree` class with unit tests.
- Created `Transform` class for string transformations.
- Set up project structure and added placeholder documentation.
- Created `LICENSE` file.
- Created `Makefile`.
- Created banner images for `README.md`, `AUTHORS.md` and `CONTRIBUTING.md`.
