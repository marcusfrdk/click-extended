![Banner](../../assets/click-extended-documentation-banner.png)

# Child Node

A child node is one of the core features of `click-extended` and adds the ability to process the value from a parent node.

## Table of Contents

- [Usage](#usage)
- [Examples](#examples)
- [Extending](#extending)

## Usage

## Examples

### Basic Example

```python
from click_extended import command, argument, option
from click_extended.decorators import to_lower_case

@command()
@argument("value")
@to_lower_case()
def my_function(value: str):
    """This function converts the value to lower case."""
    print(f"The value '{value}' should is lowercase.")

# $ python cli.py "Hello World"
# The value 'hello world' should be lowercase.
```

### Chain Example

```python
from click_extended import command, argument, option
from click_extended.decorators import to_lower_case, min_length, max_length, contains_symbols

@command()
@argument("password")
@contains_symbols()
@min_length(8)
@max_length(16)
def my_function(password: str):
    """Get a password that is validated."""
    print("The password is valid")

# $ python cli.py "this_is_valid"
# The password is valid

# $ python cli.py no
# ValueError (my_function):
```

## Extending

Creating your own child nodes is one of the most powerful features of this library, even though this library includes a lot of [pre-built decorators](../nodes/DECORATORS.md). Here is a guide in how to create your own children.

### Handlers

Before you can implement your own child, you must understand the concept of a handler. A handler is a function that handles some type, such as a primitive (string, integer, float, bool), tuples, lists, and specifically values where it's missing. However, you don't have to implement any handler for a child to work, but what's the point of that?

All handlers support either asynchronous or synchronous execution by simple adding the `async` keyword for the method and that method will be executed in an asynchronous environment.

All handlers share the same structure of parameters, which are `self`, `value`, `context`, `*args`, and `**kwargs`. The type of the value depends on the handler, and `*args` and `**kwargs` are passed on from the `as_decorator()` method.

Here is a table of all supported handler methods that can be implemented:

| Name                | Type                                            | Description                                                     |
| ------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| handle_none         | None                                            | Used for handling missing values.                               |
| handle_all          | Any                                             | Used for handling all values                                    |
| handle_primitive    | str, int, float, bool                           | Used for handling Python primitives.                            |
| handle_tuple        | tuple                                           | Used for handling all types of tuples.                          |
| handle_flat_tuple   | tuple[Any, ...]                                 | Used for handling any flat tuple (tuple of simple values).      |
| handle_nested_tuple | tuple[Any, ...]                                 | Used for strictly nested tuples (tuples of complex objects).    |
| handle_list         | list[Any]                                       | Used for handling lists.                                        |
| handle_dict         | dict[Any, Any]                                  | Used for handling dictionaries.                                 |
| handle_tag          | dict[str, Any]                                  | Used for handling the values from a `@tag` decorator.           |
| handle_datetime     | datetime.datetime, datetime.date, datetime.time | Used for handling types from the `datetime` library.            |
| handle_uuid         | uuid.UUID                                       | Used for handling values from the `uuid` library.               |
| handle_path         | pathlib.Path                                    | Used for handling `Path` objects from the `pathlib` library.    |
| handle_bytes        | bytes                                           | Used for handling `bytes` objects.                              |
| handle_decimal      | decimal.Decimal                                 | Used for handling `Decimal` objects from the `decimal` library. |

### Structure

#### Class

The class you define is the node itself. It inherits properties and methods from the `ChildNode` class, which is used to interact with the rest of the tree and context. **There are no methods you need to implement** except for the handlers for the types you want to support.

#### Handler

Handlers are the only methods you would need to implement to start using it in your own command line interface.

All handlers share the same format:

```python
def handle_<type>(
    self,
    value: <type>,
    context: Context,
    *args: Any,
    **kwargs: Any,
) -> <return_type>
```

and of course, if you want the handler to run asynchronously, you would define it nearly the same:

```python
async def handle_<type>(
    self,
    value: <type>,
    context: Context,
    *args: Any,
    **kwargs: Any,
) -> <return_type>
```

This library supports mixed environments for running the methods, so even if your function is not asynchronous, the handler can still run asynchronously.

#### Decorator

There are two ways of using your new shiny child node, either by directly- or indirectly (recommended) using it.

##### Indirectly (Recommended)

The indirect method is **highly recommended** for your end user API, as this provides better IDE support, the ability to add docstrings and more. This is how you would create an intermedia decorator:

```python
from typing import Any

from click_extended import command
from click_extended.classes import ChildNode
from click_extended.types import Context, Decorator

class MyChild(ChildNode):
    ...

def my_child(name: str | None = None) -> Decorator:
    """
    My own child, isn't this great?

    Args:
        name (str | None, optional):
            The name of my child.

    Returns:
        Decorator:
            The decorated function.
    """
    return MyChild.as_decorator(name=name) # name is now available in **kwargs in all handlers


@command()
@my_child("Alice")
...
```

##### Directly

You can define your decorator directly from the class itself by calling the `as_decorator()` method. This is useful when developing, as you won't need to update documentation and relying on an intermediate function. However, for the end-user, it's strongly recommended to access your child node indirectly. Here is an example of how to use the child node indirectly:

```python
from typing import Any

from click_extended import command
from click_extended.classes import ChildNode
from click_extended.types import Context

class MyChild(ChildNode):
    ...

@command()
@MyChild.as_decorator()
...
```
