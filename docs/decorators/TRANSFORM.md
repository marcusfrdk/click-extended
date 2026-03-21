![Banner](../../assets/click-extended-documentation-banner.png)

# Transform Decorators

Transform decorators modify or convert a value, changing its case, format, type, or structure. All are `ChildNode` type and must appear after a parent decorator.

## Table of Contents

- [add_prefix](#add_prefix)
- [add_suffix](#add_suffix)
- [apply](#apply)
- [basename](#basename)
- [dirname](#dirname)
- [expand_vars](#expand_vars)
- [lstrip / rstrip / strip](#lstrip--rstrip--strip)
- [remove_prefix](#remove_prefix)
- [remove_suffix](#remove_suffix)
- [replace](#replace)
- [slugify](#slugify)
- [split](#split)
- [to_case](#to_case)
- [to_date](#to_date)
- [to_datetime](#to_datetime)
- [to_decimal](#to_decimal)
- [to_directory](#to_directory)
- [to_file](#to_file)
- [to_path](#to_path)
- [to_string](#to_string)
- [to_symlink](#to_symlink)
- [to_time](#to_time)
- [to_timestamp](#to_timestamp)
- [truncate](#truncate)

---

## add_prefix

Type: `ChildNode` | Supports: `str`

Prepend a prefix to the string.

```python
add_prefix(prefix: str, skip: bool = True, case_sensitive: bool = False) -> Decorator
```

| Parameter        | Type   | Default | Description                                                            |
| ---------------- | ------ | ------- | ---------------------------------------------------------------------- |
| `prefix`         | `str`  |         | The prefix to add                                                      |
| `skip`           | `bool` | `True`  | If `True`, skip adding the prefix if the string already starts with it |
| `case_sensitive` | `bool` | `False` | Whether the "already starts with" check is case-sensitive              |

```python
@argument("path")
@add_prefix("/home/")
# "user" -> "/home/user", "/home/user" -> "/home/user" (unchanged)
```

---

## add_suffix

Type: `ChildNode` | Supports: `str`

Append a suffix to the string.

```python
add_suffix(suffix: str, skip: bool = True, case_sensitive: bool = False) -> Decorator
```

| Parameter        | Type   | Default | Description                                                          |
| ---------------- | ------ | ------- | -------------------------------------------------------------------- |
| `suffix`         | `str`  |         | The suffix to add                                                    |
| `skip`           | `bool` | `True`  | If `True`, skip adding the suffix if the string already ends with it |
| `case_sensitive` | `bool` | `False` | Whether the "already ends with" check is case-sensitive              |

```python
@argument("filename")
@add_suffix(".py")
# "module" -> "module.py", "module.py" -> "module.py" (unchanged)
```

---

## apply

Type: `ChildNode` | Supports: `any`

Apply an arbitrary function to the value.

```python
apply(fn: Callable[[Any], Any]) -> Decorator
```

| Parameter | Type       | Default | Description                    |
| --------- | ---------- | ------- | ------------------------------ |
| `fn`      | `Callable` |         | Function to apply to the value |

```python
@argument("name")
@apply(str.title)
@apply(lambda x: x.replace("-", "_"))
```

---

## basename

Type: `ChildNode` | Supports: `str`, `pathlib.Path`

Return the final component of a path (equivalent to `os.path.basename`).

```python
basename() -> Decorator
```

```python
@argument("path")
@basename()
# "/home/user/file.py" -> "file.py"
```

---

## dirname

Type: `ChildNode` | Supports: `str`, `pathlib.Path`

Return the directory component of a path (equivalent to `os.path.dirname`).

```python
dirname() -> Decorator
```

```python
@argument("path")
@dirname()
# "/home/user/file.py" -> "/home/user"
```

---

## expand_vars

Type: `ChildNode` | Supports: `str`

Expand environment variable references in the string (e.g., `$HOME` or `${HOME}`).

```python
expand_vars() -> Decorator
```

```python
@argument("path")
@expand_vars()
# "$HOME/config" -> "/home/user/config"
```

---

## lstrip / rstrip / strip

Type: `ChildNode` | Supports: `str`

Strip characters from the left, right, or both ends of the string.

```python
strip(chars: str | None = None) -> Decorator
lstrip(chars: str | None = None) -> Decorator
rstrip(chars: str | None = None) -> Decorator
```

| Parameter | Type          | Default | Description                                       |
| --------- | ------------- | ------- | ------------------------------------------------- |
| `chars`   | `str \| None` | `None`  | Characters to strip. If `None`, strips whitespace |

```python
@argument("value")
@strip()            # strip whitespace
@strip("\"'")       # strip quotes
@lstrip("/")        # strip leading slashes
@rstrip("/")        # strip trailing slashes
```

---

## remove_prefix

Type: `ChildNode` | Supports: `str`

Remove a prefix from the string if it starts with it.

```python
remove_prefix(prefix: str) -> Decorator
```

```python
@argument("url")
@remove_prefix("https://")
```

---

## remove_suffix

Type: `ChildNode` | Supports: `str`

Remove a suffix from the string if it ends with it.

```python
remove_suffix(suffix: str) -> Decorator
```

```python
@argument("filename")
@remove_suffix(".txt")
```

---

## replace

Type: `ChildNode` | Supports: `str`

Replace occurrences of a substring within the string.

```python
replace(old: str, new: str, count: int = -1) -> Decorator
```

| Parameter | Type  | Default | Description                                            |
| --------- | ----- | ------- | ------------------------------------------------------ |
| `old`     | `str` |         | Substring to replace                                   |
| `new`     | `str` |         | Replacement string                                     |
| `count`   | `int` | `-1`    | Maximum number of replacements. `-1` means replace all |

```python
@argument("path")
@replace("\\", "/")
```

---

## slugify

Type: `ChildNode` | Supports: `str`

Convert the string to a URL-friendly slug (uses the `python-slugify` library).

```python
slugify(**kwargs: Any) -> Decorator
```

Any keyword arguments are forwarded to `python-slugify`'s `slugify()` function.

```python
@argument("title")
@slugify()
# "Hello World!" -> "hello-world"
```

---

## split

Type: `ChildNode` | Supports: `str`

Split the string into a list.

```python
split(sep: str | None = None, maxsplit: int = -1) -> Decorator
```

| Parameter  | Type          | Default | Description                                       |
| ---------- | ------------- | ------- | ------------------------------------------------- |
| `sep`      | `str \| None` | `None`  | Separator string. If `None`, splits on whitespace |
| `maxsplit` | `int`         | `-1`    | Maximum number of splits. `-1` means no limit     |

**Returns:** `list[str]`

```python
@argument("tags")
@split(",")
# "a,b,c" -> ["a", "b", "c"]
```

---

## to_case

Type: `ChildNode` | Supports: `str`

A family of decorators for case conversion:

| Decorator                   | Example output |
| --------------------------- | -------------- |
| `to_camel_case()`           | `helloWorld`   |
| `to_pascal_case()`          | `HelloWorld`   |
| `to_snake_case()`           | `hello_world`  |
| `to_screaming_snake_case()` | `HELLO_WORLD`  |
| `to_kebab_case()`           | `hello-world`  |
| `to_train_case()`           | `Hello-World`  |
| `to_dot_case()`             | `hello.world`  |
| `to_path_case()`            | `hello/world`  |
| `to_flat_case()`            | `helloworld`   |
| `to_lower_case()`           | `hello world`  |
| `to_upper_case()`           | `HELLO WORLD`  |
| `to_title_case()`           | `Hello World`  |
| `to_meme_case()`            | `hElLo WoRlD`  |

All take no parameters:

```python
@argument("name")
@to_snake_case()

@argument("class_name")
@to_pascal_case()
```

---

## to_date

Type: `ChildNode` | Supports: `str`

Parse a string to a `datetime.date` object.

```python
to_date(*formats: str) -> Decorator
```

| Parameter  | Type  | Default                                  | Description                                                                                                     |
| ---------- | ----- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `*formats` | `str` | `"%Y-%m-%d"`, `"%d/%m/%Y"`, `"%m/%d/%Y"` | Format strings to try in order. Supports both strptime format (`%Y-%m-%d`) and simplified format (`YYYY-MM-DD`) |

**Returns:** `datetime.date`

```python
@argument("date")
@to_date("YYYY-MM-DD", "DD/MM/YYYY")
```

---

## to_datetime

Type: `ChildNode` | Supports: `str`

Parse a string to a `datetime.datetime` object.

```python
to_datetime(*formats: str, tz: str | None = None) -> Decorator
```

| Parameter  | Type          | Default                                           | Description                                                                              |
| ---------- | ------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `*formats` | `str`         | `"%Y-%m-%d"`, `"%H:%M:%S"`, `"%Y-%m-%d %H:%M:%S"` | Format strings to try in order                                                           |
| `tz`       | `str \| None` | `None`                                            | Timezone name (e.g., `"UTC"`, `"America/New_York"`). If `None`, result is timezone-naive |

**Returns:** `datetime.datetime`

```python
@argument("timestamp")
@to_datetime("%Y-%m-%d %H:%M:%S", tz="UTC")
```

---

## to_decimal

Type: `ChildNode` | Supports: `str`, `int`, `float`

Convert the value to a `decimal.Decimal`.

```python
to_decimal() -> Decorator
```

```python
@option("price", type=float)
@to_decimal()
```

---

## to_directory

Type: `ChildNode` | Supports: `str`, `pathlib.Path`

Convert and validate a string as a directory path, returning a `pathlib.Path`.

```python
to_directory(
    *,
    exists: bool = True,
    parents: bool = False,
    resolve: bool = True,
    allow_empty_directory: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator
```

| Parameter               | Type          | Default | Description                                   |
| ----------------------- | ------------- | ------- | --------------------------------------------- |
| `exists`                | `bool`        | `True`  | Whether the directory must exist              |
| `parents`               | `bool`        | `False` | Create parent directories if they don't exist |
| `resolve`               | `bool`        | `True`  | Resolve to absolute path                      |
| `allow_empty_directory` | `bool`        | `True`  | Whether an empty directory is accepted        |
| `include_pattern`       | `str \| None` | `None`  | Shell glob whitelist for directory names      |
| `exclude_pattern`       | `str \| None` | `None`  | Shell glob blacklist for directory names      |
| `is_readable`           | `bool`        | `False` | Require read permission                       |
| `is_writable`           | `bool`        | `False` | Require write permission                      |
| `is_executable`         | `bool`        | `False` | Require execute permission (Unix only)        |

**Returns:** `pathlib.Path`

---

## to_file

Type: `ChildNode` | Supports: `str`, `pathlib.Path`

Convert and validate a string as a file path, returning a `pathlib.Path`.

```python
to_file(
    *,
    exists: bool = True,
    parents: bool = False,
    resolve: bool = True,
    extensions: list[str] | None = None,
    allow_empty_file: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator
```

| Parameter          | Type                | Default | Description                                       |
| ------------------ | ------------------- | ------- | ------------------------------------------------- |
| `exists`           | `bool`              | `True`  | Whether the file must exist                       |
| `parents`          | `bool`              | `False` | Create parent directories if they don't exist     |
| `resolve`          | `bool`              | `True`  | Resolve to absolute path                          |
| `extensions`       | `list[str] \| None` | `None`  | Allowed file extensions (e.g., `[".py", ".pyx"]`) |
| `allow_empty_file` | `bool`              | `True`  | Whether a zero-byte file is accepted              |
| `include_pattern`  | `str \| None`       | `None`  | Shell glob whitelist for filenames                |
| `exclude_pattern`  | `str \| None`       | `None`  | Shell glob blacklist for filenames                |
| `is_readable`      | `bool`              | `False` | Require read permission                           |
| `is_writable`      | `bool`              | `False` | Require write permission                          |
| `is_executable`    | `bool`              | `False` | Require execute permission (Unix only)            |

**Returns:** `pathlib.Path`

```python
@argument("config")
@to_file(extensions=[".json", ".yaml"])
```

---

## to_path

Type: `ChildNode` | Supports: `str`

Convert and validate a string as a `pathlib.Path`. More flexible than `to_file` and `to_directory`; accepts both files and directories by default.

```python
to_path(
    *,
    exists: bool = True,
    parents: bool = False,
    resolve: bool = True,
    extensions: list[str] | None = None,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    allow_file: bool = True,
    allow_directory: bool = True,
    allow_empty_directory: bool = True,
    allow_empty_file: bool = True,
    allow_symlink: bool = False,
    follow_symlink: bool = True,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator
```

| Parameter               | Type                | Default | Description                                   |
| ----------------------- | ------------------- | ------- | --------------------------------------------- |
| `exists`                | `bool`              | `True`  | Whether the path must exist                   |
| `parents`               | `bool`              | `False` | Create parent directories if they don't exist |
| `resolve`               | `bool`              | `True`  | Resolve to absolute path                      |
| `extensions`            | `list[str] \| None` | `None`  | Allowed file extensions                       |
| `include_pattern`       | `str \| None`       | `None`  | Shell glob whitelist                          |
| `exclude_pattern`       | `str \| None`       | `None`  | Shell glob blacklist                          |
| `allow_file`            | `bool`              | `True`  | Whether files are accepted                    |
| `allow_directory`       | `bool`              | `True`  | Whether directories are accepted              |
| `allow_empty_directory` | `bool`              | `True`  | Whether empty directories are accepted        |
| `allow_empty_file`      | `bool`              | `True`  | Whether empty files are accepted              |
| `allow_symlink`         | `bool`              | `False` | Whether symlinks are accepted                 |
| `follow_symlink`        | `bool`              | `True`  | Whether to follow symlinks when resolving     |
| `is_readable`           | `bool`              | `False` | Require read permission                       |
| `is_writable`           | `bool`              | `False` | Require write permission                      |
| `is_executable`         | `bool`              | `False` | Require execute permission (Unix only)        |

**Returns:** `pathlib.Path`

```python
@argument("input")
@to_path(extensions=["csv"], exists=True, allow_directory=False)
```

---

## to_string

Type: `ChildNode` | Supports: `any`

Convert the value to a string using `str()`.

```python
to_string() -> Decorator
```

```python
@option("count", type=int)
@to_string()
# 42 -> "42"
```

---

## to_symlink

Type: `ChildNode` | Supports: `str`, `pathlib.Path`

Convert and validate a string as a symlink path, returning a `pathlib.Path`.

```python
to_symlink(
    *,
    exists: bool = True,
    resolve: bool = False,
    follow_symlink: bool = False,
    is_readable: bool = False,
    is_writable: bool = False,
    is_executable: bool = False,
) -> Decorator
```

| Parameter        | Type   | Default | Description                                                  |
| ---------------- | ------ | ------- | ------------------------------------------------------------ |
| `exists`         | `bool` | `True`  | Whether the symlink must exist                               |
| `resolve`        | `bool` | `False` | Resolve path (defaults to `False` to preserve the symlink)   |
| `follow_symlink` | `bool` | `False` | Follow the symlink when resolving (only when `resolve=True`) |
| `is_readable`    | `bool` | `False` | Require read permission                                      |
| `is_writable`    | `bool` | `False` | Require write permission                                     |
| `is_executable`  | `bool` | `False` | Require execute permission (Unix only)                       |

**Returns:** `pathlib.Path`

---

## to_time

Type: `ChildNode` | Supports: `str`

Parse a string to a `datetime.time` object.

```python
to_time(*formats: str) -> Decorator
```

| Parameter  | Type  | Default                 | Description                    |
| ---------- | ----- | ----------------------- | ------------------------------ |
| `*formats` | `str` | `"%H:%M:%S"`, `"%H:%M"` | Format strings to try in order |

**Returns:** `datetime.time`

```python
@argument("alarm")
@to_time("%H:%M")
```

---

## to_timestamp

Type: `ChildNode` | Supports: `datetime.datetime`, `datetime.date`

Convert a `datetime` or `date` object to a numeric Unix timestamp.

```python
to_timestamp(unit: Literal["s", "ms", "us", "ns"] = "s") -> Decorator
```

| Parameter | Type  | Default | Description                                                                                         |
| --------- | ----- | ------- | --------------------------------------------------------------------------------------------------- |
| `unit`    | `str` | `"s"`   | Timestamp unit: `"s"` (seconds), `"ms"` (milliseconds), `"us"` (microseconds), `"ns"` (nanoseconds) |

**Returns:** `float` (or `int` for nanoseconds)

```python
@argument("date")
@to_date()
@to_timestamp("ms")
# "2024-01-15" -> 1705276800000
```

---

## truncate

Type: `ChildNode` | Supports: `str`

Truncate the string to a maximum length.

```python
truncate(length: int, suffix: str = "...") -> Decorator
```

| Parameter | Type  | Default | Description                     |
| --------- | ----- | ------- | ------------------------------- |
| `length`  | `int` |         | Maximum number of characters    |
| `suffix`  | `str` | `"..."` | String to append when truncated |

```python
@argument("description")
@truncate(100)
# "A very long description..." truncated to 100 chars
```
