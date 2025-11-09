"""Command decorator for creating a command in the command line interface."""

from typing import Any, Callable, overload

import click

from click_extended.core._context_node import ContextNode


class Command(ContextNode):
    """
    A command node that wraps a function as a Click command.

    Command nodes represent terminal commands in the CLI hierarchy and cannot
    have child commands.
    """

    def __init__(
        self, fn: Callable, name: str | None = None, **attrs: Any
    ) -> None:
        """
        Initialize a new `Command` instance.

        Args:
            fn (Callable):
                The function to wrap as a command.
            name (str | None):
                The name of the command. If None, uses the function name.
            **attrs (Any):
                Additional attributes to pass to the Click command.
        """
        super().__init__(fn, name, click.Command, **attrs)


@overload
def command(fn: Callable, /) -> Command: ...


@overload
def command(
    fn: str,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Command]: ...


@overload
def command(
    fn: None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Command]: ...


def command(
    fn: Callable | str | None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Command | Callable[[Callable], Command]:
    """
    Decorator to create a Command node from a function.

    Args:
        fn (Callable | str | None):
            The function to decorate, a name string, or None.
        name (str | None, optional):
            The name of the command. If `None`, uses the function name.
        aliases (str | list[str] | None, optional):
            One or more aliases for the command.
        help (str | None, optional):
            Help text for the command. If `None`, uses the function's docstring.
        **attrs (Any):
            Additional attributes to pass to the Click command.

    Returns:
        Command | Callable[[Callable], Command]:
            Either a Command instance or a decorator function.

    Examples:
        Direct application without parentheses:

        ```python
        @command
        def hello():
            print("Hello!")
        ```

        Called with parentheses:

        ```python
        @command()
        def hello():
            print("Hello!")
        ```

        With a name string:

        ```python
        @command("greet")
        def hello():
            print("Hello!")
        ```

        With explicit parameters:

        ```python
        @command(name="greet", aliases=["hi", "hey"], help="Helpful message")
        def hello():
            print("Hello!")
        ```

        With help text and aliases:

        ```python
        @command(help="Greet the user", aliases="hi")
        def greet():
            print("Hello!")
        ```

        Accessing the context node:

        ```python
        from click_extended import command
        from click_extended.types import ContextNode

        @command
        def status(ctx: ContextNode):
            print(f"Command name: {ctx.name}")
            print(f"Is async: {ctx.is_async}")
        ```
    """
    if isinstance(fn, str):
        actual_name = fn
        fn = None
    else:
        actual_name = name

    if actual_name is not None:
        attrs["name"] = actual_name
    if aliases is not None:
        attrs["aliases"] = aliases
    if help is not None:
        attrs["help"] = help

    return Command.as_decorator(fn, **attrs)
