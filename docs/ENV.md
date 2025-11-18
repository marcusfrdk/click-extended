![Banner](../assets/click-extended-banner.png)

# Env

An environment variable parameter that reads values from the system environment. For this library, `@env` is an extension of the `ParentNode`, meaning it injects values into the context from environment variables, supporting `.env` files through automatic loading of `python-dotenv`.

## Parameters

| Name       | Description                                                                                                                     | Type             | Required | Default               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- | --------------------- |
| `env_name` | The name of the environment variable to read (e.g., `API_KEY`, `DATABASE_URL`).                                                 | str              | Yes      |                       |
| `name`     | The parameter name to inject into the function. If not provided, automatically derived from `env_name` converted to snake_case. | str              | No       | `env_name` snake_case |
| `help`     | Help text describing this parameter.                                                                                            | str              | No       | None                  |
| `required` | Whether the environment variable must be set. If `True`, an error is raised even if `default` is provided.                      | bool             | No       | False                 |
| `default`  | Default value if environment variable is not set and `required=False`.                                                          | Any              | No       | None                  |
| `tags`     | Tag(s) to associate with this parameter for validation or grouping. Used with the `@tag` decorator.                             | str or list[str] | No       | None                  |

> **Note:** The `@env` decorator automatically loads `.env` files using `python-dotenv`. The parameter name is derived from the environment variable name by converting it to snake_case (e.g., `API_KEY` becomes `api_key`).

## Examples

### Basic Usage

```python
from click_extended import command, env

@command()
@env("API_KEY")
def deploy(api_key: str):
    """Deploy using the API key from environment."""
    print(f"Deploying with key: {api_key[:8]}...")
```

### With Custom Parameter Name

```python
from click_extended import command, env

@command()
@env("DATABASE_URL", name="db_url")
def connect(db_url: str):
    """Connect to the database."""
    print(f"Connecting to: {db_url}")
```

### Required Environment Variable

```python
from click_extended import command, env

@command()
@env("SECRET_KEY", required=True)
def start(secret_key: str):
    """Start the application with required secret key."""
    print("Application started securely")
```

### With Default Value

```python
from click_extended import command, env

@command()
@env("PORT", default=8080)
def serve(port: str):
    """Start server on specified port."""
    print(f"Server running on port {port}")
```

### Multiple Environment Variables

```python
from click_extended import command, env

@command()
@env("API_KEY", required=True)
@env("API_SECRET", required=True)
@env("API_BASE_URL", default="https://api.example.com")
def api_call(api_key: str, api_secret: str, api_base_url: str):
    """Make an authenticated API call."""
    print(f"Calling {api_base_url}")
    print(f"Using credentials: {api_key[:8]}...")
```

### With Help Text

```python
from click_extended import command, env

@command()
@env("DATABASE_URL", help="PostgreSQL connection string")
@env("REDIS_URL", help="Redis cache connection string", default="redis://localhost")
def migrate(database_url: str, redis_url: str):
    """Run database migrations."""
    print(f"Migrating database: {database_url}")
    print(f"Using cache: {redis_url}")
```

### Name Transformation

```python
from click_extended import command, env

@command()
@env("MY_API_KEY")  # Becomes "my_api_key" parameter
def process(my_api_key: str):
    """Process data with API key."""
    print(f"Processing with: {my_api_key}")
```

### With Tags

```python
from click_extended import command, env

@command()
@env("API_KEY", tags=["auth", "required"])
@env("API_SECRET", tags="auth")
def authenticate(api_key: str, api_secret: str):
    """Authenticate with the service."""
    print("Authentication successful")
```

### Combined with Options and Arguments

```python
from click_extended import command, option, argument, env

@command()
@argument("filename")
@option("--format", "-f", type=str, default="json")
@env("OUTPUT_DIR", default="./output")
@env("API_KEY", required=True)
def process_file(filename: str, format: str, output_dir: str, api_key: str):
    """Process a file and upload to API."""
    print(f"Processing {filename} as {format}")
    print(f"Output directory: {output_dir}")
    print(f"Uploading with API key: {api_key[:8]}...")
```

## Complete Example

```python
import os
from click_extended import command, option, env

@command()
@option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@env("DATABASE_URL", required=True, help="PostgreSQL connection string")
@env("REDIS_URL", default="redis://localhost:6379", help="Redis cache URL")
@env("LOG_LEVEL", default="INFO", help="Logging level")
@env("MAX_WORKERS", default="4", help="Maximum worker threads")
def start_worker(
    verbose: bool,
    database_url: str,
    redis_url: str,
    log_level: str,
    max_workers: str
):
    """
    Start background worker with configuration from environment.

    Requires DATABASE_URL to be set. Other settings have sensible defaults.
    """
    if verbose:
        print(f"Database: {database_url}")
        print(f"Redis: {redis_url}")
        print(f"Log Level: {log_level}")
        print(f"Workers: {max_workers}")

    print("Worker started successfully")

if __name__ == "__main__":
    start_worker()
```

## Using .env Files

The `@env` decorator automatically loads environment variables from a `.env` file in your project root:

```bash
# .env file
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=DEBUG
```

Then in your Python script:

```python
from click_extended import command, env

@command()
@env("API_KEY", required=True)
@env("DATABASE_URL")
@env("LOG_LEVEL", default="INFO")
def deploy(api_key: str, database_url: str, log_level: str):
    """Deploy application using environment configuration."""
    print(f"Deploying with log level: {log_level}")

if __name__ == "__main__":
    deploy()
```

## Error Handling

When a required environment variable is missing:

```python
from click_extended import command, env

@command()
@env("MISSING_VAR", required=True)
def test(missing_var: str):
    print(missing_var)

```

Running this will raise: `ValueError: Required environment variable 'MISSING_VAR' is not set.`

Multiple missing required variables are reported together:

```python
from click_extended import command, env

@command()
@env("VAR1", required=True)
@env("VAR2", required=True)
@env("VAR3", required=True)
def test(var1: str, var2: str, var3: str):
    print("All set!")
```

If VAR1 and VAR3 are missing `ValueError: Required environment variables 'VAR1' and 'VAR3' are not set.` will be raised.
