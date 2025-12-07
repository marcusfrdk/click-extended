![Banner](../../assets/click-extended-documentation-banner.png)

# ChildValidationNode

The `ChildValidationNode` is a hybrid node type that combines the capabilities of a `ChildNode` and a `ValidationNode`. It is designed to be polymorphic in scenarios where a node needs to be attached to a specific parent (like a child) but also needs to perform complex validation logic or access the global context (like a validation node).

## Usage

`ChildValidationNode` is typically used as a base class for creating custom decorators that need both parent-specific context and global validation capabilities.

```python
from click_extended import ChildValidationNode

class MyHybridNode(ChildValidationNode):
    def handle_str(self, value: str) -> str:
        return value.upper()

    # Other handlers

    def on_init(self):
        pass

    def on_finalize(self):
        pass
```

```python
# As child
@command()
@argument("...")
@my_hybrid_node()

# As validator
@command()
@my_hybrid_node()
@argument("...")
```

## Methods

This inherits the methods of the [child node](./CHILD_NODE.md) and the [validation node](./VALIDATION_NODE.md).
