![Banner](../assets/click-extended-banner.png)

# Tag

A tag is a decorator that groups multiple options, arguments, or environment variables together, allowing you to apply validation or logic across a set of parameters. Tags are useful for enforcing constraints like "at least one required" or "mutually exclusive" across grouped parameters.

## Parameters

| Name   | Description                                  | Type | Required | Default |
| ------ | -------------------------------------------- | ---- | -------- | ------- |
| `name` | The name of the tag for grouping parameters. | str  | Yes      |         |

> [!NOTE]
> Tags can only have validation-only child nodes (nodes that return `None` or don't transform values). Transformation children cannot be attached to tags.

## Methods

### `.get_provided_values()`

Get the names of all parameters in this tag that were provided by the user. It returns a list of parameter names that were provided.

```python
provided = my_tag.get_provided_values()
```

## Usage

Tags are used in combination with the `tags` parameter on `@option`, `@argument`, and `@env` decorators:

```python
@command()
@option("--username", tags="credentials")
@option("--password", tags="credentials")
@tag("credentials")
def my_command(username: str, password: str):
    """A command with grouped credential options."""
    pass
```

## Examples

> [!INFO]
> For demonstration purposes, many examples include child validation decorators that are custom (i.e. not available in `click_extended`).

### Basic Tag Grouping with Validation

```python
from click_extended import command, option, tag

@command()
@option("--username", tags="credentials")
@option("--password", tags="credentials")
@tag("credentials")
@require_all_if_any()
def login(username: str | None, password: str | None):
    """Login with credentials (both username and password required together)."""
    if username and password:
        print(f"Logging in as {username}")
    else:
        print("Missing credentials.")
```

### Multiple Tags with Different Validations

```python
from click_extended import command, option, tag

@command()
@option("--api-key", tags=["auth", "api"])
@option("--api-secret", tags=["auth", "api"])
@option("--api-url", tags="api", default="https://api.example.com")
@option("--debug", tags="dev")
@tag("auth")
@require_all()
@tag("api")
@at_least(1)
def deploy(
    api_key: str,
    api_secret: str,
    api_url: str,
    debug: bool
):
    """Deploy with API configuration."""
    print(f"Deploying to {api_url}...")
    if debug:
        print("Debug mode enabled")
```

### Require At Least One Parameter

```python
from click_extended import command, option, tag

@command()
@option("--email", tags="contact")
@option("--phone", tags="contact")
@option("--username", tags="contact")
@tag("contact")
@at_least(1)
def register(email: str | None, phone: str | None, username: str | None):
    """Register with at least one contact method."""
    contact = email or phone or username
    print(f"Registering with: {contact}")
```

### Organizing Related Options with Validation

```python
from click_extended import command, option, env, tag

@command()
@option("--db-host", tags="database")
@option("--db-port", "-p", type=int, default=5432, tags="database")
@env("DB_PASSWORD", tags="database")
@option("--redis-host", tags="cache")
@option("--redis-port", type=int, default=6379, tags="cache")
@tag("database")
@require_host_when_used()
@tag("cache")
@require_host_when_used()
def start_server(
    db_host: str | None,
    db_port: int,
    db_password: str | None,
    redis_host: str | None,
    redis_port: int
):
    """Start server with database and cache configuration."""
    if db_host:
        print(f"Connecting to database: {db_host}:{db_port}")
    if redis_host:
        print(f"Connecting to cache: {redis_host}:{redis_port}")
```

### Complex Tag Structure with Cloud Provider Validation

```python
from click_extended import command, option, argument, tag

@command()
@argument("action")
@option("--aws-key", tags=["cloud", "aws"])
@option("--aws-secret", tags=["cloud", "aws"])
@option("--aws-region", default="us-east-1", tags=["cloud", "aws"])
@option("--azure-key", tags=["cloud", "azure"])
@option("--azure-tenant", tags=["cloud", "azure"])
@option("--verbose", "-v", is_flag=True, tags="debug")
@option("--dry-run", is_flag=True, tags="debug")
@tag("cloud")
@exactly_one_provider()
@tag("aws")
@require_all_if_any()
@tag("azure")
@require_all_if_any()
@tag("debug")
def cloud_deploy(
    action: str,
    aws_key: str | None,
    aws_secret: str | None,
    aws_region: str,
    azure_key: str | None,
    azure_tenant: str | None,
    verbose: bool,
    dry_run: bool
):
    """Deploy to cloud provider (exactly one provider must be configured)."""
    if verbose:
        print(f"Action: {action}")
        if aws_key:
            print(f"Using AWS in {aws_region}")
        if azure_key:
            print("Using Azure")
        if dry_run:
            print("DRY RUN MODE")
```

## Complete Example with Custom Validation

```python
from click_extended import command, option, tag

@command()
@option("--config-file", type=str, tags="config-source")
@option("--config-url", type=str, tags="config-source")
@option("--use-defaults", is_flag=True, tags="config-source")
@tag("config-source")
@exclusive()
def deploy(
    config_file: str | None,
    config_url: str | None,
    use_defaults: bool
):
    """
    Deploy with configuration from exactly one source.

    You can provide either a config file, a URL, or use defaults,
    but not multiple sources at once.
    """
    if config_file:
        print(f"Using config from file: {config_file}")
    elif config_url:
        print(f"Using config from URL: {config_url}")
    elif use_defaults:
        print("Using default configuration")
    else:
        print("No configuration source specified")

if __name__ == "__main__":
    deploy()
```
