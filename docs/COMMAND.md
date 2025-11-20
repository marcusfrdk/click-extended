![Banner](../assets/click-extended-documentation-banner.png)

# Command

A command is the entry point for all functions in a command line interface. The command is a subclass of the [root node](./ROOT_NODE.md) and handles the tree and context of the entire function lifecycle.

## Parameters

| Name       | Description                                                                                                            | Type             | Required | Default       |
| ---------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | ------------- |
| `name`     | The name of the command. If not provided, uses the decorated function's name.                                          | str              | No       | Function name |
| `aliases`  | Alternative name(s) for the command. Can be a single string or a list of strings for multiple aliases.                 | str or list[str] | No       | None          |
| `help`     | Help text displayed in CLI help output. If not provided, uses the first line of the function's docstring.              | str              | No       | None          |
| `**kwargs` | Additional arguments to pass to `click.Command` (e.g., `context_settings`, `epilog`, `short_help`, `add_help_option`). | Any              | No       | None          |

## Examples

### Basic Usage

Here is a basic example of how to get a simple command line interface working. This example is equivalent to just calling the function directly.

```python
from click_extended import command

@command()
def hello():
    """Simple command that prints hello."""
    print("Hello, World!")

if __name__ == "__main__":
    hello()
```

### Named Command

By default, if a name is not set, the name of the function (`my_function`) is used as the name of the command. However, in this example, we have overridden the name with our own name (`greet`). The name of the command matters when adding one or more commands to a [group](./GROUP.md).

```python
from click_extended import command

@command("greet")
def my_function():
    """Greet the user."""
    print("Hello!")

if __name__ == "__main__":
    my_function()
```

### With Help Text

Help messages are important for creating a well-documented command line interfaces.

```python
from click_extended import command

@command(help="This help message overwrites the default help message.")
def greet():
    """This is the default help message."""
    print("Hello!")

if __name__ == "__main__":
    greet()
```

### With Multi-Line Help Text

Sometimes, you might want to provide proper multi-line docstrings for your function. In this case, the help message is just the first line of the docstring (`This is a function that pongs your ping.`).

```python
from click_extended import command

@command()
def ping():
    """
    This is a function that pongs your ping.

    Returns:
        None:
            It literally returns nothing.
    """
    print("Pong")

if __name__ == "__main__":
    ping()
```

### With Aliases

Aliasing is a powerful way of allowing users to add shortcuts or other names in the command line interface.

```python
from click_extended import command

@command("database", aliases=["db"])
def start_database():
    """Start the database container."""
    print("Starting container...")

if __name__ == "__main__":
    start_database()
```

In the help message, this command will show up as:

```txt
database (db)  Start the database container.
```

### With Parents

A command is just the foundation, but a foundation is nothing without the building blocks. In this example, three [parent nodes](./PARENT_NODE.md) are used.

```python
from click_extended import command, option, argument, env

@command()
@argument("filename")
@option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@env("API_KEY")
def process(filename: str, verbose: bool, api_key: str):
    """Process a file."""

if __name__ == "__main__":
    process()
```

### Complete Example

```python
import os
import click
from click_extended import command, option, argument

@command(
    "convert",
    aliases=["conv", "c"],
    help="Convert files between different formats"
)
@argument("input_file", type=click.Path(exists=True))
@argument("output_file")
@option("--format", "-f", type=click.Choice(["json", "yaml", "xml"]), default="json")
@option("--verbose", "-v", is_flag=True, help="Show detailed progress")
@option("--overwrite", is_flag=True, help="Overwrite existing output file")
def convert(
    input_file: str,
    output_file: str,
    format: str,
    verbose: bool,
    overwrite: bool
):
    """Convert input file to specified format and save to output file."""
    if verbose:
        print(f"Reading from: {input_file}")
        print(f"Writing to: {output_file}")
        print(f"Format: {format}")

    if os.path.exists(output_file) and not overwrite:
        print(f"Error: {output_file} already exists. Use --overwrite to replace.")
        return

    print(f"Converting {input_file} to {format}...")

if __name__ == "__main__":
    convert()
```

### With Custom Click Settings (Advanced)

If you need to change things like the help menu formatting or the context of the underlying Click context, you can override the configuration by passing the regular keyword arguments provided by the underlying Click object (`click.Command`, `click.Argument`, `click.pass_context`, etc.).

```python
from click_extended import command, option

@command(
    "deploy",
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="For more information, visit https://example.com"
)
@option("--environment", "-e", default="production")
def deploy(environment: str):
    """Deploy the application."""
    print(f"Deploying to {environment}")

if __name__ == "__main__":
    deploy()
```
