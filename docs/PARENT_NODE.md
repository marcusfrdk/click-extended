![Banner](../assets/click-extended-documentation-banner.png)

# Parent Node

The `ParentNode` is the base class for CLI parameters in click-extended. It serves as the foundation for `@option`, `@argument`, and `@env` decorators, providing the core functionality for value retrieval, processing through child nodes (validators/transformers), and integration with the parameter tree.

Read more about the [option](./OPTION.md), [argument](./ARGUMENT.md), and [env](./ENV.md).

## Overview

A `ParentNode` represents a single parameter in your CLI application. It orchestrates:

- **Value Retrieval**: Gets raw values from sources (command-line args, options, environment variables)
- **Value Processing**: Passes values through a chain of `ChildNode` instances for validation and transformation
- **Tag Association**: Supports grouping parameters with tags for cross-parameter validation
- **Caching**: Caches processed values for efficiency
- **Metadata Management**: Tracks whether values were explicitly provided vs using defaults

## Parameters

When creating a `ParentNode` (via `@option`, `@argument`, or `@env`):

| Name       | Description                                                                                      | Type             | Required | Default |
| ---------- | ------------------------------------------------------------------------------------------------ | ---------------- | -------- | ------- |
| `name`     | The parameter name for injection (automatically derived for `@option`).                          | str              | Yes      | -       |
| `help`     | Help text displayed in CLI help output.                                                          | str              | No       | None    |
| `required` | Whether this parameter is required.                                                              | bool             | No       | False   |
| `default`  | Default value if not provided.                                                                   | Any              | No       | None    |
| `tags`     | Tag(s) to associate with this parameter for grouping. Can be a single string or list of strings. | str or list[str] | No       | None    |

## Methods

### `get_raw_value() -> Any`

Retrieve the raw value from the parameter's source (command-line, environment variable, etc.). Must be implemented by subclasses.

```python
class Option(ParentNode):
    def get_raw_value(self) -> Any:
        return self._raw_value
```

### `set_raw_value(value: Any, was_provided: bool = False) -> None`

Set the raw value manually. Called by `RootNode` during parameter injection.

```python
option_node.set_raw_value("value", was_provided=True)
```

### `get_value() -> Any`

Get the processed value after passing through all child nodes. Results are cached.

```python
from click_extended import option

@option("--count", type=int, default=1)
def my_command(count: int):
    pass
```

### `was_provided() -> bool`

Check if the user explicitly provided this value (vs using the default).

```python
if option_node.was_provided():
    print("User provided a value")
else:
    print("Using default value")
```

## Caching

The `ParentNode` caches processed values for efficiency. The first call to `get_value()` retrieves the raw value, processes through children and caches the result. For subsequent calls, it returns the cached value immediately. The cache is invalidated when `set_raw_value()` is called.

```python
value1 = parent_node.get_value() # Not cached
value2 = parent_node.get_value() # Cached
parent_node.set_raw_value("new_value") # Reset cache
value3 = parent_node.get_value() # Not cached
```

## Implementation

To create a new `ParentNode` subclass, you need to implement the abstract `get_raw_value()` method and optionally create a decorator function for convenience.

### Step 1: Create the ParentNode Subclass

Inherit from `ParentNode` and implement `get_raw_value()`:

```python
from typing import Any
from click_extended import ParentNode

class CustomSource(ParentNode):
    """ParentNode that retrieves values from a custom source."""

    def __init__(
        self,
        name: str,
        source_key: str, # Custom parameter
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the custom source parameter.

        Args:
            name (str):
                Parameter name for injection.
            source_key (str):
                Key to look up in the custom source.
            help (str):
                Help text.
            required (bool):
                Whether the parameter is required.
            default (Any):
                Default value if not found.
            tags (str | list[str], optional): Tag(s) for grouping.
            **kwargs (Any):
                Additional keyword arguments.
        """
        super().__init__(
            name=name,
            help=help,
            required=required,
            default=default,
            tags=tags,
        )
        self.source_key = source_key
        self.extra_kwargs = kwargs

    def get_raw_value(self) -> Any:
        """
        Retrieve value from the custom source.

        Returns:
            Any:
                The value from the source, or default if not found.

        Raises:
            ValueError: If required but not found in source.
        """
        value = self._fetch_from_custom_source(self.source_key)
        was_provided = value is not None

        if value is None:
            if self.required:
                raise ValueError(
                    f"Required value for '{self.source_key}' not found"
                )
            value = self.default

        self._was_provided = was_provided
        self._raw_value = value
        return value

    def _fetch_from_custom_source(self, key: str) -> Any:
        """Fetch value from your custom source (implement as needed)."""
        import json
        try:
            with open("config.json") as f:
                config = json.load(f)
                return config.get(key)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
```

### Step 2: Create a Decorator Function (Optional but Recommended)

Create a decorator function for easier usage:

```python
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

def custom_source(
    source_key: str,
    name: str | None = None,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to inject a value from custom source.

    Args:
        source_key (str):
            Key to look up in the custom source.
        name (str, optional):
            Parameter name (defaults to source_key in snake_case).
        help (str, optional):
            Help text.
        required (bool, optional):
            Whether required.
        default (Any, optional):
            Default value.
        tags (str | list[str], optional):
            Tag(s) for grouping.
        **kwargs (Any):
            Additional arguments.

    Returns:
        Callable:
            Decorator function that registers the custom source node.
    """
    from click_extended.utils.transform import Transform

    param_name = (
        name if name is not None
        else Transform(source_key).to_snake_case()
    )

    return CustomSource.as_decorator(
        name=param_name,
        source_key=source_key,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
```

### Step 3: Use Your Custom ParentNode

```python
from click_extended import command

@command()
@custom_source("database.host", default="localhost")
@custom_source("database.port", required=True)
def connect(database_host: str, database_port: int):
    """Connect using custom configuration source."""
    print(f"Connecting to {database_host}:{database_port}")
```

## See Also

- [OPTION.md](./OPTION.md) - Named command-line parameters
- [ARGUMENT.md](./ARGUMENT.md) - Positional command-line parameters
- [ENV.md](./ENV.md) - Environment variable parameters
- [CHILD_NODE.md](./CHILD_NODE.md) - Validators and transformers
- [TAG.md](./TAG.md) - Cross-parameter validation
- [ROOT_NODE.md](./ROOT_NODE.md) - CLI entry points
