![Banner](../../assets/click-extended-documentation-banner.png)

# Check Decorators

Check decorators validate a value or enforce inter-parameter constraints. Unless noted as `ValidationNode`, they are `ChildNode` types and must appear after a parent decorator (`@argument`, `@option`, `@env`, etc.).

## Table of Contents

- [conflicts](#conflicts)
- [contains](#contains)
- [dependencies](#dependencies)
- [divisible_by](#divisible_by)
- [ends_with](#ends_with)
- [exclusive](#exclusive)
- [falsy](#falsy)
- [is_email](#is_email)
- [is_hex_color](#is_hex_color)
- [is_hostname](#is_hostname)
- [is_ipv4](#is_ipv4)
- [is_ipv6](#is_ipv6)
- [is_json](#is_json)
- [is_mac_address](#is_mac_address)
- [is_negative](#is_negative)
- [is_non_zero](#is_non_zero)
- [is_numeric](#is_numeric)
- [is_port](#is_port)
- [is_positive](#is_positive)
- [is_url](#is_url)
- [is_uuid](#is_uuid)
- [length](#length)
- [not_empty](#not_empty)
- [regex](#regex)
- [requires](#requires)
- [starts_with](#starts_with)
- [truthy](#truthy)

---

## conflicts

Type: `ChildNode` | Supports: `any`, `tag`

Raise if the decorated parameter is provided at the same time as any of the named conflicting parameters.

```python
conflicts(*names: str) -> Decorator
```

| Parameter | Type  | Default | Description                                     |
| --------- | ----- | ------- | ----------------------------------------------- |
| `*names`  | `str` |         | Names of parameters that conflict with this one |

```python
@command()
@option("username")
@conflicts("api_key")
@option("api_key")
def login(username: str, api_key: str) -> None:
    # --username and --api-key cannot be used together
    pass
```

---

## contains

Type: `ChildNode` | Supports: `str`

Check that the string contains one or more substrings.

```python
contains(*text: str, all: bool = False) -> Decorator
```

| Parameter | Type   | Default | Description                                                                  |
| --------- | ------ | ------- | ---------------------------------------------------------------------------- |
| `*text`   | `str`  |         | Substrings to check for                                                      |
| `all`     | `bool` | `False` | If `True`, all substrings must be present; if `False`, any one is sufficient |

```python
@argument("message")
@contains("hello", "world")        # at least one must be present
@contains("hello", "world", all=True)  # both must be present
```

---

## dependencies

Type: `ValidationNode`

Enforce mutual dependencies between parameters: if any parameter in the group is provided, all must be provided.

```python
dependencies(*names: str) -> Decorator
```

| Parameter | Type  | Default | Description                                    |
| --------- | ----- | ------- | ---------------------------------------------- |
| `*names`  | `str` |         | Parameter or tag names in the dependency group |

```python
@command()
@option("username")
@option("password")
@dependencies("username", "password")
def login(username: str, password: str) -> None:
    # If either --username or --password is provided, the other is required too
    pass
```

---

## divisible_by

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is not divisible by `n`.

```python
divisible_by(n: int | float) -> Decorator
```

| Parameter | Type           | Default | Description |
| --------- | -------------- | ------- | ----------- |
| `n`       | `int \| float` |         | The divisor |

```python
@option("count", type=int)
@divisible_by(3)
```

---

## ends_with

Type: `ChildNode` | Supports: `str`

Check that the string ends with one of the provided suffixes.

```python
ends_with(*text: str | re.Pattern[str]) -> Decorator
```

| Parameter | Type                | Default | Description                     |
| --------- | ------------------- | ------- | ------------------------------- |
| `*text`   | `str \| re.Pattern` |         | Suffix(es) or patterns to check |

```python
@argument("filename")
@ends_with(".py", ".pyx")
```

---

## exclusive

Type: `ValidationNode`

Enforce mutual exclusivity: at most one of the named parameters may be provided.

```python
exclusive(*names: str) -> Decorator
```

| Parameter | Type  | Default | Description                            |
| --------- | ----- | ------- | -------------------------------------- |
| `*names`  | `str` |         | Names of mutually exclusive parameters |

```python
@command()
@option("json", is_flag=True)
@option("xml", is_flag=True)
@exclusive("json", "xml")
def export(json: bool, xml: bool) -> None:
    pass
```

---

## falsy

Type: `ChildNode` | Supports: `any`

Raise if the value is truthy (i.e., assert the value is falsy).

```python
falsy() -> Decorator
```

---

## is_email

Type: `ChildNode` | Supports: `str`

Validate that the string is a well-formed email address.

```python
is_email() -> Decorator
```

```python
@option("email")
@is_email()
```

---

## is_hex_color

Type: `ChildNode` | Supports: `str`

Validate that the string is a hex color code (e.g., `#fff`, `#aabbcc`).

```python
is_hex_color() -> Decorator
```

---

## is_hostname

Type: `ChildNode` | Supports: `str`

Validate that the string is a valid hostname.

```python
is_hostname() -> Decorator
```

---

## is_ipv4

Type: `ChildNode` | Supports: `str`

Validate that the string is a valid IPv4 address.

```python
is_ipv4() -> Decorator
```

---

## is_ipv6

Type: `ChildNode` | Supports: `str`

Validate that the string is a valid IPv6 address.

```python
is_ipv6() -> Decorator
```

---

## is_json

Type: `ChildNode` | Supports: `str`

Validate that the string is valid JSON.

```python
is_json() -> Decorator
```

---

## is_mac_address

Type: `ChildNode` | Supports: `str`

Validate that the string is a valid MAC address.

```python
is_mac_address() -> Decorator
```

---

## is_negative

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is not strictly negative (i.e., value must be < 0).

```python
is_negative() -> Decorator
```

---

## is_non_zero

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is zero.

```python
is_non_zero() -> Decorator
```

---

## is_numeric

Type: `ChildNode` | Supports: `str`

Raise if the string cannot be interpreted as a number.

```python
is_numeric() -> Decorator
```

---

## is_port

Type: `ChildNode` | Supports: `int`

Validate that the integer is a valid port number (1–65535).

```python
is_port() -> Decorator
```

---

## is_positive

Type: `ChildNode` | Supports: `int`, `float`

Raise if the value is not strictly positive (i.e., value must be > 0).

```python
is_positive() -> Decorator
```

---

## is_url

Type: `ChildNode` | Supports: `str`

Validate that the string is a well-formed URL.

```python
is_url(
    schemes: list[str] | None = None,
    require_tld: bool = True,
) -> Decorator
```

| Parameter     | Type                | Default | Description                                                                |
| ------------- | ------------------- | ------- | -------------------------------------------------------------------------- |
| `schemes`     | `list[str] \| None` | `None`  | Allowed URL schemes (e.g., `["http", "https"]`). `None` allows all schemes |
| `require_tld` | `bool`              | `True`  | Whether a top-level domain is required                                     |

```python
@argument("url")
@is_url(schemes=["https"])
```

---

## is_uuid

Type: `ChildNode` | Supports: `str`

Validate that the string is a valid UUID.

```python
is_uuid() -> Decorator
```

---

## length

Type: `ChildNode` | Supports: `str`

Check that the string length is within bounds.

```python
length(min: int | None = None, max: int | None = None) -> Decorator
```

| Parameter | Type          | Default | Description                |
| --------- | ------------- | ------- | -------------------------- |
| `min`     | `int \| None` | `None`  | Minimum length (inclusive) |
| `max`     | `int \| None` | `None`  | Maximum length (inclusive) |

At least one of `min` or `max` must be specified.

```python
@option("password")
@length(min=8, max=64)
```

---

## not_empty

Type: `ChildNode` | Supports: `str`

Raise if the string is empty.

```python
not_empty() -> Decorator
```

---

## regex

Type: `ChildNode` | Supports: `str`

Validate that the string matches one or more regular expression patterns.

```python
regex(*patterns: str | re.Pattern[str], flags: int = 0) -> Decorator
```

| Parameter   | Type                | Default | Description                          |
| ----------- | ------------------- | ------- | ------------------------------------ |
| `*patterns` | `str \| re.Pattern` |         | One or more patterns; all must match |
| `flags`     | `int`               | `0`     | `re` flags (e.g., `re.IGNORECASE`)   |

```python
@argument("code")
@regex(r"^[A-Z]{3}\d{3}$")
```

---

## requires

Type: `ChildNode` | Supports: `any`, `tag`

When the decorated parameter is provided, raise if any of the named required parameters are missing.

```python
requires(*names: str, require_all_tagged: bool = True) -> Decorator
```

| Parameter            | Type   | Default | Description                                                                                                              |
| -------------------- | ------ | ------- | ------------------------------------------------------------------------------------------------------------------------ |
| `*names`             | `str`  |         | Parameter or tag names that must be provided                                                                             |
| `require_all_tagged` | `bool` | `True`  | For tag names: if `True`, any provided tag member triggers the check; if `False`, all tag members must be provided first |

```python
@command()
@option("output")
@requires("input")
@option("input")
def process(input: str, output: str) -> None:
    # --output requires --input
    pass
```

---

## starts_with

Type: `ChildNode` | Supports: `str`

Check that the string starts with one of the provided prefixes.

```python
starts_with(*text: str | re.Pattern[str]) -> Decorator
```

| Parameter | Type                | Default | Description                     |
| --------- | ------------------- | ------- | ------------------------------- |
| `*text`   | `str \| re.Pattern` |         | Prefix(es) or patterns to check |

```python
@argument("path")
@starts_with("/home", "/tmp")
```

---

## truthy

Type: `ChildNode` | Supports: `any`

Raise if the value is falsy (i.e., assert the value is truthy).

```python
truthy() -> Decorator
```
