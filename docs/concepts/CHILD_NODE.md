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

TBD
