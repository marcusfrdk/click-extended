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
| `required` | Whether the argument is required. Automatically set to `False` when `default` is provided (including `None`).                          | bool             | No       | True     |
| `default`  | Default value if argument not provided. When explicitly set, automatically makes the argument optional.                                | Any              | No       | None     |
| `tags`     | Tag(s) to associate with this argument for validation or grouping. Used with the `@tag` decorator.                                     | str or list[str] | No       | None     |

> [!NOTE]
> Providing a `default` (including `None`) automatically makes the argument optional.

## Type Inference

The `type` parameter is automatically inferred:

- **Explicit type**: `type=int` uses `int`
- **From default**: `default=8080` infers `int`
- **Neither**: defaults to `str`

```python
@argument("port", default=8080)  # type = int
@argument("filename")  # type = str
@argument("value", type=str, default=42)  # type = str (explicit overrides)
```

## Understanding `nargs`

The `nargs` parameter controls how many values the argument accepts:

| `nargs`       | Value Type      | Example CLI       | Result                       |
| ------------- | --------------- | ----------------- | ---------------------------- |
| `1` (default) | `T`             | `mycli data.json` | `"data.json"`                |
| `2+`          | `tuple[T, ...]` | `mycli 10 20 30`  | `(10, 20, 30)`               |
| `-1`          | `tuple[T, ...]` | `mycli a b c`     | `("a", "b", "c")` (variadic) |

### Type Validation

Validators/transformers must have type hints matching the value structure. Use union types for flexibility:

```python
from click_extended import ChildNode, ProcessContext

class UpperCase(ChildNode):
    def process(
        self,
        value: str | tuple[str, ...],
        context: ProcessContext,
    ):
        if not isinstance(value, tuple):
            return value.upper()
        return tuple(v.upper() for v in value)
```

Union types can specify different types per structure:

```python
class FlexibleType(ChildNode):
    def process(
        self,
        value: str | tuple[str | int, ...],
        context: ProcessContext,
    ):
        return value
```

#### Understanding union type validation

The validator checks if any union member matches the parent's configuration:

- **Single value** (`str`): Matches `nargs=1`
- **Flat tuple** (`tuple[T, ...]`): Matches `nargs>1` or `nargs=-1`

Combine them to support multiple configurations:

```python
# Supports single OR tuple
value: str | tuple[str, ...]
```

Each structure can have different type support:

```python
# Single: str only. Tuple: str|int|float
value: str | tuple[str | int | float, ...]
```

Validation occurs at tree construction and provides clear error messages when types don't match.

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
