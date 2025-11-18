![Banner](../assets/click-extended-banner.png)

# Group

A group is a command that contains subcommands, allowing you to organize related commands under a common parent. Groups can contain both commands and other groups, enabling hierarchical CLI structures. For this library, a group is an extension of the `RootNode`, which serves as a container for building nested command structures.

## Parameters

| Name       | Description                                                                                                          | Type             | Required | Default       |
| ---------- | -------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | ------------- |
| `name`     | The name of the group. If not provided, uses the decorated function's name.                                          | str              | No       | Function name |
| `aliases`  | Alternative name(s) for the group. Can be a single string or a list of strings for multiple aliases.                 | str or list[str] | No       | None          |
| `help`     | Help text displayed in CLI help output. If not provided, uses the first line of the function's docstring.            | str              | No       | None          |
| `**kwargs` | Additional arguments to pass to `click.Group` (e.g., `context_settings`, `epilog`, `short_help`, `add_help_option`). | Any              | No       | None          |

> **Note:** The `@group` decorator must be the outermost decorator (furthest from the `def` statement) when stacking with `@option`, `@argument`, and other decorators. Groups can have their own options and arguments that are passed to all subcommands.

## Methods

### `.add(cls: RootNode)`

Add a command or another group to this group. This method accepts both `@command` and `@group` decorated functions, enabling nested group hierarchies.

There are two ways of calling the `add()` method, either individually:

```py
my_group.add(my_command)
my_group.add(another_command)
my_group.add(subgroup)
```

or chained:

```py
my_group.add(my_command).add(another_command).add(subgroup)
```

## Examples

### Basic Usage

```py
from click_extended import group, command

@group()
def cli():
    """Main CLI application."""

@command()
def hello():
    """Say hello."""
    print("Hello!")

@command()
def goodbye():
    """Say goodbye."""
    print("Goodbye!")

cli.add(hello)
cli.add(goodbye)

if __name__ == "__main__":
    cli()
```

### Named Group

```py
from click_extended import group, command

@group("database")
def db_commands():
    """Database management commands."""

@command()
def migrate():
    """Run migrations."""
    print("Running migrations...")

db_commands.add(migrate)

if __name__ == "__main__":
    db_commands()
```

### With Aliases

```py
from click_extended import group, command

@group("database", aliases=["db", "d"])
def database():
    """Database operations."""

@command()
def backup():
    """Backup the database."""
    print("Backing up...")

database.add(backup)

if __name__ == "__main__":
    database()
```

### Group with Options

```py
from click_extended import group, command, option

@group()
@option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose: bool):
    """CLI with global verbose flag."""
    if verbose:
        print("Verbose mode enabled")

@command()
@option("--force", is_flag=True)
def deploy(verbose: bool, force: bool):
    """Deploy the application."""
    if verbose:
        print("Deploying with force:", force)
    print("Deployed!")

cli.add(deploy)

if __name__ == "__main__":
    cli()
```

### Nested Groups

```py
from click_extended import group, command

@group()
def cli():
    """Main CLI."""

@group()
def database():
    """Database commands."""

@group()
def cache():
    """Cache commands."""

@command()
def migrate():
    """Run database migrations."""
    print("Migrating...")

@command()
def clear():
    """Clear the cache."""
    print("Cache cleared!")

cli.add(database)
cli.add(cache)
database.add(migrate)
cache.add(clear)

if __name__ == "__main__":
    cli()
```

### Group with Environment Variables

```py
from click_extended import group, command, env, option

@group()
@env("DATABASE_URL", required=True)
def db_cli(database_url: str):
    """Database CLI with connection from environment."""

@command()
@option("--dry-run", is_flag=True)
def migrate(database_url: str, dry_run: bool):
    """Run migrations."""
    print(f"Migrating {database_url}")
    if dry_run:
        print("(dry run)")

db_cli.add(migrate)

if __name__ == "__main__":
    db_cli()
```

### Using Docstring as Help

```python
from click_extended import group, command

@group()
def cli():
    """Main application CLI."""

@command()
def status():
    """Check application status."""
    print("Status: Running")

cli.add(status)

if __name__ == "__main__":
    cli()
```

### Complete Example

```python
from click_extended import group, command, option, argument, env
import click

@group(aliases=["app", "a"])
@option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@env("LOG_LEVEL", default="INFO")
def cli(config: str | None, log_level: str):
    """
    Application management CLI.

    Provides commands for deploying, monitoring, and managing
    the application lifecycle.
    """
    if config:
        print(f"Using config: {config}")
    print(f"Log level: {log_level}")

@group(aliases="db")
def database():
    """Database management commands."""

@command(aliases=["mig", "m"])
@option("--dry-run", is_flag=True, help="Simulate without making changes")
def migrate(config: str | None, log_level: str, dry_run: bool):
    """Run database migrations."""
    print("Running migrations...")
    if dry_run:
        print("(dry run mode)")

@command()
@argument("name")
def create(config: str | None, log_level: str, name: str):
    """Create a new migration."""
    print(f"Creating migration: {name}")

@command(aliases=["dep", "d"])
@argument("environment", type=click.Choice(["dev", "staging", "prod"]))
@option("--force", "-f", is_flag=True, help="Force deployment")
@option("--version", type=str, help="Specific version to deploy")
def deploy(
    config: str | None,
    log_level: str,
    environment: str,
    force: bool,
    version: str | None
):
    """Deploy to specified environment."""
    print(f"Deploying to {environment}")
    if version:
        print(f"Version: {version}")
    if force:
        print("Force mode enabled")

@command()
def status(config: str | None, log_level: str):
    """Check deployment status."""
    print("Status: Running")

cli.add(database)
cli.add(deploy)
cli.add(status)
database.add(migrate)
database.add(create)

if __name__ == "__main__":
    cli()
```

```bash
# Show main help
python app.py --help

# Show database subcommands
python app.py database --help

# Run migration
python app.py database migrate

# Run migration with group option
python app.py --config prod.yml database migrate

# Deploy using alias
python app.py dep prod --force

# Create migration
python app.py db create add_users_table
```
