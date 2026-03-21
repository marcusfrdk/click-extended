![Banner](./assets/click-extended-banner.png)

# Click Extended

![top language](https://img.shields.io/github/languages/top/marcusfrdk/click-extended)
![code size](https://img.shields.io/github/languages/code-size/marcusfrdk/click-extended)
![last commit](https://img.shields.io/github/last-commit/marcusfrdk/click-extended)
![tests](https://github.com/marcusfrdk/click-extended/actions/workflows/tests.yml/badge.svg)
![release](https://github.com/marcusfrdk/click-extended/actions/workflows/release.yml/badge.svg)
![issues](https://img.shields.io/github/issues/marcusfrdk/click-extended)
![contributors](https://img.shields.io/github/contributors/marcusfrdk/click-extended)
![pypi](https://img.shields.io/pypi/v/click-extended)
![license](https://img.shields.io/github/license/marcusfrdk/click-extended)
![downloads](https://static.pepy.tech/badge/click-extended)
![monthly downloads](https://static.pepy.tech/badge/click-extended/month)

An extension of the [Click](https://github.com/pallets/click) library with additional features like aliasing, asynchronous support, an extended decorator API and more.

## Features

- **Decorator API**: Extend the functionality your command line by adding custom data sources, data processing pipelines, and more.
- **Aliasing**: Use aliases for groups and commands to reduce boilerplate and code repetition.
- **Tags**: Use tags to group several data sources together to apply batch processing.
- **Async Support**: Native support for declaring functions and methods asynchronous.
- **Environment Variables**: Built-in support for loading and using environment variables as a data source.
- **Full Type Support**: Built with type-hinting from the ground up, meaning everything is fully typed.
- **Improved Errors**: Improved error output like tips, debugging, and more.
- **Short Flag Concatenation**: Automatically support concatenating short hand flags where `-r -f` is the same as `-rf`.
- **Global state**: Access global state through the context's `data` property.
- **Hook API**: Hook into various points and run custom functions in the lifecycle.

## Installation

```bash
pip install click-extended
```

## Requirements

- **Python**: 3.10 or higher

## Quick Start

### Basic Command

A simple command with a positional argument and an option. The command is also accessible via the alias `greet`.

```python
from click_extended import command, argument, option

@command(aliases="greet")
@argument("name")
@option("count", "-n", type=int, default=1, help="Number of times to greet.")
def hello(name: str, count: int) -> None:
    """Greet someone by name."""
    for _ in range(count):
        print(f"Hello, {name}!")

if __name__ == "__main__":
    hello()
```

```bash
$ python cli.py "Alice"
Hello, Alice!
```

```bash
$ python cli.py "Alice" -n 3
Hello, Alice!
Hello, Alice!
Hello, Alice!
```

### Command Group

A group that organises multiple subcommands. Commands can have aliases to reduce boilerplate.

```python
from click_extended import group, command, argument, option

@group()
def cli() -> None:
    """A simple task manager."""

@cli.command(aliases=["ls"])
@option("status", default="all", help="Filter by status: all, open, done.")
def list_tasks(status: str) -> None:
    """List all tasks."""
    print(f"Listing tasks with status: {status}")

@cli.command(aliases=["add"])
@argument("title")
@option("priority", "-p", default="medium", help="Task priority: low, medium, high.")
def create_task(title: str, priority: str) -> None:
    """Create a new task."""
    print(f"Created task '{title}' with priority '{priority}'.")

if __name__ == "__main__":
    cli()
```

```bash
$ python cli.py list-tasks --status open
Listing tasks with status: open
```

```bash
$ python cli.py add "Buy groceries" -p high
Created task 'Buy groceries' with priority 'high'.
```

### Multi-File CLI

For anything beyond a few commands, splitting each command into its own file keeps the project manageable. Use `group.add()` to wire everything together at the entrypoint.

**`cli/entrypoint.py`**

```python
from click_extended import group

from .commands.users import users
from .commands.deploy import deploy

@group()
def cli() -> None:
    """Production deployment tool."""

cli.add(users)
cli.add(deploy)

if __name__ == "__main__":
    cli()
```

**`cli/commands/users.py`**

```python
from click_extended import group, command, argument, option
from click_extended.decorators import is_email, length, not_empty, strip

@group(aliases=["u"])
def users() -> None:
    """Manage users."""

@users.command(aliases=["add"])
@argument("email")
@is_email()
@option("role", "-r", default="viewer", help="Role: viewer, editor, admin.")
def create_user(email: str, role: str) -> None:
    """Create a new user."""
    print(f"Created user '{email}' with role '{role}'.")

@users.command(aliases=["rm"])
@argument("email")
@is_email()
def remove_user(email: str) -> None:
    """Remove a user."""
    print(f"Removed user '{email}'.")
```

**`cli/commands/deploy.py`**

```python
from typing import Any
from click_extended import command, option
from click_extended.decorators import to_path, load_json, choice

@command(aliases=["d"])
@option("config", "-c", required=True, help="Path to deployment config.")
@to_path(exists=True, extensions=["json"])
@load_json()
@option("env", "-e", default="staging", help="Target environment.")
@choice("staging", "production")
def deploy(config: dict[str, Any], env: str) -> None:
    """Deploy the application."""
    host = config.get("host", "localhost")
    print(f"Deploying to {host} ({env}).")
```

```bash
$ python -m cli.entrypoint users add "alice@example.com" -r admin
Created user 'alice@example.com' with role 'admin'.
```

```bash
$ python -m cli.entrypoint deploy -c ./config.json -e production
Deploying to api.example.com (production).
```

See the [Splitting Files guide](./docs/guides/SPLITTING_FILES.md) for more patterns.

### Input Validation

Chain built-in decorators to validate and transform values before they reach the function.

```python
from click_extended import command, option
from click_extended.decorators import (
    strip,
    not_empty,
    is_email,
    length,
    dependencies,
)

@command()
@dependencies("username", "email", "password")
@option("username", "-u", required=True)
@strip()
@not_empty()
@option("email", "-e", required=True)
@is_email()
@option("password", "-p", required=True)
@length(min=8, max=64)
def register(username: str, email: str, password: str) -> None:
    """Register a new user account."""
    print(f"Registered '{username}' with email '{email}'.")
```

```bash
$ python cli.py -u "  alice  " -e "alice@example.com" -p "hunter42"
Registered 'alice' with email 'alice@example.com'.
```

```bash
$ python cli.py -u "alice" -e "not-an-email" -p "hunter42"
ValueError (register): 'not-an-email' is not a valid email address.
```

```bash
$ python cli.py -u "alice" -e "alice@example.com" -p "short"
ValueError (register): Value must be at least 8 characters long.
```

### Environment Variables

Load credentials or configuration from environment variables rather than command-line flags.

```python
from click_extended import command, env
from click_extended.decorators import not_empty

@command()
@env("DATABASE_URL", required=True)
@not_empty()
@env("LOG_LEVEL", default="info")
def serve(database_url: str, log_level: str) -> None:
    """Start the application server."""
    print(f"Connecting to {database_url} (log level: {log_level})")
```

```bash
$ python cli.py
ValueError (serve): Required environment variable 'DATABASE_URL' is not set.
```

```bash
$ DATABASE_URL="postgresql://localhost/mydb" python cli.py
Connecting to postgresql://localhost/mydb (log level: info)
```

### Loading a JSON Config File

Use `@to_path` to validate the path and `@load_json` to parse the file contents.

```python
from typing import Any
from click_extended import command, option
from click_extended.decorators import to_path, load_json

@command()
@option("config", "-c", required=True, help="Path to a JSON config file.")
@to_path(exists=True, extensions=["json"])
@load_json()
def deploy(config: dict[str, Any]) -> None:
    """Deploy using a JSON config file."""
    host = config.get("host", "localhost")
    port = config.get("port", 8080)
    print(f"Deploying to {host}:{port}")
```

```bash
$ python cli.py -c ./config.json
Deploying to api.example.com:443
```

### Cross-Parameter Constraints

Use `@requires`, `@conflicts`, and `@exclusive` to express relationships between parameters.

```python
from click_extended import command, option
from click_extended.decorators import requires, conflicts, exclusive

@command()
@exclusive("token", "username")
@option("token", "-t", help="API token for authentication.")
@conflicts("username")
@option("username", "-u", help="Username for basic authentication.")
@requires("password")
@option("password", "-p", help="Password for basic authentication.")
def login(token: str | None, username: str | None, password: str | None) -> None:
    """Authenticate with either a token or username and password."""
    if token:
        print(f"Logged in with token.")
    else:
        print(f"Logged in as '{username}'.")
```

```bash
$ python cli.py -t "mytoken"
Logged in with token.
```

```bash
$ python cli.py -t "mytoken" -u "alice"
ValueError (login): '--token' and '--username' are mutually exclusive.
```

```bash
$ python cli.py -u "alice"
ValueError (login): '--username' requires '--password' to be provided.
```

### Custom Child Node

If the built-in decorators do not cover your use case, you can implement your own child node.

```python
from typing import Any

from click_extended import command, option
from click_extended.classes import ChildNode
from click_extended.types import Context, Decorator


class Slugify(ChildNode):
    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        separator: str = kwargs.get("separator", "-")
        return separator.join(value.lower().split())


def slugify(separator: str = "-") -> Decorator:
    """Convert a string to a URL-friendly slug."""
    return Slugify.as_decorator(separator=separator)


@command()
@option("title", required=True, help="Blog post title.")
@slugify()
def publish(title: str) -> None:
    """Publish a blog post."""
    print(f"Published at /posts/{title}")
```

```bash
$ python cli.py --title "Hello World"
Published at /posts/hello-world
```

```bash
$ python cli.py --title "My New Post"
Published at /posts/my-new-post
```

## Documentation

The full documentation is [available here](./docs/README.md) and goes through the full library, from explaining design choices, how to use the library, and much more.

## Contributing

Contributors are more than welcome to work on this project. Read the [contribution documentation](./CONTRIBUTING.md) to learn more.

## License

This project is licensed under the MIT License, see the [license file](./LICENSE) for details.

## Acknowledgements

This project is built on top of the [Click](https://github.com/pallets/click) library.
