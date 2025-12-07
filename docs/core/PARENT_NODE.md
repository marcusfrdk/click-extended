![Banner](../../assets/click-extended-documentation-banner.png)

# Parent Node

The `ParentNode` is the abstract base class for all parameter nodes in click-extended. It defines the common interface and behavior for nodes that inject values into command functions. Concrete parameter implementations like [argument](../nodes/ARGUMENT.md), [option](../nodes/OPTION.md), and [environment variables](../nodes/ENV.md) extend from `ParentNode`.

## Table of Contents

- [Parameters](#parameters)
- [Methods](#methods)

## Parameters

Parameters of the `ParentNode` are set in the `as_decorator()` method as this is where the class is initialized.

| Name       | Type           | Default                              | Description                                                                                                |
| ---------- | -------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| name       | str            |                                      | The name of the parent node, used as the parameter name unless `param` is set (converted to `snake_case`). |
| param      | str            | The `name` parameter in `snake_case` | The parameter name to inject the value as in the function.                                                 |
| help       | str            |                                      | The help string to display in the help menu.                                                               |
| required   | bool           | `True`                               | Whether the parent node is required, the returned value of the `load()` method cannot be `None`.           |
| default    | Any            |                                      | The default value to use, this sets `required=False` even if `required=True`.                              |
| tags       | str, list[str] |                                      | A string or list of strings of tags to tag the parent node with.                                           |
| \*\*kwargs | Any            |                                      | Optional keyword arguments passed to the `load()` method.                                                  |

## Methods

### load()

#### Parameters

| Name       | Type    | Description                        |
| ---------- | ------- | ---------------------------------- |
| self       | Self    | Reference to the current instance. |
| context    | Context | The current context instance.      |
| \*args     | Any     | Optional positional arguments.     |
| \*\*kwargs | Any     | Optional keyword arguments.        |

#### Returns

##### Any

The processed value to inject into the command function.
