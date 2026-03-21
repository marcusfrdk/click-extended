![Banner](../../assets/click-extended-documentation-banner.png)

# Load Decorators

Load decorators read a file and return its parsed contents. They are `ChildNode` type and must appear **after** a path-producing decorator such as `@to_path`, `@to_file`, or `@to_directory` (which converts the raw string argument into a `pathlib.Path`).

## Table of Contents

- [load\_csv](#load_csv)
- [load\_json](#load_json)
- [load\_toml](#load_toml)
- [load\_yaml](#load_yaml)

---

## load\_csv

Type: `ChildNode` | Supports: `pathlib.Path`

Load the contents of a CSV file.

```python
load_csv(
    dialect: Literal["excel", "excel-tab", "unix"] | None = None,
    delimiter: str | None = None,
    has_header: bool = True,
    as_dict: bool = True,
    encoding: str = "utf-8",
    skip_empty: bool = True,
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `dialect` | `str \| None` | `None` | CSV dialect: `"excel"`, `"excel-tab"`, or `"unix"`. `None` uses default settings |
| `delimiter` | `str \| None` | `None` | Field separator character (e.g., `","`, `"\t"`) |
| `has_header` | `bool` | `True` | Whether the first row is a header. Only used when `as_dict=False` |
| `as_dict` | `bool` | `True` | When `True`, returns list of dicts (via `csv.DictReader`); when `False`, returns list of lists |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `skip_empty` | `bool` | `True` | Whether to skip empty rows |

**Returns:** `list[dict[str, str]]` when `as_dict=True`, `list[list[str]]` when `as_dict=False`

```python
from typing import Any
import pandas as pd
from click_extended import command, argument
from click_extended.decorators import to_path, load_csv

@command()
@argument("file", param="data")
@to_path(extensions=["csv"], exists=True)
@load_csv()
def my_command(data: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(data)
    print(df.head())
```

---

## load\_json

Type: `ChildNode` | Supports: `pathlib.Path`

Load the contents of a JSON file.

```python
load_json(
    encoding: str = "utf-8",
    strict: bool = True,
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `strict` | `bool` | `True` | When `True`, floats are parsed as `Decimal` for precision; when `False`, uses standard `float` |

**Returns:** The parsed Python object (typically `dict` or `list`).

```python
from click_extended import command, argument
from click_extended.decorators import to_file, load_json

@command()
@argument("config")
@to_file(extensions=["json"])
@load_json()
def my_command(config: dict) -> None:
    print(config["version"])
```

---

## load\_toml

Type: `ChildNode` | Supports: `pathlib.Path`

Load the contents of a TOML file.

```python
load_toml() -> Decorator
```

**Returns:** The parsed Python object (typically `dict`).

```python
from click_extended import command, argument
from click_extended.decorators import to_file, load_toml

@command()
@argument("config")
@to_file(extensions=["toml"])
@load_toml()
def my_command(config: dict) -> None:
    print(config)
```

---

## load\_yaml

Type: `ChildNode` | Supports: `pathlib.Path`

Load the contents of a YAML file.

```python
load_yaml(
    encoding: str = "utf-8",
    loader: Literal["safe", "unsafe", "full"] = "safe",
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `loader` | `str` | `"safe"` | YAML loader: `"safe"` (recommended for untrusted input), `"full"`, or `"unsafe"` |

**Returns:** The parsed Python object (typically `dict` or `list`).

```python
from click_extended import command, argument
from click_extended.decorators import to_file, load_yaml

@command()
@argument("config")
@to_file(extensions=["yaml", "yml"])
@load_yaml()
def my_command(config: dict) -> None:
    print(config)
```
