![Banner](../assets/click-extended-documentation-banner.png)

# Root Node

The `RootNode` is the base class for top-level CLI entry points in click-extended. It serves as the foundation for both `@command` and `@group` decorators, providing the core functionality for building CLI applications with automatic value injection, tree visualization, and parameter management.

Read more about the [command](./COMMAND.md) and [group](./GROUP.md).

## Overview

A `RootNode` represents the entry point of your CLI application. It orchestrates the following:

- **Tree Building**: Automatically collects and organizes all decorated parameters (`@option`, `@argument`, `@env`)
- **Value Injection**: Injects parameter values from decorators into your function
- **Tag Management**: Coordinates cross-parameter validation through tags
- **Click Integration**: Wraps Click's command/group functionality with enhanced features
- **Visualization**: Provides `.visualize()` method to display the parameter tree structure

## Subclasses

The `RootNode` class is abstract and provides two concrete implementations that serve as the foundation for all CLI applications:

- **`Command`**: Single CLI command (see [COMMAND.md](./COMMAND.md))
- **`Group`**: Container for multiple commands/subgroups (see [GROUP.md](./GROUP.md))

> [!INFO]
> These two subclasses are the only intended implementations of `RootNode`. Users should not need to extend `RootNode` directly, as `@command` and `@group` cover all standard CLI use cases. The abstraction exists to provide shared functionality between commands and groups.

## Architecture

### RootNodeWrapper

All decorated functions are wrapped in a `RootNodeWrapper` which:

- Delegates attribute access to the underlying Click object
- Provides the `.visualize()` method
- Makes the wrapper callable like the original Click command/group

### Tree Structure

Each `RootNode` maintains a `Tree` instance that tracks:

- **Root**: The `RootNode` itself
- **Children**: All `ParentNode` instances (`@option`, `@argument`, `@env`)
- **Tags**: Named groups for cross-parameter validation
- **Globals**: Global nodes with injection capabilities

## Parameters

When creating a `RootNode` (via `@command` or `@group`):

| Name       | Description                                                                                    | Type             | Required | Default       |
| ---------- | ---------------------------------------------------------------------------------------------- | ---------------- | -------- | ------------- |
| `name`     | The name of the command/group. If not provided, uses the decorated function's name.            | str              | No       | Function name |
| `aliases`  | Alternative name(s) for the command/group. Can be a single string or list of strings.          | str or list[str] | No       | None          |
| `help`     | Help text displayed in CLI help output. If not provided, uses the first line of the docstring. | str              | No       | None          |
| `**kwargs` | Additional arguments to pass to Click (e.g., `context_settings`, `epilog`).                    | Any              | No       | None          |

## Methods

### `.visualize()`

Display the tree structure of the command/group, showing all parameters and their relationships.

```python
from click_extended import command, option, argument

@command()
@option("--verbose", "-v", is_flag=True)
@argument("filename")
def process(filename: str, verbose: bool):
    """Process a file."""
    pass

if __name__ == "__main__":
    process.visualize()
```

The output will be as follows:

```txt
process
  verbose
  filename
```

## Value Injection

The `RootNode` automatically injects parameter values into your function:

```python
from click_extended import command, option, argument, env

@command()
@option("--port", "-p", type=int, default=8000)
@argument("host")
@env("API_KEY")
def server(host: str, port: int, api_key: str):
    """Start a server."""
    print(f"Starting server on {host}:{port}")
    print(f"Using API key: {api_key}")
```

When called, the function receives:

- `host` from the command-line argument
- `port` from the `--port` option
- `api_key` from the `API_KEY` environment variable

All parameters are automatically matched by name (converted to snake_case).

## Duplicate Name Detection

The `RootNode` ensures all parameter names are unique across:

- Options (`@option`)
- Arguments (`@argument`)
- Environment variables (`@env`)
- Tags (`@tag`)

If duplicates are detected, a `DuplicateNameError` is raised with details.

## Async Support

The `RootNode` automatically handles async functions:

```python
from click_extended import command, option
import asyncio

@command()
@option("--delay", type=int, default=1)
async def wait(delay: int):
    """Wait for a specified time."""
    print(f"Waiting {delay} seconds...")
    await asyncio.sleep(delay)
    print("Done!")
```

The decorator wraps async functions in `asyncio.run()` automatically.

## Examples

### Basic Command

```python
from click_extended import command

@command()
def hello():
    """Say hello."""
    print("Hello, World!")

if __name__ == "__main__":
    hello()
```

### Command with Parameters

```python
from click_extended import command, option, argument

@command()
@option("--greeting", default="Hello")
@argument("name")
def greet(name: str, greeting: str):
    """Greet someone."""
    print(f"{greeting}, {name}!")

if __name__ == "__main__":
    greet()
```

### Group with Commands

```python
from click_extended import group, command, option

@group()
@option("--verbose", "-v", is_flag=True)
def cli(verbose: bool):
    """Main CLI application."""
    if verbose:
        print("Verbose mode enabled")

@command()
def hello():
    """Say hello."""
    print("Hello!")

@command()
def goodbye():
    """Say goodbye."""
    print("Goodbye!")

cli.add(hello).add(goodbye)

if __name__ == "__main__":
    cli()
```

### Using Aliases

```python
from click_extended import command, option

@command("database", aliases=["db", "d"])
@option("--host", default="localhost")
def database_command(host: str):
    """Manage database operations."""
    print(f"Connecting to {host}")

if __name__ == "__main__":
    database_command()
```

## See Also

- [COMMAND.md](./COMMAND.md) - Single CLI commands
- [GROUP.md](./GROUP.md) - Command groups and hierarchies
- [OPTION.md](./OPTION.md) - Named parameters
- [ARGUMENT.md](./ARGUMENT.md) - Positional parameters
- [ENV.md](./ENV.md) - Environment variables
- [TAG.md](./TAG.md) - Cross-parameter validation
