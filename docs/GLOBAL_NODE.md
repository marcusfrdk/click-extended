![Banner](../assets/click-extended-documentation-banner.png)

# Global Node

The `GlobalNode` is a base class for tree-level observation and value injection in `click-extended`. It provides access to the entire command structure, allowing you to implement cross-parameter logic, inject computed values, store shared data, and observe the full context of your CLI application.

## Overview

A `GlobalNode` operates at the tree level, giving it visibility into all aspects of your CLI command. It can:

- **Observe the Tree**: Access all parameters, tags, and structure
- **Inject Values**: Compute and inject values into your command function
- **Share Data**: Use the tree's custom data storage for inter-node communication
- **Execute at Different Times**: Run early (during tree building) or late (before function call)
- **Access Everything**: See root node, parent nodes, tags, other globals, and call arguments

## Architecture

### Execution Timing

Global nodes can execute at two different points:

1. **Early Execution** (`delay=False`, default)

   - Runs during `register_root()` after tree structure is built (at the point where you declare it)
   - Occurs before command is invoked
   - Cannot access CLI call arguments
   - Useful for validation, configuration, setup

2. **Late Execution** (`delay=True`)
   - Runs just before the command function is called (after the entire tree is declared, regardless of where the node is declared)
   - Has access to CLI call arguments
   - Can modify or inject final values
   - Useful for runtime computation, logging, late validation

### Operation Modes

Global nodes operate in two modes based on the `name` parameter:

1. **Observer Mode** (`name=None`)

   - Executes logic without injecting values
   - Return value is ignored
   - Useful for logging, validation, side effects

2. **Injection Mode** (`name="var"`)
   - Executes logic and injects return value into function
   - Return value becomes a parameter in the command function
   - Useful for computed values, context injection (operates like a parent node without the ability to apply children)

## Parameters

When creating a `GlobalNode`:

| Name    | Description                                                                   | Type        | Required | Default |
| ------- | ----------------------------------------------------------------------------- | ----------- | -------- | ------- |
| `name`  | Parameter name to inject return value into. If `None`, runs in observer mode. | str \| None | No       | None    |
| `delay` | Whether to delay execution until just before function call.                   | bool        | No       | False   |

## Methods

### `process(tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs) -> Any`

Execute the global node logic. Must be implemented by subclasses.

**Parameters:**

- `tree` (Tree): The tree instance containing all structure and data
- `root` (RootNode): The root node (Command or Group)
- `parents` (list[ParentNode]): List of all ParentNode instances (Option, Argument, Env)
- `tags` (dict[str, Tag]): Dictionary mapping tag names to Tag instances
- `globals` (list[GlobalNode]): List of all GlobalNode instances (including self)
- `call_args` (tuple): Positional arguments passed to the Click command
- `call_kwargs` (dict): Keyword arguments passed to the Click command
- `*args` (Any): Additional positional arguments from `as_decorator`
- `**kwargs` (Any): Additional keyword arguments from `as_decorator`

**Returns:**

- Any: If `name` is set, this value will be injected into the function (including `None`). If `name` is `None`, return value is ignored.

```python
from click_extended.core import GlobalNode

class MyGlobal(GlobalNode):
    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Access tree data
        version = tree.get_data("version")

        # Inspect parents
        for parent in parents:
            if parent.was_provided():
                print(f"{parent.name} was provided")

        # Return value for injection (if name was set)
        return {"computed": "data"}
```

### `as_decorator(name=None, /, delay=False, **kwargs)` (classmethod)

Create a decorator from the global node class. Arguments are stored and passed to `process()`.

**Parameters:**

- `name` (str | None): Parameter name to inject return value into. If `None`, runs in observer mode.
- `delay` (bool): Whether to delay execution until just before function call. Defaults to `False`.
- `**kwargs` (Any): Additional keyword arguments passed to `process()` method

**Returns:**

- Callable: A decorator function that registers the global node

```python
def my_global(name=None, /, delay=False, **kwargs):
    """Create a global decorator."""
    return MyGlobal.as_decorator(name, delay=delay, **kwargs)

@command()
@my_global("config", delay=True)
def app(config: dict):
    print(config)
```

## Examples

### Observer Mode - Logging All Parameters

```python
from click_extended import command, option
from click_extended.core import GlobalNode

class LogParameters(GlobalNode):
    """Log all parameters that were provided."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        print(f"Command: {root.name}")
        print("Provided parameters:")
        for parent in parents:
            if parent.was_provided():
                value = parent.get_value(tags, call_args, call_kwargs)
                print(f"  {parent.name} = {value}")

def log_parameters(*args, **kwargs):
    """Log all provided parameters."""
    return LogParameters.as_decorator(None, *args, **kwargs)

@command()
@option("--name", default="World")
@option("--count", type=int, default=1)
@log_parameters()
def greet(name: str, count: int):
    """Greet someone."""
    for _ in range(count):
        print(f"Hello, {name}!")

# Usage: python app.py --name Alice --count 3
# Output:
# Command: greet
# Provided parameters:
#   name = Alice
#   count = 3
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

### Injection Mode - Provide Configuration

```python
from click_extended import command, option
from click_extended.core import GlobalNode
import json
from pathlib import Path

class LoadConfig(GlobalNode):
    """Load configuration from file and inject it."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        config_path = kwargs.get("config_path", "config.json")

        if Path(config_path).exists():
            with open(config_path) as f:
                return json.load(f)

        return {}  # Default empty config

def load_config(name, /, **kwargs):
    """Load configuration from file."""
    return LoadConfig.as_decorator(name, **kwargs)

@command()
@option("--verbose", is_flag=True)
@load_config("config", config_path="app_config.json")
def app(config: dict, verbose: bool):
    """Run the application with config."""
    if verbose:
        print(f"Loaded config: {config}")

    print(f"App version: {config.get('version', 'unknown')}")
```

### Early Execution - Validate Environment

```python
from click_extended import command, option
from click_extended.core import GlobalNode
import os

class ValidateEnvironment(GlobalNode):
    """Validate required environment variables exist."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        required_vars = kwargs.get("required", [])

        missing = [var for var in required_vars if var not in os.environ]

        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

def validate_environment(**kwargs):
    """Validate required environment variables."""
    return ValidateEnvironment.as_decorator(None, delay=False, **kwargs)

@command()
@option("--database")
@validate_environment(required=["DATABASE_URL", "API_KEY"])
def connect(database: str):
    """Connect to database."""
    print(f"Connecting to {database}")

# Fails early if DATABASE_URL or API_KEY not set
```

### Late Execution - Access Call Arguments

```python
from click_extended import command, option, argument
from click_extended.core import GlobalNode
from datetime import datetime

class LogExecution(GlobalNode):
    """Log command execution with arguments."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "command": root.name,
            "args": call_args,
            "kwargs": call_kwargs,
        }

        print(f"[{timestamp}] Executing {root.name}")

        # Store in tree data for other nodes to access
        tree.set_data("execution_log", log_entry)

def log_execution(*args, **kwargs):
    """Log command execution."""
    return LogExecution.as_decorator(None, delay=True, *args, **kwargs)

@command()
@option("--output", type=str)
@argument("input_file")
@log_execution()
def process(input_file: str, output: str):
    """Process a file."""
    print(f"Processing {input_file}")
    if output:
        print(f"Writing to {output}")
```

### Using Tree Data Storage

```python
from click_extended import command, option
from click_extended.core import GlobalNode

class StoreMetadata(GlobalNode):
    """Store metadata in tree for other nodes."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Store data in tree
        tree.set_data("app_version", "1.0.0")
        tree.set_data("environment", "production")

        return None

def store_metadata(*args, **kwargs):
    """Store application metadata."""
    return StoreMetadata.as_decorator(None, delay=False, *args, **kwargs)

class InjectMetadata(GlobalNode):
    """Inject metadata from tree."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Retrieve data from tree
        version = tree.get_data("app_version")
        env = tree.get_data("environment")

        return {
            "version": version,
            "environment": env,
        }

def inject_metadata(name, /, *args, **kwargs):
    """Inject application metadata."""
    return InjectMetadata.as_decorator(name, delay=False, *args, **kwargs)

@command()
@option("--verbose", is_flag=True)
@store_metadata()
@inject_metadata("metadata")
def app(metadata: dict, verbose: bool):
    """Application with metadata."""
    print(f"Version: {metadata['version']}")
    print(f"Environment: {metadata['environment']}")
```

### Cross-Parameter Validation

```python
from click_extended import command, option
from click_extended.core import GlobalNode
from click_extended.errors import ValidationError

class ValidateMutuallyExclusive(GlobalNode):
    """Validate that mutually exclusive options aren't both provided."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        exclusive_groups = kwargs.get("groups", [])

        for group in exclusive_groups:
            provided = [
                name for name in group
                if any(p.name == name and p.was_provided() for p in parents)
            ]

            if len(provided) > 1:
                raise ValidationError(
                    f"Options {', '.join(provided)} are mutually exclusive"
                )

        return None

def validate_exclusive(**kwargs):
    """Validate mutually exclusive options."""
    return ValidateMutuallyExclusive.as_decorator(None, delay=False, **kwargs)

@command()
@option("--json", is_flag=True)
@option("--yaml", is_flag=True)
@option("--xml", is_flag=True)
@validate_exclusive(groups=[["json", "yaml", "xml"]])
def export(json: bool, yaml: bool, xml: bool):
    """Export data in specified format."""
    if json:
        print("Exporting as JSON")
    elif yaml:
        print("Exporting as YAML")
    elif xml:
        print("Exporting as XML")

# Raises error if more than one format is specified
```

### Accessing Tags

```python
from click_extended import command, option
from click_extended.core import GlobalNode
from click_extended.errors import ValidationError

class ValidateAuth(GlobalNode):
    """Validate authentication parameters."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        auth_tag = tags.get("auth")

        if not auth_tag:
            return None

        provided = auth_tag.get_provided_values()

        # Ensure both username and password are provided
        if "username" in provided and "password" not in provided:
            raise ValidationError("Password required when username is provided")

        if "password" in provided and "username" not in provided:
            raise ValidationError("Username required when password is provided")

        return None

def validate_auth(*args, **kwargs):
    """Validate authentication parameters."""
    return ValidateAuth.as_decorator(None, delay=False, *args, **kwargs)

@command()
@option("--username", tags="auth")
@option("--password", tags="auth", hide_input=True)
@option("--api-key", tags="auth")
@validate_auth()
def login(username: str, password: str, api_key: str):
    """Login to the service."""
    if username and password:
        print(f"Logging in as {username}")
    elif api_key:
        print("Logging in with API key")
```

### Multiple Globals with Dependencies

```python
from click_extended import command, option
from click_extended.core import GlobalNode

class LoadDatabase(GlobalNode):
    """Connect to database and store connection."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Simulate database connection
        db_connection = {"connected": True, "db": "myapp"}

        # Store for other globals to use
        tree.set_data("db_connection", db_connection)

        # Also inject into function
        return db_connection

def load_database(name, /, *args, **kwargs):
    """Load database connection."""
    return LoadDatabase.as_decorator(name, delay=False, *args, **kwargs)

class LoadUser(GlobalNode):
    """Load user from database using stored connection."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Get database connection from tree
        db = tree.get_data("db_connection")

        if not db:
            raise RuntimeError("Database not connected")

        # Simulate user loading
        user = {"id": 1, "name": "Alice", "db": db["db"]}

        return user

def load_user(name, /, *args, **kwargs):
    """Load user from database."""
    return LoadUser.as_decorator(name, delay=False, *args, **kwargs)

@command()
@option("--user-id", type=int)
@load_database("db")
@load_user("current_user")
def dashboard(db: dict, current_user: dict, user_id: int):
    """Show user dashboard."""
    print(f"Database: {db['db']}")
    print(f"User: {current_user['name']}")
    if user_id:
        print(f"Viewing user: {user_id}")
```

### Conditional Injection Based on Options

```python
from click_extended import command, option
from click_extended.core import GlobalNode

class ConditionalConfig(GlobalNode):
    """Load different config based on environment option."""

    def process(self, tree, root, parents, tags, globals, call_args, call_kwargs, *args, **kwargs):
        # Find the environment option
        env = None
        for parent in parents:
            if parent.name == "environment" and parent.was_provided():
                env = parent.get_value(tags, call_args, call_kwargs)
                break

        # Load different config based on environment
        configs = {
            "dev": {"debug": True, "db": "localhost"},
            "prod": {"debug": False, "db": "prod.example.com"},
        }

        return configs.get(env, configs["dev"])

def conditional_config(name, /, *args, **kwargs):
    """Load configuration based on environment."""
    return ConditionalConfig.as_decorator(name, delay=False, *args, **kwargs)

@command()
@option("--environment", type=str, default="dev")
@conditional_config("config")
def app(environment: str, config: dict):
    """Run application with environment-specific config."""
    print(f"Environment: {environment}")
    print(f"Debug: {config['debug']}")
    print(f"Database: {config['db']}")
```

## Implementation

To create a new `GlobalNode` subclass, implement the abstract `process()` method:

### Step 1: Create the GlobalNode Subclass

```python
from typing import Any
from click_extended.core import GlobalNode, Tree, RootNode, ParentNode, Tag

class CustomGlobal(GlobalNode):
    """Custom global node logic."""

    def process(
        self,
        tree: Tree,
        root: RootNode,
        parents: list[ParentNode],
        tags: dict[str, Tag],
        globals: list[GlobalNode],
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Execute custom logic.

        Args:
            tree (Tree):
                The tree instance.
            root (RootNode):
                The root node.
            parents (list[ParentNode]):
                All parent nodes.
            tags (dict[str, Tag]):
                All tag instances.
            globals (list[GlobalNode]):
                All global nodes (including self).
            call_args (tuple[Any, ...]):
                CLI positional arguments.
            call_kwargs (dict[str, Any]):
                CLI keyword arguments.
            *args (Any):
                Additional positional arguments.
            **kwargs (Any):
                Additional keyword arguments.

        Returns:
            Any:
                Value to inject (if name was set) or `None`.
        """
        # Your logic here
        return {"result": "data"}
```

### Step 2: Create Intermediate Decorator Function

```python
def custom_global(name=None, /, delay=False, **kwargs):
    """Create a custom global decorator."""
    return CustomGlobal.as_decorator(name, delay=delay, **kwargs)
```

### Step 3: Use as Decorator

```python
from click_extended import command, option

# Observer mode
@command()
@option("--verbose", is_flag=True)
@custom_global()
def app(verbose: bool):
    print("Running app")

# Injection mode
@command()
@option("--verbose", is_flag=True)
@custom_global("data", delay=True)
def app(data: dict, verbose: bool):
    print(f"Data: {data}")
```

### Complete Example: Request Logger

```python
from typing import Any
from click_extended import command, option, argument
from click_extended.core import GlobalNode, Tree, RootNode, ParentNode, Tag
from datetime import datetime
import json
from pathlib import Path

class RequestLogger(GlobalNode):
    """Log all command invocations to a file."""

    def process(
        self,
        tree: Tree,
        root: RootNode,
        parents: list[ParentNode],
        tags: dict[str, Tag],
        globals: list[GlobalNode],
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Log command execution details to file.

        Returns:
            dict:
                Log entry with metadata.
        """
        log_file = kwargs.get("log_file", "commands.log")

        # Collect parameter values
        params = {}
        for parent in parents:
            if parent.was_provided():
                try:
                    value = parent.get_value(tags, call_args, call_kwargs)
                    params[parent.name] = value
                except Exception:
                    params[parent.name] = "<error>"

        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": root.name,
            "parameters": params,
            "cli_args": list(call_args),
            "cli_kwargs": dict(call_kwargs),
        }

        # Append to log file
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Store in tree for access by other nodes
        tree.set_data("last_log_entry", log_entry)

        # Return for injection if name was provided
        return log_entry

def request_logger(name=None, /, delay=True, **kwargs):
    """
    Log command invocations to file.

    Args:
        name (str | None):
            Parameter name to inject log entry (optional).
        delay (bool):
            Whether to delay until just before function call.
        log_file (str):
            Path to log file (default: "commands.log").
    """
    return RequestLogger.as_decorator(name, delay=delay, **kwargs)

@command()
@option("--output", type=str)
@option("--verbose", is_flag=True)
@argument("input_file")
@request_logger(log_file="app.log")
def process(input_file: str, output: str, verbose: bool):
    """Process a file with logging."""
    if verbose:
        print(f"Processing {input_file}")

    if output:
        print(f"Writing to {output}")

# Usage: python app.py input.txt --output out.txt --verbose
# Creates app.log with:
# {"timestamp": "2024-...", "command": "process", "parameters": {...}, ...}
```

## See Also

- [TREE.md](./TREE.md) - Tree structure and data storage
- [ROOT_NODE.md](./ROOT_NODE.md) - CLI entry points
- [PARENT_NODE.md](./PARENT_NODE.md) - Parameter value sources
- [CHILD_NODE.md](./CHILD_NODE.md) - Validators and transformers
- [TAG.md](./TAG.md) - Cross-parameter validation
