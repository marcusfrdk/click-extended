"""Debugging example."""

import click

from click_extended import command, option
from click_extended.debug import debug


@command
@option("--name")
@debug
def my_function(name):
    """Example function."""
    result = f"Hello, {name}!"
    click.echo(result)
    return result


if __name__ == "__main__":
    my_function()
