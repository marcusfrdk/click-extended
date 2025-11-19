![Banner](../assets/click-extended-documentation-banner.png)

# Tree

The `Tree` class is the central registry for managing the node hierarchy in `click-extended`. It orchestrates the registration and organization of all nodes (root, parent, child, tag, and global) in your CLI application, maintaining the relationships between decorators and handling the bottom-to-top decorator application order.

## Overview

A `Tree` instance serves as the backbone of a CLI command's structure. It manages:

- **Root Node**: The command or group at the top of the hierarchy
- **Parent Nodes**: Parameters like `@option`, `@argument`, `@env` that provide values
- **Child Nodes**: Transformers and validators attached to parent nodes
- **Tags**: Named groups for cross-parameter validation
- **Global Nodes**: Special nodes that can access and modify the entire tree
- **Custom Data**: Key-value storage accessible to GlobalNodes for sharing data across the tree

> [!NOTE]
> The `Tree` class is an internal implementation detail. Users interact with the tree indirectly through decorators (`@command`, `@option`, etc.) and the `.visualize()` method. Direct tree manipulation is reserved for advanced use cases via GlobalNodes (see [GLOBAL_NODE.md](./GLOBAL_NODE.md)).

## Architecture

### Decorator Processing Order

Decorators in Python are applied **bottom-to-top**, but click-extended needs them processed **top-to-bottom**. The `Tree` solves this by:

1. **Queueing**: As decorators execute (bottom-to-top), nodes are queued in a pending list
2. **Registration**: When the root decorator executes (last), it registers itself and triggers tree building
3. **Reversal**: The pending queue is reversed to restore logical top-to-bottom order
4. **Building**: Nodes are processed in correct order to build the hierarchy

```python
@command()        # Executed LAST (root), triggers tree building
@option("--name") # Executed 2nd (parent), queued
@uppercase()      # Executed FIRST (child), queued
def greet(name: str):
    print(f"Hello, {name}!")
```

### Node Hierarchy

```text
Tree
├── Root (RootNode)
│   ├── Parent 1 (ParentNode)
│   │   ├── Child 1 (ChildNode)
│   │   └── Child 2 (ChildNode)
│   └── Parent 2 (ParentNode)
│       └── Child 1 (ChildNode)
├── Tags (dict[str, Tag])
│   └── auth (Tag)
│       └── Child 1 (ChildNode)
└── Globals (list[GlobalNode])
    └── Global 1 (GlobalNode)
```

## Attributes

| Name         | Description                                                | Type               | Default |
| ------------ | ---------------------------------------------------------- | ------------------ | ------- |
| `root`       | The root node (command or group) of the tree.              | RootNode \| None   | None    |
| `recent`     | Most recently registered parent node for child attachment. | ParentNode \| None | None    |
| `recent_tag` | Most recently registered tag for child attachment.         | Tag \| None        | None    |
| `tags`       | Dictionary of tag instances by name.                       | dict[str, Tag]     | {}      |
| `globals`    | List of global nodes in registration order.                | list[GlobalNode]   | []      |
| `data`       | Custom key-value storage for GlobalNodes to share data.    | dict[str, Any]     | {}      |

## Methods

### `get_data(key: str) -> Any`

Retrieve a value from the custom data dictionary. Primarily used by GlobalNodes to access shared data.

**Parameters:**

- `key` (str): The key to look up

**Returns:**

- Any: The value if found, `None` otherwise

> [!NOTE]
> This method is typically accessed within GlobalNodes via the `tree` parameter. See [GLOBAL_NODE.md](./GLOBAL_NODE.md) for usage examples.

### `set_data(key: str, value: Any) -> None`

Store a value in the custom data dictionary. Primarily used by GlobalNodes to share data across the tree.

**Parameters:**

- `key` (str): The key to store
- `value` (Any): The value to store

> [!NOTE]
> This method is typically accessed within GlobalNodes via the `tree` parameter. See [GLOBAL_NODE.md](./GLOBAL_NODE.md) for usage examples.

### `register_root(node: RootNode) -> None` _(Internal)_

Register the root node and build the entire tree from queued pending nodes. This is called automatically by `@command` or `@group` decorators.

**Parameters:**

- `node` (RootNode): The root node to register

**Raises:**

- `RootNodeExistsError`: If a root node is already registered
- `ParentNodeExistsError`: If duplicate parent names are found
- `NoParentError`: If a child node has no parent to attach to
- `InvalidChildOnTagError`: If a transformation child is attached to a tag

**Internal Process:**

1. Sets the root node
2. Retrieves and reverses pending nodes queue
3. Processes each node type:
   - **parent**: Adds to root's children, updates `recent`
   - **child**: Attaches to `recent` parent or `recent_tag`
   - **tag**: Registers tag and updates `recent_tag`
   - **global**: Executes (if not delayed) and adds to globals list

### `register_parent(node: ParentNode) -> None` _(Internal)_

Register a parent node directly to the tree. Used internally during the decoration process.

**Parameters:**

- `node` (ParentNode): The parent node to register

**Raises:**

- `NoRootError`: If no root node exists
- `ParentNodeExistsError`: If a parent with the same name already exists

### `register_child(node: ChildNode) -> None` _(Internal)_

Register a child node directly to the tree. Used internally during the decoration process.

**Parameters:**

- `node` (ChildNode): The child node to register

**Raises:**

- `NoRootError`: If no root node exists
- `NoParentError`: If no recent parent node exists

### `visualize() -> None`

Display the tree structure in a formatted, indented view showing all nodes and their relationships. This method is accessible through the command/group wrapper.

**Raises:**

- `NoRootError`: If no root node exists

```python
from click_extended import command, option, argument

@command()
@option("--verbose", "-v", is_flag=True)
@argument("filename")
def process(filename: str, verbose: bool):
    """Process a file."""
    pass

# Visualize via the wrapper (not direct tree access)
process.visualize()

# Output:
# process
#   verbose
#   filename
```

## Pending Nodes Queue

The module provides global functions for managing the pending nodes queue during decorator execution:

### `queue_parent(node: ParentNode) -> None`

Add a parent node to the pending queue. Called automatically by `@option`, `@argument`, `@env` decorators.

### `queue_child(node: ChildNode) -> None`

Add a child node to the pending queue. Called automatically by child node decorators.

### `queue_tag(node: Tag) -> None`

Add a tag to the pending queue. Called automatically by `@tag` decorator.

### `queue_global(node: GlobalNode) -> None`

Add a global node to the pending queue. Called automatically by global node decorators.

### `get_pending_nodes() -> list[tuple[str, Node]]`

Retrieve and clear the pending nodes queue. Returns a list of tuples containing node type and node instance.

**Returns:**

- list[tuple[str, Node]]: List of ("parent"|"child"|"tag"|"global", node) tuples

## Examples

### Basic Tree Structure

```python
from click_extended import command, option, argument

@command()
@option("--name", default="World")
@argument("count", type=int)
def greet(name: str, count: int):
    """Greet someone multiple times."""
    for _ in range(count):
        print(f"Hello, {name}!")

# Tree structure:
# greet (RootNode)
# ├── name (ParentNode: Option)
# └── count (ParentNode: Argument)
```

### Tree with Child Nodes

```python
from click_extended import command, option, ChildNode, ProcessContext

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()

def uppercase(*args, **kwargs):
    return Uppercase.as_decorator(*args, **kwargs)

@command()
@option("--name")
@uppercase()
def greet(name: str):
    print(f"Hello, {name}!")

# Tree structure:
# greet (RootNode)
# └── name (ParentNode: Option)
#     └── uppercase (ChildNode)
```

### Tree with Tags

```python
from click_extended import command, option, ChildNode, ProcessContext

class ValidatePassword(ChildNode):
    def process(self, value, context: ProcessContext):
        auth_tag = context.tags.get("auth")
        if auth_tag:
            provided = auth_tag.get_provided_values()
            username = provided.get("username")
            if username and value == username:
                raise ValueError("Password cannot match username")
        return None

def validate_password(*args, **kwargs):
    return ValidatePassword.as_decorator(*args, **kwargs)

@command()
@option("--username", tags="auth")
@option("--password", tags="auth")
@validate_password()
def register(username: str, password: str):
    print("Registration successful!")

# Tree structure:
# register (RootNode)
# ├── username (ParentNode: Option)
# └── password (ParentNode: Option)
#     └── validate_password (ChildNode)
# Tags:
# └── auth (Tag)
#     ├── username
#     └── password
```

### Tree with Multiple Children per Parent

```python
from click_extended import command, option, ChildNode, ProcessContext

class Strip(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.strip()

def strip(*args, **kwargs):
    return Strip.as_decorator(*args, **kwargs)

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()

def uppercase(*args, **kwargs):
    return Uppercase.as_decorator(*args, **kwargs)

class AddExclamation(ChildNode):
    def process(self, value, context: ProcessContext):
        return f"{value}!"

def add_exclamation(*args, **kwargs):
    return AddExclamation.as_decorator(*args, **kwargs)

@command()
@option("--message")
@strip()
@uppercase()
@add_exclamation()
def announce(message: str):
    print(message)

# Tree structure:
# announce (RootNode)
# └── message (ParentNode: Option)
#     ├── strip (ChildNode)
#     ├── uppercase (ChildNode)
#     └── add_exclamation (ChildNode)
```

### Visualizing Complex Trees

```python
from click_extended import command, group, option, argument

@group()
@option("--verbose", "-v", is_flag=True)
def cli(verbose: bool):
    """Main CLI group."""
    pass

@cli.command()
@option("--name", default="World")
@argument("count", type=int)
def greet(name: str, count: int):
    """Greet someone."""
    for _ in range(count):
        print(f"Hello, {name}!")

@cli.command()
@option("--force", "-f", is_flag=True)
@argument("filename")
def delete(filename: str, force: bool):
    """Delete a file."""
    print(f"Deleting {filename}")

cli.visualize()

# Output:
# cli
#   verbose
#   greet
#     name
#     count
#   delete
#     force
#     filename
```

## Error Handling

The `Tree` class raises specific exceptions during decorator processing. Understanding these helps diagnose issues with decorator ordering and structure:

### `RootNodeExistsError`

Raised when attempting to register a second root node. This typically indicates multiple `@command` or `@group` decorators on the same function.

### `ParentNodeExistsError`

Raised when attempting to register a parent with a duplicate name.

```python
@command()
@option("--name")
@option("--name")  # Raises ParentNodeExistsError
def cmd(name: str):
    pass
```

### `NoRootError`

Raised when attempting operations that require a root node before one is registered. This is an internal error that shouldn't occur during normal decorator usage.

### `NoParentError`

Raised when attempting to register a child without a recent parent node.

```python
@command()
@uppercase()  # Raises NoParentError (no parent to attach to)
def cmd():
    pass
```

### `InvalidChildOnTagError`

Raised when attempting to attach a transformation child node to a tag (tags only support validation nodes).

```python
@command()
@option("--username", tags="auth")
@option("--password", tags="auth")
@tag()
@uppercase()  # Raises InvalidChildOnTagError if attached to tag
def register(username: str, password: str):
    pass
```

## Implementation Details

### Decorator Order Reversal

When decorators execute, they apply bottom-to-top:

```python
@command()        # Step 3: Root registered, builds tree
@option("--name") # Step 2: Parent queued
@uppercase()      # Step 1: Child queued
def greet(name: str):
    pass
```

The `register_root()` method reverses the queue to process them top-to-bottom:

1. Retrieves pending nodes: `[("child", uppercase), ("parent", Option)]`
2. Reverses the list: `[("parent", Option), ("child", uppercase)]`
3. Processes in correct order: parent first, then child

### Recent Node Tracking

The `recent` and `recent_tag` attributes track the most recently registered parent or tag, ensuring child nodes attach to the correct parent:

```python
@command()
@option("--name")    # recent = "name" option
@uppercase()         # Attaches to "name"
@option("--email")   # recent = "email" option
@validate_email()    # Attaches to "email"
def cmd(name: str, email: str):
    pass
```

### Global Node Execution

Global nodes can be executed immediately or delayed:

- **Immediate** (`delay=False`): Executed during `register_root()`
- **Delayed** (`delay=True`): Executed when the command is invoked

```python
class MyGlobal(GlobalNode):
    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Access and modify tree structure
        pass

def my_global(*args, **kwargs):
    return MyGlobal.as_decorator(*args, **kwargs)

@my_global(delay=False)  # Executes during tree building
@command()
def cmd():
    pass
```

## See Also

- [ROOT_NODE.md](./ROOT_NODE.md) - CLI entry points (commands and groups)
- [PARENT_NODE.md](./PARENT_NODE.md) - Parameter value sources
- [CHILD_NODE.md](./CHILD_NODE.md) - Validators and transformers
- [GLOBAL_NODE.md](./GLOBAL_NODE.md) - Command groups
- [TAG.md](./TAG.md) - Cross-parameter validation
- [COMMAND.md](./COMMAND.md) - Single CLI commands
- [GROUP.md](./GROUP.md) - Command groups
