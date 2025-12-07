![Banner](../../assets/click-extended-documentation-banner.png)

# Tag Node

A `Tag` node is a special node used for grouping multiple [ParentNodes](./PARENT_NODE.md) together. Tags allow you to apply [ChildNodes](./CHILD_NODE.md) to multiple parents at once and perform cross-node validation or transformation.

## Table of Contents

- [Usage](#usage)
- [Methods](#methods)

## Usage

Tags are applied using the `@tag` decorator. Any parent node (Argument, Option, Env) that references the tag name in its `tags` parameter will be associated with that tag.

```python
from click_extended import command, option, tag
from click_extended.decorators import to_upper_case

@command()
@option("username", tags="login")
@option("password", tags="login")
@option("method")
@tag("login")
@requires("method")
def cli(*args, **kwargs):
    ...

if __name__ == "__main__":
    cli()
```

```bash
$ python cli.py --opt1 "hello" --opt2 "world"
```

## Methods

### get_value()

Get a dictionary of values from all parent nodes associated with this tag.

#### Returns

##### dict[str, Any]

Dictionary mapping parameter names to their values. Keys are parent node names, values are the processed values (or `None` if not provided).

### get_provided_values()

Get the names of all ParentNodes in this tag that were provided by the user.

#### Returns

##### list[str]

List of parameter names that were provided.
