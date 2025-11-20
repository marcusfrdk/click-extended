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
| `nargs`    | Number of arguments each occurrence accepts. `1` for single value, `>1` for multiple values per occurrence.                                    | int              | No       | 1        |
| `multiple` | Whether the option can appear multiple times on command line. When `True`, value is ALWAYS `tuple[tuple[T, ...], ...]`.                        | bool             | No       | False    |
| `help`     | Help text displayed in CLI help output.                                                                                                        | str              | No       | None     |
| `required` | Whether the option is required. Defaults to `False` (options are typically optional by nature).                                                | bool             | No       | False    |
| `default`  | Default value if option not provided.                                                                                                          | Any              | No       | None     |
| `tags`     | Tag(s) to associate with this option for validation or grouping. Used with the `@tag` decorator.                                               | str or list[str] | No       | None     |

> [!NOTE]
> The parameter name in your function is automatically derived from the long flag by removing `--` and converting hyphens to underscores (e.g., `--config-file` becomes `config_file`).

## Type Inference

The `type` parameter is automatically inferred:

- **Explicit type**: `type=int` uses `int`
- **From default**: `default=8080` infers `int`
- **Neither**: defaults to `str`

```python
@option("--port", default=8080)  # type = int
@option("--name")  # type = str
@option("--value", type=str, default=42)  # type = str (explicit overrides)
```

## Understanding `nargs` and `multiple`

The `nargs` and `multiple` parameters control how option values are structured:

| `nargs`       | `multiple`        | Value Type                  | Example CLI               | Result                 |
| ------------- | ----------------- | --------------------------- | ------------------------- | ---------------------- |
| `1` (default) | `False` (default) | `T`                         | `--name John`             | `"John"`               |
| `2+`          | `False`           | `tuple[T, ...]`             | `--coords 10 20`          | `(10, 20)`             |
| `1`           | `True`            | `tuple[tuple[T, ...], ...]` | `--tag foo --tag bar`     | `(("foo",), ("bar",))` |
| `2+`          | `True`            | `tuple[tuple[T, ...], ...]` | `--point 1 2 --point 3 4` | `((1, 2), (3, 4))`     |

### Type Validation

Validators/transformers must have type hints matching the value structure. Use union types for flexibility:

```python
from click_extended import ChildNode, ProcessContext

class UpperCase(ChildNode):
    def process(
        self,
        value: str | tuple[str, ...] | tuple[tuple[str, ...], ...],
        context: ProcessContext,
    ):
        if not isinstance(value, tuple):
            return value.upper()
        if value and isinstance(value[0], tuple):
            return tuple(tuple(v.upper() for v in group) for group in value)
        return tuple(v.upper() for v in value)
```

Union types can specify different types per structure:

```python
class FlexibleType(ChildNode):
    # Single: str only. Tuples: str|int|float
    def process(
        self,
        value: str | tuple[str | int | float, ...] | tuple[tuple[str | int | float, ...], ...],
        context: ProcessContext,
    ):
        return value
```

**Understanding union type validation:**

The validator checks if any union member matches the parent's configuration:

- **Single value** (`str`): Matches `nargs=1, multiple=False`
- **Flat tuple** (`tuple[T, ...]`): Matches `nargs>1, multiple=False`
- **Nested tuple** (`tuple[tuple[T, ...], ...]`): Matches `multiple=True`

Combine them to support multiple configurations:

```python
# Supports single OR flat tuple
value: str | tuple[str, ...]

# Supports single OR nested tuple
value: str | tuple[tuple[str, ...], ...]

# Supports all three
value: str | tuple[str, ...] | tuple[tuple[str, ...], ...]
```

Each structure can have different type support:

```python
# Single: str only. Tuples: str|int|float
value: str | tuple[str | int | float, ...] | tuple[tuple[str | int | float, ...], ...]
```

Validation occurs at tree construction (before `process()` is executed) and provides clear error messages when types don't match.

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
def build(tag: tuple[tuple[str, ...], ...]):
    for (t,) in tag:
        print(f"Adding tag: {t}")
```

```bash
mycli --tag python --tag cli
# tag = (("python",), ("cli",))
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
def export(
    source: str,
    output: str,
    format: str,
    verbose: bool,
    tag: tuple[tuple[str, ...], ...]
):
    """Export data from source to output directory."""
    if verbose:
        print(f"Exporting {source} to {output} as {format}")
        for (t,) in tag:
            print(f"Tag: {t}")
    print("Export complete!")

if __name__ == "__main__":
    export()
```
