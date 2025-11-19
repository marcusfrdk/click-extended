![Banner](../assets/click-extended-documentation-banner.png)

# Child Node

The `ChildNode` is the base class for parameter validators and transformers in click-extended. It provides the foundation for processing parameter values through a chain of operations, enabling validation, transformation, and custom logic to be applied to CLI parameter values before they reach your command function.

## Overview

A `ChildNode` represents a single processing step in a parameter's value chain. It orchestrates:

- **Value Transformation**: Modify parameter values (uppercase, format, convert types, etc.)
- **Value Validation**: Verify parameter values meet requirements (raise errors if invalid)
- **Sequential Processing**: Chain multiple operations in order
- **Context Awareness**: Access sibling nodes, tags, and parent information
- **Flexible Arguments**: Support custom arguments passed to the processing logic

## Architecture

### Processing Chain

Child nodes are attached to `ParentNode` instances and process values sequentially:

```text
Raw Value -> ChildNode 1 -> ChildNode 2 -> ChildNode 3 -> Final Value
```

Each child node receives:

- The current value from the previous node (or raw value if first)
- Information about sibling nodes
- Access to tags for cross-parameter validation
- Reference to the parent node

### Validation vs Transformation

**Transformation Nodes**: Return a modified value

```python
from click_extended.types import ProcessContext

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()
```

**Validation Nodes**: Return `None` or nothing to preserve the value, or raise exceptions

```python
from click_extended.types import ProcessContext

class ValidateLength(ChildNode):
    def process(self, value, context: ProcessContext):
        if len(value) < 3:
            raise ValueError("Too short")
```

## Parameters

When creating a `ChildNode`:

| Name             | Description                                             | Type  | Required | Default |
| ---------------- | ------------------------------------------------------- | ----- | -------- | ------- |
| `name`           | The name of the node.                                   | str   | Yes      | -       |
| `process_args`   | Positional arguments to pass to the `process()` method. | tuple | No       | ()      |
| `process_kwargs` | Keyword arguments to pass to the `process()` method.    | dict  | No       | {}      |

## Type Hints and Type Safety

click-extended uses type hints from the `process()` method to provide type safety:

1. **Automatic Type Validation**: The type hint on the `value` parameter determines which parent types are supported:

   ```python
   class IsPositive(ChildNode):
       """Validator for positive numbers."""

       def process(self, value: int | float, context: ProcessContext):
           if value <= 0:
               raise ValueError("Value must be positive")
   ```

   This validator automatically rejects non-numeric types at registration time.

2. **No Type Hint = Accept All Types**:

   ```python
   class LogValue(ChildNode):
       """Log any value."""

       def process(self, value, context: ProcessContext):
           print(f"Value: {value}")
   ```

3. **Union Types**: Use union syntax to support multiple types:

   ```python
   class FormatNumber(ChildNode):
       """Format numeric values."""

       def process(self, value: int | float, context: ProcessContext):
           return f"{value:,.2f}"
   ```

## Missing Values

Command line interfaces are never predictable in terms of missing values. The child node handles this using type hints:

1. **Skip None by Default**: If `None` is not in the type hint, the `process()` method is skipped for `None` values:

   ```python
   # Process is not called if the value is None
   class MyValidator(ChildNode):
       """My custom validator."""

       def process(self, value: int | float, context: ProcessContext):
           if value <= 0:
               raise ValueError("Value must be positive")
   ```

2. **Accept None**: Add `None` to the type hint to handle missing values explicitly:

   ```python
   # Process is called even if the value is None
   class MyValidator(ChildNode):
       """My custom validator."""

       def process(self, value: int | float | None, context: ProcessContext):
           if value is None:
               raise ValueError("Value must be provided")
           if value <= 0:
               raise ValueError("Value must be positive")
   ```

3. **No Type Hint**: Without a type hint, `None` values are skipped by default:

   ```python
   class MyTransform(ChildNode):
       """Transform any non-None value."""

       def process(self, value, context: ProcessContext):
           # This is only called for non-None values
           return str(value).upper()
   ```

## Methods

### `process(value, context: ProcessContext) -> Any`

Process and return the transformed/validated value. Must be implemented by subclasses.

**Parameters:**

- `value` (Any): The current value from the previous node or raw source
- `context` (ProcessContext): Context object containing:

  - `context.parent` (ParentNode | Tag): The parent node this child is attached to
  - `context.siblings` (list[str]): Class names of all sibling child nodes
  - `context.tags` (dict[str, Tag]): Dictionary of tag instances for cross-parameter access
  - `context.args` (tuple[Any, ...]): Additional positional arguments from `process_args`
  - `context.kwargs` (dict[str, Any]): Additional keyword arguments from `process_kwargs`

  **Helper Methods:**

  - `context.is_tag()`: Check if parent is a Tag
  - `context.is_option()`: Check if parent is an Option
  - `context.is_argument()`: Check if parent is an Argument
  - `context.is_env()`: Check if parent is an Env
  - `context.get_tag_values()`: Get dictionary of tag parent node values (only for tags)

**Returns:**

- Transformed value, or
- `None` to preserve current value (validation only), or
- Raises exception to indicate validation failure

```python
from click_extended import ChildNode, ProcessContext

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()
```

### `as_decorator(*args, **kwargs)` (classmethod)

Create a decorator from the child node class. Arguments are stored and passed to `process()`.

```python
def uppercase(*args, **kwargs):
    """Convert value to uppercase."""
    return Uppercase.as_decorator(*args, **kwargs)

@command()
@option("--name")
@uppercase()
def greet(name: str):
    print(f"Hello, {name}!")
```

## Examples

### Basic Transformation

```python
from click_extended import command, option, ChildNode, ProcessContext

class Uppercase(ChildNode):
    """Transform value to uppercase."""

    def process(self, value, context: ProcessContext):
        return value.upper() if value else value

def uppercase(*args, **kwargs):
    """Convert value to uppercase."""
    return Uppercase.as_decorator(*args, **kwargs)

@command()
@option("--name")
@uppercase()
def greet(name: str):
    """Name will be automatically uppercased."""
    print(f"Hello, {name}!")

# Usage: python script.py --name john
# Output: Hello, JOHN!
```

### Basic Validation

```python
from click_extended import command, option, ChildNode, ProcessContext

class ValidateLength(ChildNode):
    """Validate value length."""

    def process(self, value, context: ProcessContext):
        if len(value) < 3:
            raise ValueError("Value must be at least 3 characters")
        return None

def validate_length(*args, **kwargs):
    """Validate value length."""
    return ValidateLength.as_decorator(*args, **kwargs)

@command()
@option("--username")
@validate_length()
def register(username: str):
    """Register with validated username."""
    print(f"Registered: {username}")

# Usage: python script.py --username ab
# Error: Value must be at least 3 characters
```

### Transformation with Arguments

```python
from click_extended import command, option, ChildNode, ProcessContext

class Multiply(ChildNode):
    """Multiply value by a factor."""

    def process(self, value, context: ProcessContext):
        factor = context.args[0] if context.args else 1
        return value * factor

def multiply(*args, **kwargs):
    """Multiply value by a factor."""
    return Multiply.as_decorator(*args, **kwargs)

@command()
@option("--count", type=int, default=1)
@multiply(3)
def repeat(count: int):
    """Count will be multiplied by 3."""
    print(f"Repeating {count} times")

# Usage: python script.py --count 5
# Output: Repeating 15 times
```

### Transformation with Keyword Arguments

```python
from click_extended import command, option, ChildNode, ProcessContext

class AddPrefix(ChildNode):
    """Add prefix to value."""

    def process(self, value, context: ProcessContext):
        prefix = context.kwargs.get("prefix", "")
        return f"{prefix}{value}"

def add_prefix(*args, **kwargs):
    """Add prefix to value."""
    return AddPrefix.as_decorator(*args, **kwargs)

@command()
@option("--message")
@add_prefix(prefix="[INFO] ")
def log(message: str):
    """Message will have prefix added."""
    print(message)

# Usage: python script.py --message "Hello"
# Output: [INFO] Hello
```

### Multiple Child Nodes (Chaining)

```python
from click_extended import command, option, ChildNode, ProcessContext

class Strip(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.strip()

def strip(*args, **kwargs):
    """Strip whitespace from value."""
    return Strip.as_decorator(*args, **kwargs)

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()

def uppercase(*args, **kwargs):
    """Convert value to uppercase."""
    return Uppercase.as_decorator(*args, **kwargs)

class AddExclamation(ChildNode):
    def process(self, value, context: ProcessContext):
        return f"{value}!"

def add_exclamation(*args, **kwargs):
    """Add exclamation mark to value."""
    return AddExclamation.as_decorator(*args, **kwargs)

@command()
@option("--text")
@strip()
@uppercase()
@add_exclamation()
def shout(text: str):
    """Transform text through multiple steps."""
    print(text)

# Usage: python script.py --text "  hello  "
# Flow: "  hello  " -> "hello" -> "HELLO" -> "HELLO!"
# Output: HELLO!
```

### Validation and Transformation Combined

```python
from click_extended import command, option, ChildNode, ProcessContext

class ValidatePositive(ChildNode):
    """Validate number is positive."""

    def process(self, value, context: ProcessContext):
        if value <= 0:
            raise ValueError("Number must be positive")
        return None  # Preserve value

def validate_positive(*args, **kwargs):
    """Validate number is positive."""
    return ValidatePositive.as_decorator(*args, **kwargs)

class Round(ChildNode):
    """Round to specified decimal places."""

    def process(self, value, context: ProcessContext):
        places = context.args[0] if context.args else 0
        return round(value, places)

def round_decimal(*args, **kwargs):
    """Round to specified decimal places."""
    return Round.as_decorator(*args, **kwargs)

@command()
@option("--price", type=float)
@validate_positive()
@round_decimal(2)
def set_price(price: float):
    """Set price with validation and rounding."""
    print(f"Price: ${price:.2f}")

# Usage: python script.py --price 19.996
# Output: Price: $20.00
```

### Using Siblings Information

```python
from click_extended import command, option, ChildNode, ProcessContext

class LogSiblings(ChildNode):
    """Log information about sibling nodes."""

    def process(self, value, context: ProcessContext):
        print(f"Sibling nodes: {', '.join(context.siblings)}")
        return value

def log_siblings(*args, **kwargs):
    """Log information about sibling nodes."""
    return LogSiblings.as_decorator(*args, **kwargs)

class Uppercase(ChildNode):
    def process(self, value, context: ProcessContext):
        return value.upper()

def uppercase(*args, **kwargs):
    """Convert value to uppercase."""
    return Uppercase.as_decorator(*args, **kwargs)

@command()
@option("--name")
@log_siblings()
@uppercase()
def test(name: str):
    print(f"Result: {name}")

# Output: Sibling nodes: Uppercase
# Result: JOHN
```

### Cross-Parameter Validation with Tags

```python
from click_extended import command, option, ChildNode, ProcessContext

class ValidatePassword(ChildNode):
    """Validate password requirements."""

    def process(self, value, context: ProcessContext):
        auth_tag = context.tags.get("auth")
        if auth_tag:
            provided = auth_tag.get_provided_values()
            username = provided.get("username")

            if username and value == username:
                raise ValueError("Password cannot be same as username")

        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")

def validate_password(*args, **kwargs):
    """Validate password requirements."""
    return ValidatePassword.as_decorator(*args, **kwargs)

@command()
@option("--username", tags="auth")
@option("--password", tags="auth")
@validate_password()
def register(username: str, password: str):
    """Register with validated credentials."""
    print("Registration successful!")

# Usage: python script.py --username john --password john
# Error: Password cannot be same as username
```

### Checking Parent Information

```python
from click_extended import command, option, ChildNode, ProcessContext
from click_extended.core.tag import Tag

class CheckIfProvided(ChildNode):
    """Only process if value was explicitly provided."""

    def process(self, value, context: ProcessContext):
        if isinstance(context.parent, Tag):
            return value

        if context.parent.was_provided():
            return value.upper()

        return value

def check_if_provided(*args, **kwargs):
    """Only process if value was explicitly provided."""
    return CheckIfProvided.as_decorator(*args, **kwargs)

@command()
@option("--name", default="guest")
@check_if_provided()
def greet(name: str):
    print(f"Hello, {name}!")

# Usage: python script.py
# Output: Hello, guest!

# Usage: python script.py --name john
# Output: Hello, JOHN!
```

## Implementation

To create a new `ChildNode` subclass, implement the abstract `process()` method:

### Step 1: Create the ChildNode Subclass

```python
from typing import Any
from click_extended import ChildNode, ProcessContext

class CustomTransform(ChildNode):
    """Custom transformation logic."""

    def process(
        self,
        value: Any,
        context: ProcessContext
    ) -> Any:
        """
        Transform the value.

        Args:
            value (Any):
                Current value from previous node.
            context (ProcessContext):
                Context object.

        Returns:
            Any:
                Transformed value or `None` to preserve.
        """
        return value.upper()
```

### Step 2: Use as a Decorator

```python
from click_extended import command, option

def custom_transform(*args, **kwargs):
    """Custom transformation logic."""
    return CustomTransform.as_decorator(*args, **kwargs)

@command()
@option("--text")
@custom_transform()
def process(text: str):
    print(text)
```

### Step 3: Add Custom Arguments (Optional)

```python
class CustomTransform(ChildNode):
    def process(self, value, context: ProcessContext):
        multiplier = context.kwargs.get("multiplier", 1)
        prefix = context.kwargs.get("prefix", "")
        return f"{prefix}{value * multiplier}"

def custom_transform(multiplier: int, prefix: str, *args, **kwargs):
    """Custom transformation logic."""
    return CustomTransform.as_decorator(*args, multiplier=multiplier, prefix=prefix, **kwargs)

@command()
@option("--text")
@custom_transform(3, prefix=">>> ")
def process(text: str):
    print(text)
```

### Complete Example: Port Validator

```python
from typing import Any
from click_extended import command, option, ChildNode, ProcessContext

class ValidatePort(ChildNode):
    """Validate port number range."""

    def process(
        self,
        value: Any,
        context: ProcessContext
    ) -> Any:
        """
        Validate port is in valid range.

        Raises:
            ValueError:
                If port is outside valid range (1024-65535).
        """
        if not isinstance(value, int):
            raise TypeError(f"Port must be an integer, got {type(value)}")

        min_port = context.kwargs.get("min_port", 1024)
        max_port = context.kwargs.get("max_port", 65535)

        if not (min_port <= value <= max_port):
            raise ValueError(
                f"Port must be between {min_port} and {max_port}, "
                f"got {value}"
            )

def validate_port(*args, **kwargs):
    """Validate port number range."""
    return ValidatePort.as_decorator(*args, **kwargs)

@command()
@option("--port", type=int, default=8000)
@validate_port(min_port=1024, max_port=65535)
def start_server(port: int):
    """Start server on validated port."""
    print(f"Server starting on port {port}")

# Usage: python script.py --port 80
# Error: Port must be between 1024 and 65535, got 80

# Usage: python script.py --port 8080
# Output: Server starting on port 8080
```

## See Also

- [PARENT_NODE.md](./PARENT_NODE.md) - Parameter value sources
- [OPTION.md](./OPTION.md) - Named command-line parameters
- [ARGUMENT.md](./ARGUMENT.md) - Positional command-line parameters
- [ENV.md](./ENV.md) - Environment variable parameters
- [TAG.md](./TAG.md) - Cross-parameter validation
- [ROOT_NODE.md](./ROOT_NODE.md) - CLI entry points
