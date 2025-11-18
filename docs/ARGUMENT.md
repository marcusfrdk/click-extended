![Banner](../assets/click-extended-banner.png)

# Argument

An argument in the command line interface is a positional argument. For this library, an argument is an extension of the `ParentNode`, meaning it injects values into the context.

## Parameters

| Name       | Description                                                                                                                            | Type             | Required | Default |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | ------- |
| `name`     | The name of the argument, converted to snake_case and injected into the function.                                                      | str              | Yes      |         |
| `nargs`    | Number of values to accept. `1` for single value, `N` for exactly N values (returns tuple), `-1` for unlimited values (returns tuple). | int              | No       | 1       |
| `type`     | Type to convert input to. Supports primitives (`int`, `str`, `float`, `bool`) and Click types (`click.Path`, `click.File`, etc.).      | type             | No       | str     |
| `help`     | Help text displayed in CLI help output.                                                                                                | str              | No       | None    |
| `required` | Whether the argument is required. Automatically set to `False` when `default` is provided (except when `default=None`).                | bool             | No       | True    |
| `default`  | Default value if argument not provided. When set (and not `None`), automatically makes the argument optional.                          | Any              | No       | None    |
| `tags`     | Tag(s) to associate with this argument for validation or grouping. Used with the `@tag` decorator.                                     | str or list[str] | No       | None    |

> **Note:** When you provide a `default` value (other than `None`), the argument automatically becomes optional. You don't need to set `required=False` explicitly.

## Examples

### Basic Usage

```python
from click_extended import command, argument

@command()
@argument("filename")
def process(filename: str):
    print(f"Processing: {filename}")
```

### With Type Conversion

```python
from click_extended import command, argument

@command()
@argument("port", type=int)
def start_server(port: int):
    print(f"Starting on port {port}")
```

### Optional Argument

```python
from click_extended import command, argument

@command()
@argument("output", default="output.txt")
def save(output: str):
    print(f"Saving to: {output}")
```

### Multiple Values

```python
from click_extended import command, argument

@command()
@argument("files", nargs=-1)
def batch_process(files: tuple[str, ...]):
    for file in files:
        print(f"Processing: {file}")
```

### Fixed Number of Values

```python
from click_extended import command, argument

@command()
@argument("coords", nargs=3, type=float)
def plot(coords: tuple[float, float, float]):
    x, y, z = coords
    print(f"Point: ({x}, {y}, {z})")
```

### With Tags

```python
from click_extended import command, argument

@command()
@argument("input_file", tags=["io", "required"])
def read(input_file: str):
    print(f"Reading: {input_file}")
```

### Name Transformation

```python
from click_extended import command, argument

@command()
@argument("input-file")  # Becomes "input_file" parameter
def process(input_file: str):
    print(f"Processing: {input_file}")
```

### Using Click Types

```python
from click_extended import command, argument
import click

@command()
@argument("input", type=click.Path(exists=True))
@argument("output", type=click.File("w"), default="output.txt")
def convert(input: str, output):
    with open(input, "r", encoding="utf-8") as f:
        content = f.read()
    output.write(content.upper())
```

## Complete Example

```python
from click_extended import command, argument, option

@command()
@argument("source", type=click.Path(exists=True))
@argument("dest", default="./output")
@option("--verbose", "-v", is_flag=True)
def copy(source: str, dest: str, verbose: bool):
    """Copy a file to a destination."""
    if verbose:
        print(f"Copying {source} to {dest}")

if __name__ == "__main__":
    copy()
```
