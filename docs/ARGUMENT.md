![Banner](../assets/click-extended-documentation-banner.png)

# Argument

An argument in the command line interface is a positional argument. For this library, an argument is an extension of the `ParentNode`, meaning it injects values into the context.

## Parameters

| Name       | Description                                                                                                                            | Type             | Required | Default  |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | -------- |
| `name`     | The name of the argument, converted to snake_case and injected into the function.                                                      | str              | Yes      |          |
| `nargs`    | Number of values to accept. `1` for single value, `N` for exactly N values (returns tuple), `-1` for unlimited values (returns tuple). | int              | No       | 1        |
| `type`     | Type to convert input to. If not specified, defaults to `str` or is inferred from `default`. Supports primitives and Click types.      | type             | No       | Inferred |
| `help`     | Help text displayed in CLI help output.                                                                                                | str              | No       | None     |
| `required` | Whether the argument is required. Automatically set to `False` when `default` is provided (except when `default=None`).                | bool             | No       | True     |
| `default`  | Default value if argument not provided. When set (and not `None`), automatically makes the argument optional.                          | Any              | No       | None     |
| `tags`     | Tag(s) to associate with this argument for validation or grouping. Used with the `@tag` decorator.                                     | str or list[str] | No       | None     |

> [!NOTE]
> When you provide a `default` value (other than `None`), the argument automatically becomes optional. You don't need to set `required=False` explicitly.

## Type Inference

The `type` parameter supports automatic inference based on the following rules:

1. **Explicit type specified**: Uses the specified type (e.g., `type=int`)
2. **Default value provided**: Infers type from the default value (e.g., `default=8080` → `int`)
3. **Neither specified**: Defaults to `str`

### Examples

```python
# Type inferred as int from default
@argument("port", default=8080)  # type = int

# Type inferred as float from default
@argument("ratio", default=2.5)  # type = float

# Type defaults to str (no default, no type)
@argument("filename")  # type = str

# Explicit type overrides inference
@argument("value", type=str, default=42)  # type = str, not int
```

This inference system helps reduce boilerplate while maintaining type safety and enabling proper validation.

## Type Inference and Validators

Type inference integrates seamlessly with the validation system. When using validators that specify supported types (like `@is_positive()` which supports `int` and `float`), the inferred type is automatically checked:

```python
from click_extended import command, argument
from click_extended.validation import is_positive

# Working
@command()
@argument("count", default=10)
@is_positive()
def process(count: int):
    print(f"Processing {count} items")

@command()
@argument("port", type=int)
@is_positive()
def serve(port: int):
    print(f"Serving on port {port}")

# Raises exception
@command()
@argument("filename")  # Type inferred as str
@is_positive()  # Error: is_positive only supports int and float
def load(filename: str):
    print(f"Loading {filename}")
```

This type checking happens at validation time, providing clear error messages when validators are applied to incompatible types.

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
