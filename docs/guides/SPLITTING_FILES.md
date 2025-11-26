![Banner](../../assets/click-extended-documentation-banner.png)

# Splitting Files

Command line interfaces quickly grow very large in size of both the functions and the directory structure. This is a guide how you can apply different patterns to build your command line interface. These patterns are not exclusive and are recommended to use together.

## Single File

Using a single file is useful when you either have a small command line interface, or if you want to collect nested commands/groups.

### cli.py

```python
from click_extended import group

@group()
def my_group():
    ...

@my_group.command(aliases=["mc"])
def my_command():
    print("Hello from my command")
```

```bash
python3 cli.py mc
Hello from my command
```

## Multiple Files

Splitting your command line interface is a good choice when the project grows and each command or group grows in size.

### entrypoint.py

```python
from click_extended import group
from .nested_command import my_nested_command
from .nested_group import my_nested_group

@group()
def entrypoint():
    ...

entrypoint.add(my_nested_command)
entrypoint.add(my_nested_group)

if __name__ == "__main__":
    entrypoint()
```

### nested_command.py

```python
from click_extended import command

@command(aliases=["mnc"])
def my_nested_command():
    print("Hello from my nested command")
```

### nested_group.py

```python
from click_extended import group

@group(aliases=["mng"])
def my_nested_group():
    ...

@my_nested_group.command(aliases=["mdnc"])
def my_deeply_nested_command():
    print("Hello from my deeply nested command")
```

```bash
python3 -m entrypoint mnc
Hello from my nested command
```

```bash
python3 -m entrypoint mng mdnc
Hello from my deeply nested command
```
