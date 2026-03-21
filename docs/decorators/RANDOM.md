![Banner](../../assets/click-extended-documentation-banner.png)

# Random Decorators

Random decorators generate random values and inject them as parameters. They are all `ParentNode` type, meaning they act as data sources rather than transformers. They do **not** consume any CLI argument.

All random decorators accept a `name` parameter (the parameter name to inject into the function) and an optional `seed` for reproducible results.

## Table of Contents

- [random_bool](#random_bool)
- [random_choice](#random_choice)
- [random_datetime](#random_datetime)
- [random_float](#random_float)
- [random_integer](#random_integer)
- [random_prime](#random_prime)
- [random_string](#random_string)
- [random_uuid](#random_uuid)

---

## random_bool

Generate a random boolean value.

```python
random_bool(
    name: str,
    weight: float = 0.5,
    seed: int | None = None,
) -> Decorator
```

| Parameter | Type          | Default | Description                                          |
| --------- | ------------- | ------- | ---------------------------------------------------- |
| `name`    | `str`         |         | Parameter name to inject into the function           |
| `weight`  | `float`       | `0.5`   | Probability of `True` (0.0 to 1.0). Clamped to range |
| `seed`    | `int \| None` | `None`  | Optional seed for reproducibility                    |

**Returns:** `bool`

```python
from click_extended import command
from click_extended.decorators import random_bool

@command()
@random_bool("flag")
def cmd(flag: bool) -> None:
    print(f"Flag: {flag}")

# Always True:
@random_bool("always_true", weight=1.0)
```

---

## random_choice

Select a random element from a sequence.

```python
random_choice(
    name: str,
    iterable: Sequence[str | int | float | bool],
    weights: Sequence[float] | None = None,
    seed: int | None = None,
) -> Decorator
```

| Parameter  | Type                      | Default | Description                                                   |
| ---------- | ------------------------- | ------- | ------------------------------------------------------------- |
| `name`     | `str`                     |         | Parameter name                                                |
| `iterable` | `Sequence`                |         | The sequence to choose from                                   |
| `weights`  | `Sequence[float] \| None` | `None`  | Optional weights for each element (same length as `iterable`) |
| `seed`     | `int \| None`             | `None`  | Optional seed for reproducibility                             |

**Returns:** The type of the selected element.

```python
from click_extended import command
from click_extended.decorators import random_choice

@command()
@random_choice("color", ["red", "green", "blue"])
def cmd(color: str) -> None:
    print(f"Color: {color}")

# Weighted choice:
@random_choice("env", ["prod", "staging", "dev"], weights=[1, 2, 7])
```

---

## random_datetime

Generate a random datetime within a range.

```python
random_datetime(
    name: str,
    start_date: str | datetime,
    end_date: str | datetime,
    timezone: str | None = None,
    seed: int | None = None,
) -> Decorator
```

| Parameter    | Type              | Default | Description                                                                                                                                            |
| ------------ | ----------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`       | `str`             |         | Parameter name                                                                                                                                         |
| `start_date` | `str \| datetime` |         | Start of the range. String formats: `"YYYY-MM-DD HH:MM:SS"`, `"YYYY-MM-DD"`, `"HH:MM:SS"`, or keywords `"now"`, `"today"`, `"tomorrow"`, `"yesterday"` |
| `end_date`   | `str \| datetime` |         | End of the range (same formats as `start_date`)                                                                                                        |
| `timezone`   | `str \| None`     | `None`  | Timezone name (e.g., `"UTC"`, `"Europe/London"`). If `None`, result is timezone-naive                                                                  |
| `seed`       | `int \| None`     | `None`  | Optional seed for reproducibility                                                                                                                      |

**Returns:** `datetime.datetime`

```python
from click_extended import command
from click_extended.decorators import random_datetime

@command()
@random_datetime("event_time", "2024-01-01", "2024-12-31", timezone="UTC")
def cmd(event_time) -> None:
    print(f"Event at: {event_time}")
```

---

## random_float

Generate a random floating point number.

```python
random_float(
    name: str,
    min_value: float = 0.0,
    max_value: float = 1.0,
    decimals: int = 3,
    seed: int | None = None,
) -> Decorator
```

| Parameter   | Type          | Default | Description                          |
| ----------- | ------------- | ------- | ------------------------------------ |
| `name`      | `str`         |         | Parameter name                       |
| `min_value` | `float`       | `0.0`   | Lower bound (inclusive)              |
| `max_value` | `float`       | `1.0`   | Upper bound (inclusive)              |
| `decimals`  | `int`         | `3`     | Number of decimal places to round to |
| `seed`      | `int \| None` | `None`  | Optional seed for reproducibility    |

**Returns:** `float`

```python
@command()
@random_float("rate", min_value=0.01, max_value=0.99, decimals=2)
def cmd(rate: float) -> None:
    print(f"Rate: {rate}")
```

---

## random_integer

Generate a random integer.

```python
random_integer(
    name: str,
    min_value: int = 0,
    max_value: int = 100,
    seed: int | None = None,
) -> Decorator
```

| Parameter   | Type          | Default | Description                       |
| ----------- | ------------- | ------- | --------------------------------- |
| `name`      | `str`         |         | Parameter name                    |
| `min_value` | `int`         | `0`     | Lower bound (inclusive)           |
| `max_value` | `int`         | `100`   | Upper bound (inclusive)           |
| `seed`      | `int \| None` | `None`  | Optional seed for reproducibility |

**Returns:** `int`

```python
@command()
@random_integer("port", min_value=1024, max_value=65535)
def cmd(port: int) -> None:
    print(f"Port: {port}")
```

---

## random_prime

Generate a random prime number from the first `k` primes.

```python
random_prime(
    name: str,
    k: int = 100,
    seed: int | None = None,
) -> Decorator
```

| Parameter | Type          | Default | Description                                                                               |
| --------- | ------------- | ------- | ----------------------------------------------------------------------------------------- |
| `name`    | `str`         |         | Parameter name                                                                            |
| `k`       | `int`         | `100`   | Pool size: selects from the first `k` prime numbers. Keep small to avoid slow computation |
| `seed`    | `int \| None` | `None`  | Optional seed for reproducibility                                                         |

**Returns:** `int`

```python
@command()
@random_prime("p", k=50)
def cmd(p: int) -> None:
    print(f"Prime: {p}")
```

---

## random_string

Generate a random string.

```python
random_string(
    name: str,
    length: int = 8,
    lowercase: bool = True,
    uppercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
    seed: int | None = None,
) -> Decorator
```

| Parameter   | Type          | Default | Description                       |
| ----------- | ------------- | ------- | --------------------------------- |
| `name`      | `str`         |         | Parameter name                    |
| `length`    | `int`         | `8`     | Length of the generated string    |
| `lowercase` | `bool`        | `True`  | Include lowercase letters         |
| `uppercase` | `bool`        | `True`  | Include uppercase letters         |
| `numbers`   | `bool`        | `True`  | Include digit characters          |
| `symbols`   | `bool`        | `True`  | Include symbol characters         |
| `seed`      | `int \| None` | `None`  | Optional seed for reproducibility |

**Returns:** `str`

```python
@command()
@random_string("token", length=32, symbols=False)
def cmd(token: str) -> None:
    print(f"Token: {token}")
```

---

## random_uuid

Generate a random UUID.

```python
random_uuid(
    name: str,
    version: Literal[1, 3, 4, 5] = 4,
    namespace: UUID | str | None = None,
    uuid_name: str | None = None,
    seed: int | None = None,
) -> Decorator
```

| Parameter   | Type                  | Default | Description                                                                              |
| ----------- | --------------------- | ------- | ---------------------------------------------------------------------------------------- |
| `name`      | `str`                 |         | Parameter name                                                                           |
| `version`   | `int`                 | `4`     | UUID version: `1` (time-based), `3` (MD5/namespace), `4` (random), `5` (SHA-1/namespace) |
| `namespace` | `UUID \| str \| None` | `None`  | Namespace UUID for versions 3 and 5 (required for those versions)                        |
| `uuid_name` | `str \| None`         | `None`  | Name string for versions 3 and 5 (required for those versions)                           |
| `seed`      | `int \| None`         | `None`  | Optional seed for reproducibility (version 4 only)                                       |

**Returns:** `uuid.UUID`

```python
from uuid import NAMESPACE_DNS
from click_extended import command
from click_extended.decorators import random_uuid

# Random UUID (v4, most common)
@command()
@random_uuid("id")
def cmd(id) -> None:
    print(f"ID: {id}")

# Deterministic UUID (v5)
@command()
@random_uuid("id", version=5, namespace=NAMESPACE_DNS, uuid_name="example.com")
def cmd(id) -> None:
    print(f"ID: {id}")
```
