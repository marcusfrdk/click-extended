![Banner](./assets/click-extended-banner.png)

# Click Extended

![top language](https://img.shields.io/github/languages/top/marcusfrdk/click-extended)
![code size](https://img.shields.io/github/languages/code-size/marcusfrdk/click-extended)
![last commit](https://img.shields.io/github/last-commit/marcusfrdk/click-extended)
![issues](https://img.shields.io/github/issues/marcusfrdk/click-extended)
![contributors](https://img.shields.io/github/contributors/marcusfrdk/click-extended)
![PyPI](https://img.shields.io/pypi/v/click-extended)
![License](https://img.shields.io/github/license/marcusfrdk/click-extended)
![Downloads](https://static.pepy.tech/badge/click-extended)
![Monthly Downloads](https://static.pepy.tech/badge/click-extended/month)

An extension of the [Click](https://github.com/pallets/click) library with additional features like aliasing, asynchronous support, an extended decorator API and more.

## Features

- **Aliasing**: Add multiple aliases to a group or command.
- **Async supprt**: Automatically run both synchronous and asynchronous functions.
- **Extensible decorator API**: Extend the Click decorator API with custom decorators like validators, transformers, and more.
- **Environment variables**: Automatically validate and inject environment variables into the function.
- **Fully type-hinted**: The library is fully type-hinted and provides good types for easy development.
- **Help alias**: The `-h` and `--help` automatically show the help menu unless overridden.

## Installation

```bash
pip install click-extended
```

## Requirements

- **Python**: 3.10 or higher

## Quick Start

### Basic Command

```python
from click_extended import command, option

@command()
@option("--name", default="World", help="Name to greet")
@option("--count", type=int, default=1, help="Number of greetings")
def greet(name: str, count: int):
    """Greet someone multiple times."""
    for _ in range(count):
        print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

```bash
$ python app.py --name Alice --count 3
Hello, Alice!
Hello, Alice!
Hello, Alice!
```

### Async Support

```python
import asyncio

from click_extended import command, option

@command()
@option("--url", required=True, help="URL to fetch")
async def fetch(url: str):
    """Fetch data from a URL asynchronously."""
    await asyncio.sleep(1)
    print(f"Fetched data from {url}")

if __name__ == "__main__":
    fetch()
```

### Command Aliases

```python
from click_extended import command, option

@command(aliases=["hi", "hello"])
@option("--name", default="World")
def greet(name: str):
    """Greet someone."""
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

```bash
$ python app.py greet --name Alice
Hello, Alice!
$ python app.py hi --name Bob
Hello, Bob!
$ python app.py hello --name Charlie
Hello, Charlie!
```

### Environment Variables

Environment variables are automatically loaded from the `.env` file, but as long as the variable is defined in your system environment, it will work.

```txt
API_TOKEN=secret123
```

```python
from click_extended import command, option, env

@command()
@option("--token", help="API token")
@env("API_TOKEN", name="token", required=True)
def api_call(token: str):
    """Make an API call with authentication."""
    print(f"Using token: {token[:8]}...")

if __name__ == "__main__":
    api_call()
```

```bash
$ python app.py
Using token: secret12...
```

### Value Validation

```python
from click_extended import command, option, ChildNode, ProcessContext

class IsPositive(ChildNode):
    """Validate that a number is positive."""

    def process(self, value, context: ProcessContext):
        if value <= 0:
            raise ValueError(f"Value must be positive, got {value}")

def is_positive(*args, **kwargs):
    """Validate positive numbers."""
    return IsPositive.as_decorator(*args, **kwargs)

@command()
@option("--count", type=int, required=True)
@is_positive()
def process(count: int):
    """Process a positive number of items."""
    print(f"Processing {count} items")

if __name__ == "__main__":
    process()
```

```bash
$ python app.py --count 5
Processing 5 items
$ python app.py --count -1
Error: Value must be positive, got -1
```

## Documentation

### Core Concepts

- [Commands and Groups](./docs/ROOT_NODE.md) - CLI entry points
- [Options, Arguments, and Environment Variables](./docs/PARENT_NODE.md) - Parameter sources
- [Validators and Transformers](./docs/CHILD_NODE.md) - Value processing
- [Global Nodes](./docs/GLOBAL_NODE.md) - Tree-level operations
- [Tags](./docs/TAG.md) - Cross-parameter validation
- [Tree Architecture](./docs/TREE.md) - Internal structure

### Guides

- [Migrating from Click](./docs/MIGRATING_FROM_CLICK.md) - Upgrade guide

## Contributing

Contributors are more than welcome to work on this project. Read the [contribution documentation](./CONTRIBUTING.md) to learn more.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgements

This project is built on top of the [Click](https://github.com/pallets/click) library.
