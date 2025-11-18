![Banner](../assets/click-extended-banner.png)

# Command

A command is the entry point for a CLI application. For this library, a command is an extension of the `RootNode`, which serves as the foundation for building CLI commands with automatic value injection from decorators like `@option` and `@argument`.

## Parameters

| Name       | Description                                                                                                            | Type             | Required | Default       |
| ---------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | ------------- |
| `name`     | The name of the command. If not provided, uses the decorated function's name.                                          | str              | No       | Function name |
| `aliases`  | Alternative name(s) for the command. Can be a single string or a list of strings for multiple aliases.                 | str or list[str] | No       | None          |
| `help`     | Help text displayed in CLI help output. If not provided, uses the first line of the function's docstring.              | str              | No       | None          |
| `**kwargs` | Additional arguments to pass to `click.Command` (e.g., `context_settings`, `epilog`, `short_help`, `add_help_option`). | Any              | No       | None          |

> **Note:** The `@command` decorator must be the outermost decorator (furthest from the `def` statement) when stacking with `@option`, `@argument`, and other decorators.

## Examples

### Basic Usage

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

```python
from click_extended import command

@command(help="Display a greeting message")
def greet():
    print("Hello!")

if __name__ == "__main__":
    greet()
```

### With Aliases

```python
from click_extended import command

@command("server", aliases=["srv", "s"])
def start_server():
    """Start the development server."""
    print("Server starting...")

if __name__ == "__main__":
    start_server()
```

### Single Alias

```python
from click_extended import command

@command("build", aliases="b")
def build_project():
    """Build the project."""
    print("Building...")

if __name__ == "__main__":
    build_project()
```

### With Options and Arguments

```python
from click_extended import command, option, argument

@command()
@argument("filename")
@option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def process(filename: str, verbose: bool):
    """Process a file."""
    if verbose:
        print(f"Processing {filename} in verbose mode")
    else:
        print(f"Processing {filename}")

if __name__ == "__main__":
    process()
```

### Using Docstring as Help

```python
from click_extended import command, argument

@command()
@argument("name")
def greet(name: str):
    """Greet a person by name.

    This command displays a personalized greeting message.
    The help text shown in the command list will only show
    the first line of this docstring.
    """
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

> **Note:** When using a multiline docstring, only the first line is used as the short help text in command listings. The full docstring is still available when viewing detailed help (e.g., `--help`).

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
