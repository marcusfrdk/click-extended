![Banner](../../assets/click-extended-documentation-banner.png)

# Hooks

Hooks is a system that allows you to hook into various lifecycles of the command-line interface.

## Methods

All methods can be used either as global or local. Global means they always will run regardless of what command or group is called, this will not have access to the active context and are called in the global scope as a function, e.g. `on_init(handler)`. When locally scoped, they are used as decorators in a context like `@on_init(handler)`, and will therefore have access to the tree's context.

| Method     | Runs                     | Note                                                               |
| ---------- | ------------------------ | ------------------------------------------------------------------ |
| `on_boot`  | Before context creation. |                                                                    |
| `on_init`  | After context creation.  |                                                                    |
| `on_error` | On an interrupt.         | Can catch all exceptions or select specific to include or exclude. |
| `on_exit`  | When the program exits.  | For example, when `sys.exit()` is called.                          |

## Examples

### `on_error`

This example shows a simple, catch-all, global usage of the `on_error` hook. If any exceptions are raised, the hook will run the `handle_error` function.

```python
from click_extended import command
from click_extended.hooks import on_error
from click_extended.types import HookEvent

def handle_error(event: HookEvent) -> None:
    ...

on_error(handle_error)

@command()
def my_command() -> None:
    ...
```

This example will be locally scoped to the `my_command` command. If any exceptions are raised inside that command, the `handle_error` function will be called.

```python
from click_extended import command
from click_extended.hooks import on_error
from click_extended.types import HookEvent

def handle_error(event: HookEvent) -> None:
    ...

@command()
@on_error(handle_error)
def my_command() -> None:
    ...
```

In this example, only the `ValueError` will be handled and is locally scoped to the `my_command` command. By default, the provided exceptions are inclusive and works in a whitelist pattern using the variadic `*exc` or `include` parameter.

```python
from click_extended import command
from click_extended.hooks import on_error
from click_extended.types import HookEvent

def handle_error(event: HookEvent) -> None:
    ...

@command()
@on_error(handle_error, ValueError)
def my_command() -> None:
    ...

@command()
@on_error(handle_error, include=ValueError)
def my_other_command() -> None:
    ...

@command()
@on_error(handle_error, include=(ValueError, TypeError))
def my_command() -> None:
    ...
```

Finally, if you want to include all exceptions except some specific ones, which is done by using the blacklist-pattern with the `exclude` parameter.

```python
from click_extended import command
from click_extended.hooks import on_error
from click_extended.types import HookEvent

def handle_error(event: HookEvent) -> None:
    ...

@command()
@on_error(handle_error, exclude=KeyboardInterrupt)
def my_other_command() -> None:
    ...

@command()
@on_error(handle_error, exclude=(KeyboardInterrupt, SystemExit))
def my_command() -> None:
    ...
```
