![Banner](../../assets/click-extended-documentation-banner.png)

# Context

The context is a data structure available inside any context and is initialized in the tree. It contains information about the current context with properties for accessing other nodes, a data store, and more. It also contains helper methods for checks, comparisons, and more.

## Table of Contents

- [Usage](#usage)
- [Data Store](#data-store)
- [Properties](#properties)
- [Methods](#methods)

## Usage

As the context is available in the tree, you can access it from anywhere. It is directly accessible from _handlers_, but also accessible from the tree.

With access to the `Context` instance, you can now access properties such as `children`, `parents`, and `data`. This allows you to fully visualize the tree and access all other nodes, as well as access the custom data store.

The context also includes helpers methods for querying the context, filtering the context, and performing various other actions.

## Data Store

The data store is a special property of the context. This allows data sharing between nodes. The `context.data` is a dictionary, allowing you to use it like any other dictionary in Python.

### Setting Data

```python
context.data["my_key"] = "value"
```

### Getting Data

```python
value = context.data.get("my_key", None)
```

```python
value = context.data["my_key"]
```

## Properties

| Name          | Type                        | Description                                                            |
| ------------- | --------------------------- | ---------------------------------------------------------------------- |
| root          | `RootNode`                  | The root node of the current context.                                  |
| parent        | `ParentNode`, `Tag`, `None` | The parent node if the current node is a `ChildNode`.                  |
| child         | `ChildNode`, `None`         | A reference to the current child if the current node is a `ChildNode`. |
| click_context | `click.Context`             | The underlying `Click` context.                                        |
| nodes         | `dict[str, Node]`           | A dictionary with all registered nodes in the tree.                    |
| parents       | `dict[str, ParentNode]`     | A dictionary with all registered parent nodes in the tree.             |
| tags          | `dict[str, Tag]`            | A dictionary with all registered tag nodes in the tree.                |
| children      | `dict[str, ChildNode]`      | A dictionary with all registered child nodes in the tree.              |
| globals       | `dict[str, GlobalNode]`     | A dictionary with all registered global nodes in the tree.             |
| data          | dict[str, Any]              | The custom data store used for inter-node-communication.               |
| debug         | bool                        | Whether the application is running in debug mode.                      |

## Methods

| Name                             | Returns                       | Description                                                                                                               |
| -------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `get_root()`                     | `RootNode`                    | Get the root node.                                                                                                        |
| `get_children(name: str)`        | `list[ChildNode]`             | Get a list of all children defined under the same parent, if `name` is not provided, uses the current parent.             |
| `get_siblings()`                 | `list[ChildNode]`             | Get a list of all siblings in the current parent, excluding the current child.                                            |
| `get_parent(name: str)`          | `ParentNode`, `None`          | Get a `ParentNode` with the name if exists.                                                                               |
| `get_global(name: str)`          | `GlobalNode`, `None`          | Get a `GlobalNode` with the name if exists.                                                                               |
| `get_node(name: str)`            | `Node`, `None`                | Get a `Node` with the name if exists.                                                                                     |
| `get_tag(name: str)`             | `Tag`, `None`                 | Get a `Tag` with the name if exists.                                                                                      |
| `get_tagged()`                   | `dict[str, list[ParentNode]]` | Get a dictionary of tagged `ParentNode` instances.                                                                        |
| `get_values()`                   | `dict[str, Any]`              | Get the processed value of all source nodes.                                                                              |
| `get_provided_arguments()`       | `list[Argument]`              | Get all provided positional arguments.                                                                                    |
| `get_provided_options()`         | `list[Option]`                | Get all provided keyword arguments.                                                                                       |
| `get_provided_envs()`            | `list[Env]`                   | Get all provided environment variables.                                                                                   |
| `get_provided_value(name: str)`  | `Any`                         | Get the provided value of a parent node.                                                                                  |
| `get_provided_values()`          | `dict[str, Any]`              | Get the provided values in the context.                                                                                   |
| `get_missing_arguments()`        | `list[Argument]`              | Get all missing positional arguments.                                                                                     |
| `get_missing_options()`          | `list[Option]`                | Get all missing keyword arguments.                                                                                        |
| `get_missing_envs()`             | `list[Env]`                   | Get all missing environment variables.                                                                                    |
| `get_current_tags()`             | `list[str]`                   | Get a list of the tags of the current node.                                                                               |
| `get_current_parent_as_parent()` | `ParentNode`                  | Get the current parent as a `ParentNode`. Raises `RuntimeError` if called outside a `ChildNode` or the parent is a `Tag`. |
| `get_current_parent_as_tag()`    | `Tag`                         | Get the current parent as a `Tag`. Raises `RuntimeError` if called outside a `ChildNode` or the parent is a `ParentNode`. |
