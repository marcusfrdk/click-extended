![Banner](../../assets/click-extended-documentation-banner.png)

# Math Decorators

Math decorators apply arithmetic or mathematical transformations to numeric values. All are `ChildNode` type and must appear after a parent decorator.

## Table of Contents

- [absolute](#absolute)
- [add](#add)
- [ceil](#ceil)
- [clamp](#clamp)
- [divide](#divide)
- [floor](#floor)
- [maximum](#maximum)
- [minimum](#minimum)
- [modulo](#modulo)
- [multiply](#multiply)
- [normalize](#normalize)
- [power](#power)
- [rounded](#rounded)
- [sqrt](#sqrt)
- [subtract](#subtract)
- [to_percent](#to_percent)

---

## absolute

Type: `ChildNode` | Supports: `int`, `float`

Return the absolute value.

```python
absolute() -> Decorator
```

```python
@option("offset", type=float)
@absolute()
# -3.5 -> 3.5
```

---

## add

Type: `ChildNode` | Supports: `int`, `float`, `str`

Add `n` to the value. For strings, concatenates `n` to the end.

```python
add(n: int | float | str) -> Decorator
```

| Parameter | Type                  | Default | Description                |
| --------- | --------------------- | ------- | -------------------------- |
| `n`       | `int \| float \| str` |         | Value to add / concatenate |

```python
@option("count", type=int)
@add(1)
# 5 -> 6
```

---

## ceil

Type: `ChildNode` | Supports: `int`, `float`

Round up to the nearest integer.

```python
ceil() -> Decorator
```

```python
@option("value", type=float)
@ceil()
# 2.3 -> 3
```

---

## clamp

Type: `ChildNode` | Supports: `int`, `float`

Clamp the value between an optional minimum and maximum. Values outside the range are snapped to the nearest bound.

```python
clamp(
    min_val: int | float | None = None,
    max_val: int | float | None = None,
) -> Decorator
```

| Parameter | Type                   | Default | Description             |
| --------- | ---------------------- | ------- | ----------------------- |
| `min_val` | `int \| float \| None` | `None`  | Lower bound (inclusive) |
| `max_val` | `int \| float \| None` | `None`  | Upper bound (inclusive) |

```python
@option("volume", type=int)
@clamp(min_val=0, max_val=100)
# 150 -> 100, -5 -> 0
```

---

## divide

Type: `ChildNode` | Supports: `int`, `float`

Divide the value by `n`.

```python
divide(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description                |
| --------- | -------------- | ------- | -------------------------- |
| `n`       | `int \| float` |         | Divisor (must not be zero) |

```python
@option("bytes", type=int)
@divide(1024)
# Convert bytes to kilobytes
```

---

## floor

Type: `ChildNode` | Supports: `int`, `float`

Round down to the nearest integer.

```python
floor() -> Decorator
```

```python
@option("value", type=float)
@floor()
# 2.9 -> 2
```

---

## maximum

Type: `ChildNode` | Supports: `int`, `float`

Cap the value at a maximum. If the value exceeds `max_val`, return `max_val`.

```python
maximum(max_val: int | float) -> Decorator
```

| Parameter | Type           | Default | Description       |
| --------- | -------------- | ------- | ----------------- |
| `max_val` | `int \| float` |         | The ceiling value |

```python
@option("speed", type=int)
@maximum(300)
```

---

## minimum

Type: `ChildNode` | Supports: `int`, `float`

Floor the value at a minimum. If the value is below `min_val`, return `min_val`.

```python
minimum(min_val: int | float) -> Decorator
```

| Parameter | Type           | Default | Description     |
| --------- | -------------- | ------- | --------------- |
| `min_val` | `int \| float` |         | The floor value |

```python
@option("count", type=int)
@minimum(0)
```

---

## modulo

Type: `ChildNode` | Supports: `int`, `float`

Return `value % n`.

```python
modulo(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description |
| --------- | -------------- | ------- | ----------- |
| `n`       | `int \| float` |         | The modulus |

```python
@option("index", type=int)
@modulo(10)
# 13 -> 3
```

---

## multiply

Type: `ChildNode` | Supports: `int`, `float`

Multiply the value by `n`.

```python
multiply(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description |
| --------- | -------------- | ------- | ----------- |
| `n`       | `int \| float` |         | Multiplier  |

```python
@option("price", type=float)
@multiply(1.25)
# Apply 25% markup
```

---

## normalize

Type: `ChildNode` | Supports: `int`, `float`

Normalize the value from `[min_val, max_val]` to `[new_min, new_max]`. If `new_min` and `new_max` are not provided, normalizes to `[0.0, 1.0]`.

```python
normalize(
    min_val: float,
    max_val: float,
    new_min: float | None = None,
    new_max: float | None = None,
) -> Decorator
```

| Parameter | Type            | Default | Description                                     |
| --------- | --------------- | ------- | ----------------------------------------------- |
| `min_val` | `float`         |         | Minimum of the input range                      |
| `max_val` | `float`         |         | Maximum of the input range                      |
| `new_min` | `float \| None` | `None`  | Minimum of the output range (defaults to `0.0`) |
| `new_max` | `float \| None` | `None`  | Maximum of the output range (defaults to `1.0`) |

```python
@option("score", type=float)
@normalize(0, 100)
# 75 -> 0.75

@option("score", type=float)
@normalize(0, 100, new_min=0, new_max=10)
# 75 -> 7.5
```

---

## power

Type: `ChildNode` | Supports: `int`, `float`

Raise the value to the power `n`.

```python
power(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description  |
| --------- | -------------- | ------- | ------------ |
| `n`       | `int \| float` |         | The exponent |

```python
@option("side", type=float)
@power(2)
# Compute area of a square: 5 -> 25
```

---

## rounded

Type: `ChildNode` | Supports: `int`, `float`

Round to `digits` decimal places.

```python
rounded(digits: int = 0) -> Decorator
```

| Parameter | Type  | Default | Description              |
| --------- | ----- | ------- | ------------------------ |
| `digits`  | `int` | `0`     | Number of decimal places |

```python
@option("rate", type=float)
@rounded(2)
# 3.14159 -> 3.14
```

---

## sqrt

Type: `ChildNode` | Supports: `int`, `float`

Return the square root of the value.

```python
sqrt() -> Decorator
```

```python
@option("area", type=float)
@sqrt()
# 25.0 -> 5.0
```

---

## subtract

Type: `ChildNode` | Supports: `int`, `float`

Subtract `n` from the value.

```python
subtract(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description       |
| --------- | -------------- | ------- | ----------------- |
| `n`       | `int \| float` |         | Value to subtract |

```python
@option("index", type=int)
@subtract(1)
# Convert 1-based index to 0-based: 1 -> 0
```

---

## to_percent

Type: `ChildNode` | Supports: `int`, `float`

Multiply the value by 100 (convert a ratio to a percentage).

```python
to_percent() -> Decorator
```

```python
@option("ratio", type=float)
@to_percent()
# 0.75 -> 75.0
```
