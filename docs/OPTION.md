![Banner](../assets/click-extended-documentation-banner.png)

# Option

An option in the command line interface is a named parameter that can be specified using flags. For this library, an option is an extension of the `ParentNode`, meaning it injects values into the context.

## Parameters

| Name       | Description                                                                                                                                    | Type             | Required | Default  |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | -------- |
| `long`     | The long flag for the option (e.g., `--port`, `--config-file`). The parameter name is extracted by removing `--` and converting to snake_case. | str              | Yes      |          |
| `short`    | The short flag for the option (e.g., `-p`, `-c`). Single letter with hyphen prefix.                                                            | str              | No       | None     |
| `is_flag`  | Whether this is a boolean flag (no value needed). When `True`, defaults to `False` if not provided.                                            | bool             | No       | False    |
| `type`     | Type to convert input to. If not specified, defaults to `str` or is inferred from `default`. Supports primitives and Click types.              | type             | No       | Inferred |
| `multiple` | Whether to allow multiple values for this option. Can be specified multiple times on command line.                                             | bool             | No       | False    |
| `help`     | Help text displayed in CLI help output.                                                                                                        | str              | No       | None     |
| `required` | Whether the option is required. Defaults to `False` (options are typically optional by nature).                                                | bool             | No       | False    |
| `default`  | Default value if option not provided.                                                                                                          | Any              | No       | None     |
| `tags`     | Tag(s) to associate with this option for validation or grouping. Used with the `@tag` decorator.                                               | str or list[str] | No       | None     |

> [!NOTE]
> The parameter name in your function is automatically derived from the long flag by removing `--` and converting hyphens to underscores (e.g., `--config-file` becomes `config_file`).

## Type Inference

The `type` parameter supports automatic inference based on the following rules:

1. **Explicit type specified**: Uses the specified type (e.g., `type=int`)
2. **Default value provided**: Infers type from the default value (e.g., `default=5` → `int`)
3. **Neither specified**: Defaults to `str`

### Examples

```python
# Type inferred as int from default
@option("--port", default=8080)  # type = int

# Type inferred as float from default
@option("--ratio", default=1.5)  # type = float

# Type defaults to str (no default, no type)
@option("--name")  # type = str

# Explicit type overrides inference
@option("--value", type=str, default=42)  # type = str, not int
```

This inference system helps reduce boilerplate while maintaining type safety and enabling proper validation.

## Type Inference and Validators

Type inference integrates seamlessly with the validation system. When using validators that specify supported types (like `@is_positive()` which supports `int` and `float`), the inferred type is automatically checked:

```python
from click_extended import command, option
from click_extended.validation import is_positive

# Working
@command()
@option("--count", default=5)
@is_positive()
def process(count: int):
    print(f"Processing {count} items")

@command()
@option("--port", type=int)
@is_positive()
def serve(port: int):
    print(f"Serving on port {port}")

# Raises exception
@command()
@option("--name")  # Type inferred as str
@is_positive()  # Error: is_positive only supports int and float
def greet(name: str):
    print(f"Hello, {name}!")
```

This type checking happens at validation time, providing clear error messages when validators are applied to incompatible types.

## Examples

### Basic Usage

```python
from click_extended import command, option

@command()
@option("--name")
def greet(name: str):
    print(f"Hello, {name}!")
```

### With Short Flag

```python
from click_extended import command, option

@command()
@option("--port", "-p", type=int, default=8080)
def start_server(port: int):
    print(f"Starting server on port {port}")
```

### Boolean Flag

```python
from click_extended import command, option

@command()
@option("--verbose", "-v", is_flag=True)
def process(verbose: bool):
    if verbose:
        print("Verbose mode enabled")
    print("Processing...")
```

### Required Option

```python
from click_extended import command, option

@command()
@option("--api-key", required=True)
def deploy(api_key: str):
    print(f"Deploying with API key: {api_key}")
```

### Multiple Values

```python
from click_extended import command, option

@command()
@option("--tag", multiple=True)
def build(tag: tuple[str, ...]):
    for t in tag:
        print(f"Adding tag: {t}")
```

### With Type Conversion

```python
from click_extended import command, option

@command()
@option("--count", type=int, default=10)
@option("--rate", type=float, default=1.5)
def simulate(count: int, rate: float):
    print(f"Running {count} simulations at {rate}x speed")
```

### With Tags

```python
from click_extended import command, option

@command()
@option("--config", tags=["config", "required"])
def setup(config: str):
    print(f"Using config: {config}")
```

### Name Transformation

```python
from click_extended import command, option

@command()
@option("--config-file")  # Becomes "config_file" parameter
def load(config_file: str):
    print(f"Loading config from: {config_file}")
```

### Using Click Types

```python
from click_extended import command, option
import click

@command()
@option("--input", type=click.Path(exists=True))
@option("--output", type=click.File("w"))
@option("--format", type=click.Choice(["json", "yaml", "xml"]))
def convert(input: str, output, format: str):
    print(f"Converting {input} to {format}")
```

### Multiple Options with Short Flags

```python
from click_extended import command, option

@command()
@option("--host", "-h", default="localhost")
@option("--port", "-p", type=int, default=8080)
@option("--debug", "-d", is_flag=True)
def serve(host: str, port: int, debug: bool):
    """Start a development server."""
    mode = "debug" if debug else "production"
    print(f"Server running at {host}:{port} in {mode} mode")
```

## Complete Example

```python
from click_extended import command, option, argument
import click

@command()
@argument("source", type=click.Path(exists=True))
@option("--output", "-o", default="./dist")
@option("--format", "-f", type=click.Choice(["json", "yaml"]), default="json")
@option("--verbose", "-v", is_flag=True)
@option("--tag", multiple=True, help="Add tags to the output")
def export(source: str, output: str, format: str, verbose: bool, tag: tuple[str, ...]):
    """Export data from source to output directory."""
    if verbose:
        print(f"Exporting {source} to {output} as {format}")
        for t in tag:
            print(f"Tag: {t}")
    print("Export complete!")

if __name__ == "__main__":
    export()
```
