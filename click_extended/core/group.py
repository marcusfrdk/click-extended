"""Group decorator for grouping commands and groups."""

from typing import Any, Callable, overload

import click

from click_extended.core._context_node import ContextNode
from click_extended.core._parent_node import ParentNode
from click_extended.core.command import Command
from click_extended.errors.invalid_command_type_error import (
    InvalidCommandTypeError,
)


class ClickGroupWithAliasSupport(click.Group):
    """
    Custom Click Group that formats commands with aliases in help text.

    This extends `click.Group` to display command aliases alongside their
    primary names in the help output, formatted as "name (alias1, alias2)".
    """

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format the commands section of the help text with alias support.

        Args:
            ctx (click.Context):
                The Click context.
            formatter (click.HelpFormatter):
                The formatter to write help text to.
        """
        extended_group = getattr(self, "_extended_group", None)
        if extended_group is None:
            return super().format_commands(ctx, formatter)

        commands_to_display = {}

        for name, cmd in extended_group.commands.items():
            display_name = name
            if cmd.aliases:
                display_name = f"{name} ({', '.join(cmd.aliases)})"
            commands_to_display[display_name] = cmd

        rows = [
            (name, cmd.cls.get_short_help_str())
            for name, cmd in commands_to_display.items()
        ]

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)


class Group(ContextNode):
    """
    A group node that wraps a function as a Click group.

    Group nodes can contain child commands and subgroups, creating a
    hierarchical CLI structure. They support aliases and custom help
    formatting.
    """

    def __init__(
        self, fn: Callable, name: str | None = None, **attrs: Any
    ) -> None:
        """
        Initialize a new `Group` instance.

        Args:
            fn (Callable):
                The function to wrap as a group.
            name (str | None):
                The name of the group. If `None`, uses the function name.
            **attrs (Any):
                Additional attributes to pass to the underlying `click.Group`.
        """
        if "context_settings" not in attrs:
            attrs["context_settings"] = {}
        if "help_option_names" not in attrs["context_settings"]:
            attrs["context_settings"]["help_option_names"] = ["-h", "--help"]

        super().__init__(fn, name, ClickGroupWithAliasSupport, **attrs)
        self.commands: dict[str, "Command | Group"] = {}
        self.cls._extended_group = self

    def add_parent(self, parent: ParentNode) -> None:
        super().add_parent(parent)

        for parent in self.parents.values():
            if parent.short == "-h":
                if self.cls.params and hasattr(self.cls.params[0], "opts"):
                    help_param = self.cls.params[0]
                    help_param.opts = ["--help"]
                    help_param.secondary_opts = []
                break

    def add(self, cls: "Command | Group", name: str | None = None) -> None:
        """
        Add a command or subgroup to this group.

        This registers the command/group with its primary name and all aliases
        to the underlying Click group.

        Args:
            cls (Command | Group):
                The command or group to add.
            name (str | None, optional):
                Override name for the command. If `None`, uses `cls.name`.

        Raises:
            InvalidCommandTypeError:
                If `cls` is not a `ContextNode` instance.
        """
        if not isinstance(cls, ContextNode):
            cmd_type = type(cls).__name__
            raise InvalidCommandTypeError(cmd_type)

        self.commands[cls.name] = cls
        self.cls.add_command(cls.cls, name)

        for alias in cls.aliases:
            self.cls.add_command(cls.cls, alias)


@overload
def group(fn: Callable, /) -> Group: ...


@overload
def group(
    fn: str,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Group]: ...


@overload
def group(
    fn: None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Callable[[Callable], Group]: ...


def group(
    fn: Callable | str | None = None,
    /,
    *,
    name: str | None = None,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **attrs: Any,
) -> Group | Callable[[Callable], Group]:
    """
    Decorator to create a Group node from a function.

    Args:
        fn (Callable | str | None):
            The function to decorate, a name string, or `None`.
        name (str | None, optional):
            The name of the group. If `None`, uses the function name.
        aliases (str | list[str] | None, optional):
            One or more aliases for the group.
        help (str | None, optional):
            Help text for the group. If `None`, uses the function's docstring.
        **attrs (Any):
            Additional attributes to pass to the Click group.

    Returns:
        Group | Callable[[Callable], Group]:
            Either a Group instance or a decorator function.

    Examples:
        Direct application without parentheses:

        ```python
        @group
        def cli():
            pass
        ```

        Called with parentheses:

        ```python
        @group()
        def cli():
            pass
        ```

        With a name string:

        ```python
        @group("main")
        def cli():
            pass
        ```

        With explicit parameters:

        ```python
        @group(name="main", aliases=["m", "app"], help="Main CLI group")
        def cli():
            pass
        ```

        Creating a nested group structure:

        ```python
        @group
        def cli():
            pass

        @group
        def database():
            pass

        database.add(cli)

        @command
        def migrate():
            print("Running migrations...")

        migrate.add(database)
        ```

        Accessing the context node:

        ```python
        from click_extended import group
        from click_extended.types import ContextNode

        @group
        def cli(ctx: ContextNode):
            print(f"Group name: {ctx.name}")
            print(f"Available commands: {list(ctx.commands.keys())}")
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

    return Group.as_decorator(fn, **attrs)
