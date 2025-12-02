![Banner](../../assets/click-extended-documentation-banner.png)

# Validation Node

A validation node is one of the core features of `click-extended` and adds the ability to hook into the lifecycle and perform validation.

## Table of Contents

- [Usage](#usage)
- [Examples](#examples)
- [Extending](#extending)

## Usage

The validation node is pretty straightforward in how it works. Unlike [parent nodes](./PARENT_NODE.md), the validation node is not positional and can be placed anywhere in the decorator tree. It will run either before or after the tree has been processed, or both.

It is validation only (hence the name) and is used to perform validation, such as exclusivity checks and more.

There are two methods that can be implemented based of needs, either the `on_init` method which runs before any other nodes have been processed (or in order of declaration if other validation nodes are present), and the `on_finalize` method, which runs after all other nodes have been processed.

## Examples

```python
from typing import Any
from click_extended.classes import ValidationNode
from click_extended.types import Context, Decorator

class MyValidator(ValidationNode):
    def on_init(self, context: Context, *args: Any, **kwargs: Any) -> None:
        print("Context before:", context)

    def on_finalize(self, context: Context, *args: Any, **kwargs: Any) -> None:
        print("Context after:", context)

def my_validator() -> Decorator:
    return MyValidator.as_decorator()
```

```python
@command()
@my_validator()
def my_function():
    ...
```

## Extending

As with the [parent node](./PARENT_NODE.md) and the [child node](./CHILD_NODE.md), the validation node is also extendable by either implementing the `on_init` or `on_finalize` methods.

### Methods

| Name          | Description                                        |
| ------------- | -------------------------------------------------- |
| `on_init`     | Runs _before_ all other nodes have been processed. |
| `on_finalize` | Runs _after_ all other nodes have been processed.  |
