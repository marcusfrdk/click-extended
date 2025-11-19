![Banner](../assets/click-extended-documentation-banner.png)

# Migrating From Click

`click-extended` is designed to be a drop-in replacement for Click with minimal changes required. The core decorators work the same way, so migration is straightforward.

## Quick Migration

### Step 1: Update Imports

Replace Click imports with `click-extended` imports:

**Before (Click):**

```python
import click

@click.command()
@click.option("--name", default="World")
def greet(name: str):
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

**After (click-extended):**

```python
from click_extended import command, option

@command()
@option("--name", default="World")
def greet(name: str):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

### Step 2: Update Groups

**Before (Click):**

```python
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("--count", default=1)
def hello(count):
    for _ in range(count):
        click.echo("Hello!")

cli.add_command(hello)

if __name__ == "__main__":
    cli()
```

**After (click-extended):**

```python
from click_extended import group, command, option

@group()
def cli():
    pass

@cli.command()
@option("--count", default=1)
def hello(count: int):
    for _ in range(count):
        print("Hello!")

cli.add(hello)

if __name__ == "__main__":
    cli()
```

## Import Reference

Replace these Click imports:

| Click Import     | click-extended Import                 |
| ---------------- | ------------------------------------- |
| `click.command`  | `from click_extended import command`  |
| `click.group`    | `from click_extended import group`    |
| `click.option`   | `from click_extended import option`   |
| `click.argument` | `from click_extended import argument` |

## Example Migration

Here's a complete example showing a Click application migrated to `click-extended`:

**Before (Click):**

```python
import click

@click.group()
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, verbose):
    """My CLI application."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument("filename")
@click.option("--output", "-o", help="Output file")
@click.pass_context
def process(ctx, filename, output):
    """Process a file."""
    if ctx.obj["verbose"]:
        click.echo(f"Processing {filename}")

    if output:
        click.echo(f"Writing to {output}")

if __name__ == "__main__":
    cli()
```

**After (click-extended):**

```python
from click_extended import group, command, argument, option, pass_context

@group()
@option("--verbose", is_flag=True, help="Verbose output")
@pass_context
def cli(ctx, verbose: bool):
    """My CLI application."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@argument("filename")
@option("--output", "-o", help="Output file")
@pass_context
def process(ctx, filename: str, output: str):
    """Process a file."""
    if ctx.obj["verbose"]:
        print(f"Processing {filename}")

    if output:
        print(f"Writing to {output}")

if __name__ == "__main__":
    cli()
```

## New Features Available

Once migrated, the `@command` and `@group` decorators can take advantage of new features:

### Command Aliases

```python
from click_extended import command, option

@command(aliases=["hi", "hello"])
@option("--name", default="World")
def greet(name: str):
    """Greet someone."""
    print(f"Hello, {name}!")
```

### Async Support

```python
import asyncio

from click_extended import command, option

@command()
@option("--delay", type=float, default=1.0)
async def async_task(delay: float):
    """Run an async task."""
    await asyncio.sleep(delay)
    print("Task complete!")
```

## Compatibility Notes

- `click-extended` is built on top of Click, so all Click features remain available
- You can still access Click's utilities via `import click` if needed
- `click.echo()` works, but standard `print()` is also fine
- Context objects (`ctx`) work exactly the same way
- All Click types (`click.Path`, `click.Choice`, etc.) are fully supported

## See Also

- [COMMAND.md](./COMMAND.md)
- [GROUP.md](./GROUP.md)
- [OPTION.md](./OPTION.md)
- [ARGUMENT.md](./ARGUMENT.md)
- [ENV.md](./ENV.md)
- [CHILD_NODE.md](./CHILD_NODE.md)
