![Banner](../../assets/click-extended-documentation-banner.png)

# Argument Node

An `ArgumentNode` is an abstract extension of the [parent node](./PARENT_NODE.md) designed specifically for CLI positional arguments. It receives the parsed argument value directly in its `load()` method, allowing for value transformation, validation, or processing before injection into the command function.

## Table of Contents

- [Parameters](#parameters)
- [Methods](#methods)

## Parameters

Parameters of the `ArgumentNode` as set in the `as_decorator()` method where the class is initialized.

| Name       | Type                  | Default                              | Description                                                                                                  |
| ---------- | --------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| name       | str                   |                                      | The name of the argument node, used as the parameter name unless `param` is set (converted to `snake_case`). |
| param      | str                   | The `name` parameter in `snake_case` | The parameter name to inject the value as in the function.                                                   |
| type       | str, int, float, bool | `str`                                | The type of the argument value.                                                                              |
| nargs      | int                   | `1`                                  | The number of arguments to accept. When `nargs > 1` or `nargs = -1`, creates a container tuple.              |
| help       | str                   |                                      | The help string to display in the help menu.                                                                 |
| required   | bool                  | `True`                               | Whether the argument is required.                                                                            |
| default    | str, int, float, bool |                                      | The default value to use, this sets `required=False` even if `required=True`.                                |
| tags       | str, list[str]        |                                      | A string or list of strings of tags to tag the argument node with.                                           |
| \*args     | Any                   |                                      | Optional positional arguments passed to the `load()` method.                                                 |
| \*\*kwargs | Any                   |                                      | Optional keyword arguments passed to the `load()` method.                                                    |

### Container Tuples

When `nargs > 1` or `nargs = -1` (unlimited), the argument produces a **container tuple**. Container tuples are automatically processed element-wise by child nodes:

- Each element is passed individually to the appropriate type handler (`handle_int`, `handle_str`, etc.)
- The tuple structure is preserved in the final result
- Errors include index paths showing where in the tuple the error occurred (e.g., `[0]`, `[2]`)

## Methods

### load()

The method used for injecting the value into the context. It receives the value from the `click.Argument` instance and should return the value to be injected into the context (either to the first child or the function itself). Returning no value or `None` will inject `None` as the value.

#### Parameters

| Name       | Type                        | Description                                                 |
| ---------- | --------------------------- | ----------------------------------------------------------- |
| self       | Self                        | Reference to the current instance.                          |
| value      | str, int, float, bool, None | The parsed option value from the `click.Argument` instance. |
| context    | Context                     | The current context instance.                               |
| \*args     | Any                         | Optional positional arguments.                              |
| \*\*kwargs | Any                         | Optional keyword arguments.                                 |

#### Returns

##### Any

The processed value to inject into the first child or the function itself.
