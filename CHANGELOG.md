![Banner](./assets/click-extended-changelog-banner.png)

# Changelog

## v1.0.0

### Added

- Added new `context` parameter for the `ChildNode.process` method.
- Added new `ProcessMethod` type.
- Added `validation` module.
- Added `validation.is_positive` decorator with unit tests.
- Added type validation system for `ChildNode` with `types` attribute and `validate_type()` method.
- Added `TypeMismatchError` exception for type validation failures.
- Added automatic type inference for `Option` and `Argument` classes.
- Added comprehensive unit tests for type inference.
- Added integration tests for type validation system.

### Updated

- Updated unit tests for new process context parameter.
- Updated `Option` class to infer type from default value when not explicitly specified.
- Updated `Argument` class to infer type from default value when not explicitly specified.
- Updated `process_children()` to validate child node types before processing.
- Updated documentation for `Option` with type inference section and examples.
- Updated documentation for `Argument` with type inference section and examples.

### Fixed

- Fixed circular import issue in type validation by using class name checks instead of isinstance.
- Fixed Pylance type errors by adding proper type annotations with `cast()`.

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
