![Banner](../../assets/click-extended-documentation-banner.png)

# Misc Decorators

Miscellaneous decorators that don't fit neatly into other categories. They cover defaults, observation, confirmation, error handling, warnings, and more.

## Table of Contents

- [catch](#catch)
- [confirm_if](#confirm_if)
- [default](#default)
- [deprecated](#deprecated)
- [experimental](#experimental)
- [now](#now)
- [observe](#observe)

---

## catch

Type: `ValidationNode`

Catch exceptions raised during command execution or validation. An optional handler is invoked when a matching exception is caught.

```python
catch(
    *exception_types: type[BaseException],
    handler: Callable | None = None,
    reraise: bool = False,
) -> Decorator
```

| Parameter          | Type                  | Default     | Description                                                                                                            |
| ------------------ | --------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| `*exception_types` | `type[BaseException]` | `Exception` | Exception types to catch. If none are given, catches `Exception`                                                       |
| `handler`          | `Callable \| None`    | `None`      | Optional handler called when an exception is caught. Accepts `()`, `(exception)`, or `(exception, context)` signatures |
| `reraise`          | `bool`                | `False`     | If `True`, re-raise the exception after calling the handler                                                            |

```python
from click_extended import command
from click_extended.decorators import catch

@command()
@catch(ValueError, handler=lambda e: print(f"Error: {e}"))
def cmd() -> None:
    raise ValueError("something went wrong")

# Combining with @exclusive to catch validation errors:
@command()
@exclusive("json", "xml")
@catch(ValueError, handler=lambda e: print(f"Conflict: {e}"))
@option("json", is_flag=True)
@option("xml", is_flag=True)
def export(json: bool, xml: bool) -> None:
    pass
```

---

## confirm_if

Type: `ChildNode` | Supports: `any`

Conditionally prompt the user for confirmation based on a predicate function. If the predicate returns `True`, the user is asked to confirm before continuing. If they decline, the command is aborted.

```python
confirm_if(
    prompt: str,
    fn: Callable[[Any], bool] | Callable[[Any, Context], bool],
    truthy: list[str] | None = None,
) -> Decorator
```

| Parameter | Type                | Default                   | Description                                                                                              |
| --------- | ------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------- |
| `prompt`  | `str`               |                           | Confirmation prompt text. Can include `{value}` placeholder                                              |
| `fn`      | `Callable`          |                           | Predicate: return `True` to trigger the confirmation prompt. Accepts `fn(value)` or `fn(value, context)` |
| `truthy`  | `list[str] \| None` | `["y", "yes", "ok", "1"]` | Accepted confirmation responses (case-insensitive)                                                       |

If `CLICK_EXTENDED_TESTING=1` is set, confirmation is automatically granted (useful for tests).

```python
@option("count", type=int)
@confirm_if("Are you sure you want to process {value} items?", lambda x: x > 100)
```

---

## default

Type: `ChildNode` | Supports: `any`

Set a default value when the parameter was not provided by the user. Exactly one source must be given.

```python
default(
    *,
    from_value: Any = None,
    from_env: str | None = None,
    from_param: str | None = None,
) -> Decorator
```

| Parameter    | Type          | Default | Description                                  |
| ------------ | ------------- | ------- | -------------------------------------------- |
| `from_value` | `Any`         | `None`  | A literal value to use as default            |
| `from_env`   | `str \| None` | `None`  | Name of an environment variable to read      |
| `from_param` | `str \| None` | `None`  | Name of another parameter whose value to use |

Sources are evaluated in order: `from_value` → `from_env` → `from_param`. Exactly one must be provided.

```python
@option("output")
@default(from_value="./output")

@option("host")
@default(from_env="DEFAULT_HOST")

@option("backup_path")
@default(from_param="input_path")
```

---

## deprecated

Type: `ChildNode` | Supports: `any`

Print a deprecation warning to stderr when the decorated parameter is used.

```python
deprecated(
    name: str | None = None,
    since: str | None = None,
    removed: str | None = None,
) -> Decorator
```

| Parameter | Type          | Default | Description                                    |
| --------- | ------------- | ------- | ---------------------------------------------- |
| `name`    | `str \| None` | `None`  | Name of the replacement parameter              |
| `since`   | `str \| None` | `None`  | Version in which the parameter was deprecated  |
| `removed` | `str \| None` | `None`  | Version in which the parameter will be removed |

```python
@option("old_flag")
@deprecated(name="new_flag", since="2.0", removed="3.0")
```

---

## experimental

Type: `ChildNode` | Supports: `any`

Print an experimental warning to stderr when the decorated parameter is used.

```python
experimental(
    *,
    message: str | None = None,
    since: str | None = None,
    stable: str | None = None,
) -> Decorator
```

| Parameter | Type          | Default | Description                                                      |
| --------- | ------------- | ------- | ---------------------------------------------------------------- |
| `message` | `str \| None` | `None`  | Custom warning message. If set, overrides auto-generated message |
| `since`   | `str \| None` | `None`  | Version since which the parameter is experimental                |
| `stable`  | `str \| None` | `None`  | Version in which the parameter is expected to be stable          |

```python
@option("turbo_mode")
@experimental(since="1.5", stable="2.0")

@option("new_feature")
@experimental(message="This feature is experimental and may change.")
```

---

## now

Type: `ParentNode`

Inject the current datetime as a parameter. Does not consume any CLI argument.

```python
now(name: str, tz: str = "UTC") -> Decorator
```

| Parameter | Type  | Default | Description                                                         |
| --------- | ----- | ------- | ------------------------------------------------------------------- |
| `name`    | `str` |         | The parameter name to inject the datetime as                        |
| `tz`      | `str` | `"UTC"` | Timezone name (e.g., `"UTC"`, `"Europe/Stockholm"`, `"US/Eastern"`) |

**Returns:** `datetime.datetime` (timezone-aware)

```python
from click_extended import command
from click_extended.decorators import now

@command()
@now("timestamp")
@now("local_time", tz="Europe/Stockholm")
def my_command(timestamp, local_time) -> None:
    print(f"UTC: {timestamp}")
    print(f"Local: {local_time}")
```

---

## observe

Type: `ChildNode` | Supports: `any`

Observe a value without modifying it. The handler is called with the current value (and optionally the context) but the value is passed through unchanged.

```python
observe(
    handler: Callable[[Any], Any] | Callable[[Any, Context], Any],
) -> Decorator
```

| Parameter | Type       | Default | Description                                                              |
| --------- | ---------- | ------- | ------------------------------------------------------------------------ |
| `handler` | `Callable` |         | Observer function. Accepts `handler(value)` or `handler(value, context)` |

Supports both sync and async handlers.

```python
@option("token")
@observe(lambda v: print(f"Token received: {v}"))

@option("path")
@observe(lambda v, ctx: print(f"Processing {v} for {ctx.get_current_parent_as_parent().name}"))
```
