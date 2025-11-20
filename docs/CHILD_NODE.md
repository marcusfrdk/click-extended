![Banner](../assets/click-extended-documentation-banner.png)

# Child Node

The `ChildNode` is the base class for parameter validators and transformers in click-extended. It provides the foundation for processing parameter values through a chain of operations, enabling validation, transformation, and custom logic to be applied to CLI parameter values before they reach your command function.

## Purpose

The purpose of the child node is to perform validation or transformation to the values provided by [parent nodes](./PARENT_NODE.md). This could be anything from converting the value to upper case to checking if children are exclusive. The library is built to be easy to extend with your own children if needed, but many pre-built children are provided in either the `click_extended.validation` or `click_extended.transform` modules.

## Types

A child node is either considered a _transformation_ or _validation_ node depending if a `return` statement is present. Validation nodes are only run, but the output is ignored and passed to the next transformation node or the decorated function, while the output of transformation nodes are passed on to the next value.

## Flow of Data

Data always originates from a [parent node](./PARENT_NODE.md) or another child node. Here is an example of how to structure the decorators.

```python
@option("--name") # ParentNode (defaults to type=str)
@to_lower_case() # ChildNode
@min_length(2) # ChildNode
@max_length(32) # ChildNode
def my_function(name: str):
    ...
```

In this example, we have one parent (data source), one transformation node (`@to_lower_case`) and two validation nodes (`@min_length` and `@max_length`). So the data originates from user input in `@option`, which gets passed along to the `@to_lower_case` node. This then passes the transformed value to both validation nodes, which then gets passed along to the function `my_function` as a keyword argument called `name`. Names are always transformed to `snake_case` in all data sources in order to work with Python.

## Error Handling

Like in any program, errors can be raise inside the `process()` method of a child node. However, `click-extended` handle some errors in a special way. Any exception that is a subclass of the `click_extended.errors.CatchableError` will be caught, formatted, and displayed in a user-friendly way. There are also certain other types which read the context of the node and display more customized base errors like `click_extended.errors.ChildNodeProcessError` which displays more detailed information about what has gone wrong.

| Name                              | Description                                                                       | Parent Class          |
| --------------------------------- | --------------------------------------------------------------------------------- | --------------------- |
| `CatchableError`                  | Naive base class for any error that chould be handled gracefully                  |                       |
| `ChildNodeProcessError`           | Context-aware base class for errors that should include formatting of the message |                       |
| `ValidationError(message: str)`   | Exception raised when some validation fails.                                      | CatchableError        |
| `TransformError(message: str)`    | Exception raised when some transformation fails.                                  | CatchableError        |
| `UnhandledValueError(value: Any)` | Exception raised for code paths which should not be reached.                      | ChildNodeProcessError |

## Creating Your Own Decorator

### Bare Minimum

For those who like to keep Python simple, here is how you would set up the bare minimum without any typing.

```python
from click_extended import ChildNode

class AddSuffix(ChildNode):
    def process(self, value, context):
        return value + context.kwargs["suffix"]

def add_suffix(suffix):
    return AddSuffix.as_decorator(suffix=suffix)
```

It is strongly discouraged avoid using types, as you will lose out on most features `click-extended` provides. But this example is shown for those who just want to get started.

### With Typing

If you want to utilize the power of Python's type-hinting system and use the additional features provided by `click-extended`, this is how you would set up the same example but with additional features.

```python
from click_extended import ChildNode
from click_extended.types import ProcessContext, Decorator

class AddSuffix(ChildNode):
    """ Decorator to add a suffix to a string. """

    def process(self, value: str, context: ProcessContext) -> str:
        return value + context.kwargs["suffix"]

def add_suffix(suffix: str) -> Decorator:
    """
    Add a suffix to the value.

    Supports: `str`, `tuple[str]`, and `tuple[tuple[str]]`

    Args:
        suffix (str):
            The suffix to use.

    Returns:
        Decorator:
            The decorated function.
    """
    return AddSuffix.as_decorator(suffix=suffix)
```

This is a fully typed example that now offers additional features. By typing the `process()` method, `click-extended` now knows that `process()` should only be called if the input value is a string. If the value is missing, the `process()` method will not be called. Alongside this, it tells `click-extended` that this decorator only supports [parents](./PARENT_NODE.md) that have `type=str` (default). If the types don't match, a `TypeMismatchError` will be raised.

### Supporting Complex Values

In `click-extended`, there are three type of values; singular values, tuple values and nested tuple values. Adding `None` as a type makes the `process()` method accept missing values, and not typing the `process()` method or setting is as `typing.Any` will accept all types.

#### Singluar Value

Singular values are the normal values, such as `@option("--value")`, `@argument("value", type=int)`, and `@env("API_KEY")`. These pass along a single value.

Child nodes where the `value` parameter of the `process()` method are typed like `value: str`, `value: int | float`, `value: Any`, or `value: str | None` accept singular values.

#### Tuple Value

The next type of value is a tuple value. This is a value that originates from an `@option` or `@argument` which sets the `nargs` parameter to a values which is not equal to one. The incoming value is now a tuple with simple types (such as primitives, `pathlib.Path` or `datetime.datetime`). These values come from configurations like `@option("--value", nargs=2)` and `@argument("value", nargs=-1)`. Note that options are not variadic and don't support `nargs=-1` like the argument does, meaning you need to set it to a fixed value.

If the `value` parameter is marked as `value: tuple[<type>]`, it accepts a tuple value.

#### Nested Tuple Value

The last type of value comes from the most complex type of configuration, which is when multiple options are accepted that themselves require multiple values. This sets `value` to a nested tuple of values (`tuple[tuple[<type>]])`) and comes from configurations like `@option("--tag", nargs=2, multiple=True)`. _Note that this is exclusive to options._

If the `value` parameter is marked as `tuple[tuple[<type>]], it accepts nested tuple values. Note that a nested tuple value does not automatically accept regular tuple values or singular values, as each must be explicitly set.

#### Examples

Here is an extension of the previous example but with full support and typing for all three modes:

```python
from click_extended import ChildNode
from click_extended.types import ProcessContext, Decorator
from click_extended.errors import UnhandledValueError
from click_extended.utils import (
    is_single_value,
    is_tuple_value,
    is_nested_tuple_value,
)

class AddSuffix(ChildNode):
    """ Decorator to add a suffix to a string. """

    def process(
        self, value: str | tuple[str] | tuple[tuple[str]],
        context: ProcessContext,
    ) -> str | tuple[str] | tuple[tuple[str]]:
        suffix = context.kwargs["suffix"]

        if is_single_value(value, str):
            return value + context.kwargs.suffix
        if is_tuple_value(value, str):
            return tuple(v + suffix for v in value)
        if is_nested_tuple_value(value, str):
            return tuple(tuple(v + suffix for v in t) for t in value)

        raise UnhandledValueError(value)

def add_suffix(suffix: str) -> Decorator:
    """
    Add a suffix to the value.

    Supports: `str`, `tuple[str]`, and `tuple[tuple[str]]`

    Args:
        suffix (str):
            The suffix to use.

    Returns:
        Decorator:
            The decorated function.
    """
    return AddSuffix.as_decorator(suffix=suffix)
```

In your application, you can now use the function `add_suffix` as a transformation child node with `@add_suffix("!")`.
