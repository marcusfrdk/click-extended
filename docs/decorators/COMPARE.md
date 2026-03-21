![Banner](../../assets/click-extended-documentation-banner.png)

# Compare Decorators

Compare decorators validate that a numeric, date, or time value satisfies a comparison against a threshold or range. All are `ChildNode` type and must appear after a parent decorator.

## Table of Contents

- [at\_least](#at_least)
- [at\_most](#at_most)
- [between](#between)
- [greater\_than](#greater_than)
- [less\_than](#less_than)

---

## at\_least

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is less than `n` (equivalent to `>= n`).

```python
at_least(n: int) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `n` | `int` | | Minimum allowed value (inclusive) |

```python
@option("count", type=int)
@at_least(1)
```

---

## at\_most

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is greater than `n` (equivalent to `<= n`).

```python
at_most(n: int) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `n` | `int` | | Maximum allowed value (inclusive) |

```python
@option("retries", type=int)
@at_most(10)
```

---

## between

Type: `ChildNode` | Supports: `int`, `float`, `datetime.date`, `datetime.time`, `datetime.datetime`

Raise if the value is outside the specified bounds. Both bounds must be of the same type as the value.

```python
between(
    lower: int | float | date | time | datetime,
    upper: int | float | date | time | datetime,
    inclusive: bool = True,
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `lower` | numeric or datetime-like | | Lower bound |
| `upper` | numeric or datetime-like | | Upper bound |
| `inclusive` | `bool` | `True` | Whether the bounds themselves are valid values |

```python
from datetime import date

@option("age", type=int)
@between(0, 150)

@option("start")
@to_date()
@between(date(2020, 1, 1), date(2030, 12, 31))
```

---

## greater\_than

Type: `ChildNode` | Supports: `int`, `float`, `decimal.Decimal`, `datetime.datetime`, `datetime.date`, `datetime.time`

Raise if the value is not greater than the threshold.

```python
greater_than(
    threshold: int | float | Decimal | datetime | date | time,
    inclusive: bool = False,
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `threshold` | numeric or datetime-like | | Value must be greater than this |
| `inclusive` | `bool` | `False` | If `True`, allow equality (`>=`); if `False`, strict (`>`) |

```python
@option("score", type=float)
@greater_than(0.0)          # must be > 0
@greater_than(0.0, inclusive=True)  # must be >= 0
```

---

## less\_than

Type: `ChildNode` | Supports: `int`, `float`, `decimal.Decimal`, `datetime.datetime`, `datetime.date`, `datetime.time`

Raise if the value is not less than the threshold.

```python
less_than(
    threshold: int | float | Decimal | datetime | date | time,
    inclusive: bool = False,
) -> Decorator
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `threshold` | numeric or datetime-like | | Value must be less than this |
| `inclusive` | `bool` | `False` | If `True`, allow equality (`<=`); if `False`, strict (`<`) |

```python
@option("age", type=int)
@less_than(100)             # must be < 100
@less_than(100, inclusive=True)  # must be <= 100
```
