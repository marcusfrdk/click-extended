![Banner](../assets/click-extended-documentation-banner.png)

# Argument

An argument in the command line interface is a positional argument and is an extension of the `ParentNode`, meaning it injects values into the context.

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

## Type Inference

The type of the argument can be set in several ways. By default, the type of an argument is `str`.

```python
@argument("filename") # Defaults to type=str
```

However, if the `type` parameter is not set and default is, the type of the `default` parameter if inferred. In this case, it's an `int`.

```python
@argument("port", default=8080)
```

If the `type` parameter is set, that takes precedence over both.

```python
@argument("value", type=str, default=42)
```

## Number of Arguments

The `nargs` parameter controls how many values the argument accepts:

| `nargs`     | Type          | Input                   | Output                |
| ----------- | ------------- | ----------------------- | --------------------- |
| 1 (default) | T             | cli 1                   | 1                     |
| n           | tuple[T, ...] | cli 1, 2, ..., n        | (1, 2, ..., n)        |
| -1          | tuple[T, ...] | cli 1, 2, ..., $\infty$ | (1, 2, ..., $\infty$) |

## Examples

### Basic Usage

This is the most basic example. In this example, `filename` is a required string (defualt type) and will be injected into the `**kwargs` parameter as `filename: str`.

```python
from click_extended import command, argument

@command()
@argument("filename")
def process(filename: str):
    print(f"Processing: {filename}")
```

### With Type Conversion

When setting a type, `Click` will automatically convert the type as arguments are required by default, so you can safely assume the type for the parameter. If `required=False`, the type should be `int | None` as `None` is a possible value.

```python
from click_extended import command, argument

@command()
@argument("port", type=int)
def start_server(port: int):
    print(f"Starting on port {port}")
```

### Optional Argument

There are two ways of marking an argument optional, either by setting `required=False` or by setting a default value as is done in this example. As the type is not set, the type of the `output` parameter is a `str`.

```python
from click_extended import command, argument

@command()
@argument("output", default="output.txt")
def save(output: str):
    print(f"Saving to: {output}")
```

### Multiple Values

As mentioned in the [number of arguments](#number-of-arguments) section, the `nargs` parameter accepts and positive number (or `-1` for any number). In this example, we accept any number of positional arguments, which get injected as a tuple of strings (as the type is `str`).

```python
from click_extended import command, argument

@command()
@argument("files", nargs=-1)
def batch_process(files: tuple[str, ...]):
    for file in files:
        print(f"Processing: {file}")
```

### Fixed Number of Values

If `nargs` is set to a fixed scalar, the argument requires that number of arguments to be provided. As for the type, it's preferred to type if as `tuple[float, float, float]`, but Python would also accept either `tuple[float]` or `tuple[float, ...]` as well.

```python
from click_extended import command, argument

@command()
@argument("coords", nargs=3, type=float)
def plot(coords: tuple[float, float, float]):
    x, y, z = coords
    print(f"Point: ({x}, {y}, {z})")
```

### With Tags

Tags are a way of grouping multiple [parent nodes](./PARENT_NODE.md) together to perform various operations in bulk, such as transformation, validation or even exclusivity checks. You can read mode about tags in the [tag documentation](./TAG.md).

```python
from click_extended import command, argument

@command()
@argument("input_file", tags=["io", "required"])
def read(input_file: str):
    print(f"Reading: {input_file}")
```

### Name Transformation

The name of an argument can be anything, but under the hood, it is converted to `snake_case` to conform to a more pythonic format. So in this example, the argument is injected as `input_file` even though the name is `input-file`.

Arguments can be named in whatever format you want, but it is stored and injected as `snake_case`, and `click` uses `SCREAMING_SNAKE_CASE` in the help menu.

```python
from click_extended import command, argument

@command()
@argument("input-file")  # Becomes "input_file" parameter
def process(input_file: str):
    print(f"Processing: {input_file}")
```

### Using Click Types

Out of the box, the types `click` provide are supported in `click-extended`.

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
