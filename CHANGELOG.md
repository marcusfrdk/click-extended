![Banner](./assets/click-extended-changelog-banner.png)

# Changelog

## v1.0.0

### Added

- **Check Utilities**: Added `is_argument`, `is_option`, and `is_tag` utility functions with type guards.
- **Code Snippets**: Python code snippets.
- **Dependencies**: Added `PyYAML` and `tomli` (only before 3.11) as a project dependency.
- **Dev Dependencies**: Added `types-PyYAML` as a project dev dependency.
- **`@to_time`**: Child decorator to convert a string from various formats to a `time` object.
- **`@to_datetime`**: Child decorator to convert a string from various formats to a `datetime` object.
- **`@load_csv`**: Child decorator to load a CSV file from a `pathlib.Path` object.
- **`@load_toml`**: Child decorator to load a TOML file from a `pathlib.Path` object.
- **`@load_yaml`**: Child decorator to load a YAML file from a `pathlib.Path` object.
- **`@load_json`**: Child decorator to load a JSON file from a `pathlib.Path` object.
- **`@to_path`**: Child decorator to validate and convert a string to a `pathlib.Path` object.
- **`@default`**: Child decorator to default to a value if not provided.
- **`@experimental`**: Child decorator to warn the user a parent is experimental.
- **`@deprecated`**: Child decorator to warn the user a parent is deprecated.
- **`@apply`**: Child decorator to apply an arbitrary function to a value.
- **`@at_most`**: Child decorator to check if at most `n` arguments are provided.
- **`@at_least`**: Child decorator to check if at least `n` arguments are provided.
- **`ValidationNode`**: Added new node type for validation only in the global context with lifecycle methods.
- **`@exclusive`**: Added decorator to check for exclusivity between parents and tags.
- **`@selection`**: Added a new parent node decorator for selecting one or more values from a carousel.
- **`@prompt`**: Added a parent node decorator to prompt the user for a value.
- **`@to_lower_case`**: A child decorator that converts a string to `lower case`.
- **`@to_upper_case`**: A child decorator that converts a string to `UPPER CASE`.
- **`@to_meme_case`**: A child decorator that converts a string to `mEmE cASe`.
- **`@to_snake_case`**: A child decorator that converts a string to `snake_case`.
- **`@to_screaming_snake_case`**: A child decorator that converts a string to `SCREAMING_SNAKE_CASE`.
- **`@to_camel_case`**: A child decorator that converts a string to `camelCase`.
- **`@to_pascal_case`**: A child decorator that converts a string to `PascalCase`.
- **`@to_kebab_case`**: A child decorator that converts a string to `kebab-case`.
- **`@to_train_case`**: A child decorator that converts a string to `Train-Case`.
- **`@to_flat_case`**: A child decorator that converts a string to `flatcase`.
- **`@to_dot_case`**: A child decorator that converts a string to `dot.case`.
- **`@to_title_case`**: A child decorator that converts a string to `Title Case`.
- **`@to_path_case`**: A child decorator that converts a string to `path/case`.
- **`@random_prime`**: Added parent node decorator for generating a random prime number with unit tests.
- **`@random_uuid`**: Added parent node decorator for generating random `UUID` objects with unit tests.
- **`@random_choice`**: Added parent node decorator for selecting a random choice from a sequence with unit tests.
- **`@random_datetime`**: Added parent node decorator for generating random `datetime` objects with unit tests.
- **`@random_string`**: Added parent node decorator for generating random strings with unit tests.
- **`@random_integer`**: Added parent node decorator for generating a random integer with unit tests.
- **`@random_float`**: Added parent node decorator for generating a random floating point value with unit tests.
- **`@random_bool`**: Added parent node decorator for generating a random boolean with unit tests.

### Updated

- **Granular Handlers**: Replaced `handle_primitive` with more granular `handle_string`, `handle_int`, and more.

### Fixed

- **Name and Tag Naming Conflict**: Added validation so nodes cannot have a tag of the same name as the node itself.
- **Typing Issue**: Fixed typing issues for `Group.command()` and `Group.group()` methods.
- **Existing Parents**: Fixed issue where duplicate parents were allowed.
- **Error output**: Improved user-friendliness of exceptions raised outside context

## v0.4.0

### Added

- **New Decorator API**: A new and simplified decorator API.
- **ArgumentNode**: A parent node that receives its value from a positional command line argument.
- **OptionNode**: A parent node that receives its value from a keyword command line argument.
- **Context**: A universal context that is initialized and used within a tree and accessible from anywhere.
- **Test Coverage**: Added test coverage as a part of the pipeline and achieved 92% test coverage.
- **Humanize**: Added humanize utility module for better displaying iterables and types in a human readable format.
- **Documentation**: A new and improved documentation.
- **Phase System**: The framework applies initialization in phases with a clearer separation than before.

### Updated

- **ParentNode**: The parent node is now a base class for `ArgumentNode`, `OptionNode`, and custom implementations while replacing the functionality of the old `GlobalNode`.
- **Improved Errors**: Rehauled the error system to be more pythonic, display better errors, and a debug mode.
- **Easier Custom Classes**: Implementing custom `ParentNode` and `ChildNode` classes is now much easier because of a simpler API.

### Removed

- **ProcessContext**: Removed the context specific to handlers and made it more universal as the `Context`.
- **GlobalNode**: Removed the `GlobalNode` as it's replaced with the `ParentNode`.

### Fixed

- **Better Tag Support**: Tags are now deeply integrated into the framework.
- **Better Async Support**: All handlers and parent node methods support both an asynchronous or a synchronous execution model.

## v0.3.2

### Added

- **docs/TRANSFORMERS.md**: Added documentation for available transformation nodes.

### Updated

- **types.py**: `ProcessContext` is now exported from the `click_extended.types` module instead of the `click_extended` module.
- **docs/ARGUMENT.md**: Rewrote documentation for the `@argument` decorator.
- **docs/CHILD_NODE.md**: Rewrote documentation for the `ChildNode` class.
- **docs/COMMAND.md**: Rewrote documentation for the `@command` decorator.

### Removed

- **types.py**: Removed unused import.
- **core/\_aliased.py**: Removed unused import.

### Fixed

- **core/\_aliased.py**: Fixed type issues.
- **core/\_child_node.py**: Fixed type issues.

## v0.3.1

### Added

- **transform/to_case.py**: Added new factory class that creates to\_\*\_case decorators.
- **New transform decorators**: Added `@to_camel_case`, `@to_dot_case`, `@to_flat_case`, `@to_kebab_case`, `@to_lower_case`, `@to_meme_case`, `@to_pascal_case`, `@to_path_case`, `@to_screaming_snake_case`, `@to_snake_case`, `@to_title_case`, `@to_train_case`, `@to_upper_case` decorators.

### Updated

- **utils/transform.py**: Added `to_upper_case`, `to_lower_case` and `to_meme_case` methods to the `Transform` class.

### Removed

- **transform/to_uppercase.py**: Removed since this is now included in `transform/to_case.py`.
- **transform/to_lowercase.py**: Removed since this is now included in `transform/to_case.py`.
- **tests/transform**: Removed tests for removed `to_uppercase.py` and `to_lowercase.py` files.
- **tests/utils/transform.py**: Added test cases for upper case, lower case and meme case.

## v0.3.0

### Added

- **Type checking utilities**: Added `is_single_value()`, `is_tuple_value()`, and `is_nested_tuple_value()` utility functions with TypeGuard support for runtime type checking and compile-time type narrowing in ChildNode implementations.
- **TypeGuard overloads**: Added overload signatures for individual primitive types (`str`, `int`, `float`, `bool`) and common union types (`int | float`, `str | Path`, `str | datetime`) to enable precise type narrowing with explicit type parameters.
- **ChildNodeProcessError**: Added new base exception class for errors that must be raised within `ChildNode.process()` methods, with automatic child node name detection via frame inspection (walks up to 10 stack frames).
- **UnhandledValueError**: Added specialized exception for unexpected values in `process()` methods with automatic type formatting and child node context.

### Updated

- **Error handling**: Enhanced error system with automatic context detection. Exceptions now automatically include the child node name without manual parameter passing using Python frame inspection.
- **Error formatting**: `ChildNodeProcessError` now supports named string formatting with `{name}` placeholder and custom kwargs for flexible error messages in subclasses.
- **Transformers**: Updated `to_lowercase()`, `to_uppercase()`, and `as_path()` transformers to use new type-checking utilities with TypeGuard for improved type safety and support for all three value structures (single, flat tuple, nested tuple).
- **Validators**: Updated `is_positive()` validator to handle all three value structures using type-checking utilities with `(int, float)` union type support.
- **Type checking API**: Simplified type-checking utilities to require explicit type parameters.
- **Documentation**: Updated `CONTRIBUTING.md` with guidelines for creating validators/transformers, including the new type-checking utilities pattern and error handling best practices.

## v0.2.1

### Updated

- **Changelog**: Wrapped all `@` with backticks to avoid Github user mentions.
- **format_list**: Now supports asymmetric wrapping by providing a tuple of two strings `str` or `tuple[str, str]`.
- **TypeMismatchError**: Now uses the asymmetric wrapping in `format_list` to show types as `<str>`, etc.

### Removed

- **CI/CD**: Removed "View Full Release" section of the release notes.

## v0.2.0

### Added

- **`@option`**: Added `nargs` parameter to control number of arguments per occurrence (defaults to `1`).
- **Union type support**: ChildNode validators/transformers now support union types (e.g., `str | int | tuple[str, ...]`) for flexible type validation across different parent configurations.
- **Flexible validation**: Single ChildNode can now handle multiple value structures (single, flat tuple, nested tuple) using union type hints.
- **format_list()**: Added utility function for formatting lists with natural language conjunctions and optional prefixes.
- **Integration tests**: Added tests for union type validation, nargs/multiple combinations, and flexible type support.

### Updated

- **`@option`**: Updated to support `nargs` parameter alongside `multiple` for fine-grained control over value structure.
- **`@argument`**: Both `@option` and `@argument` now support the same `nargs` API.
- **Type validation**: Improved ChildNode type validation to support union types (both `|` and `typing.Union` syntax).
- **Type validation**: Validation now checks if any union member matches the parent's configuration (single, flat tuple, or nested tuple).
- **Type validation**: Added detailed error messages explaining value structure mismatches with suggestions for correct type hints.
- **TypeMismatchError**: Updated to use `format_list()` for human-readable type lists.
- **Docs**: Updated `OPTION.md` with `nargs` and `multiple` behavior table and union type validation examples.
- **Docs**: Updated `ARGUMENT.md` with `nargs` behavior table and union type validation examples.
- **Docs**: Condensed documentation to focus on core concepts rather than exhaustive examples.

### Fixed

- **Type validation**: Fixed union type handling to properly expand `UnionType` (Python 3.10+ `|` syntax) in addition to `typing.Union`.
- **Type validation**: Fixed validation to correctly handle union types with different type support per structure.
- **Code quality**: Extracted `_expand_union_types()` helper method to eliminate code duplication in ChildNode.
- **Code quality**: Removed unused `parent_type` parameter from `_collect_relevant_types()` method.

## v0.1.1

### Added

- **`@as_path`**: New decorator to transform and validate a string to a path.
- **`@to_lowercase`**: Added decorator to transform a string to lowercase.
- **`@to_uppercase`**: Added decorator to transform a string to uppercase.

## v0.1.0

### Added

- **`@argument`**: Added automatic type inference for `Argument` class.
- **`@argument`**: Added sentinel value `_MISSING` to properly distinguish between no default and `default=None`.
- **ChildNode**: Added new `context` parameter for the `ChildNode.process()` method.
- **ChildNode**: Added new `ProcessMethod` data class.
- **ChildNode**: Added `ProcessContext` helper methods: `is_tag()`, `is_option()`, `is_argument()`, `is_env()`, `get_tag_values()`.
- **ChildNode**: Added type-hint-first system for `ChildNode` with automatic type inference from `process()` method signature.
- **ChildNode**: Added `get_supported_types()` method to `ChildNode` for inspecting inferred types.
- **ChildNode**: Added `should_skip_none()` method to `ChildNode` with automatic inference from type hints.
- **ChildNode**: Added `TypeMismatchError` exception for type validation failures.
- **`@option`**: Added automatic type inference for `Option` class.
- **`@option`**: Made `is_flag` and `type` parameters exclusive for `option` decorator.
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
- **`@option`**: Updated `Option` class to infer type from default value when not explicitly specified.
- **`@argument`**: Updated `Argument` class to infer type from default value when not explicitly specified.
- **`@argument`**: Updated `Argument` class to automatically set `required=False` when `default` is provided (including `None`).
- **`@argument`**: Updated `_root_node.py` to properly pass `required` parameter to Click's `argument()` function.
- **Docs**: Updated documentation for `Option` with type inference section and examples.
- **Docs**: Updated documentation for `Argument` with type inference section and examples.
- **Docs**: Updated `CHILD_NODE.md` documentation with type-hint-first approach and ProcessContext helpers.
- **Docs**: Updated `CHILD_NODE.md` with comprehensive "Error Handling" section explaining `ValidationError`, `TransformError`.
- **Docs**: Updated all code examples in `CHILD_NODE.md`, `README.md`, `TREE.md`, and `GLOBAL_NODE.md` to use `ValidationError` instead of `ValueError`.
- **Docs**: Updated `ARGUMENT.md` and `OPTION.md` with type inference sections.
- **Docs**: Updated structure of `CHANGELOG.md`.
- **`@tag`**: Updated tag processing to iterate through each parent node value individually.
- **Testing**: Updated unit tests for new process context parameter.
- **Testing**: Updated all validator and transformer tests to use `ValidationError` and `TransformError`.
- **pyproject.toml**: Disabled the pyright error `reportUnnecessaryIsInstance` (Disabled the warning for unnecessary isinstance checks).

### Fixed

- **`@argument`**: Fixed required/optional argument behavior to match Click's semantics (arguments with defaults are optional).
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

- **`@env`**: Fixed error output for one or more missing environment variables.

## v0.0.1

### Added

- **`@tag`**: Added `tag` decorator with unit tests.
- **`@option`**: Added `option` decorator with unit tests.
- **`@group`**: Added `group` decorator with unit tests.
- **`@env`**: Added `env` decorator with unit tests.
- **`@command`**: Added `command` decorator with unit tests.
- **`@argument`**: Added `argument` decorator with unit tests.
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
