"""Group implementation for the `click_extended` library.

This module provides the `group` decorator with support for:
- Group aliasing: Allow multiple names for the same group
- Custom help text: Override docstrings with explicit help parameters
- Automatic alias registration: Child commands/groups inherit alias support
- Value injection: Inherit values from parent nodes in the tree
- Async functions: Automatically wrap async functions for Click compatibility

Examples:
    Basic group with aliases:
        @group(name="database", aliases=["db", "d"], help="Database commands")
        def database():
            pass

    Group with single alias (shorthand):
        @group(name="config", aliases="cfg")
        def config_group():
            '''Configuration management.'''
            pass

    Group without aliases (uses docstring as help):
        @group()
        def admin():
            '''Admin commands.'''
            pass

    Adding commands with aliases:
        @command(name="list", aliases=["ls"])
        def list_items():
            '''List all items.'''
            pass

        database.add(list_items)
        # Both 'database list' and 'db ls' will work

    Async group:
        @group(name="async_group", aliases="ag")
        async def async_grp():
            '''Async group operations.'''
            await asyncio.sleep(0.1)
"""

from typing import TYPE_CHECKING, Any, Callable, TypeVar

import click

from click_extended.core._root_node import RootNode, RootNodeWrapper

T = TypeVar("T", bound="ClickExtendedGroup")

if TYPE_CHECKING:
    from click_extended.core.command import ClickExtendedCommand


class AliasedGroup(click.Group):
    """A Click group that supports aliasing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new AliasedGroup instance.

        Args:
            *args (Any):
                Positional arguments for the base click.Group class.
            **kwargs (Any):
                Keyword arguments for the base click.Group class.
        """
        self.aliases: str | list[str] | None = kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

    def add_command(self, cmd: click.Command, name: str | None = None) -> None:
        """
        Add a command to the group, including its aliases.

        Args:
            cmd (click.Command):
                The command to add to the group.
            name (str, optional):
                The name to use for the command. If not provided, uses the
                command's default name.
        """
        super().add_command(cmd, name)

        aliases = getattr(cmd, "aliases", None)
        if aliases is not None:
            aliases_list = [aliases] if isinstance(aliases, str) else aliases
            for alias in aliases_list:
                if alias:
                    super().add_command(cmd, alias)

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format the command list for display in help text.

        Args:
            ctx (click.Context):
                The Click context containing command information.
            formatter (click.HelpFormatter):
                The formatter to write command information to.
        """
        commands: dict[str, click.Command] = {}
        for name, cmd in self.commands.items():
            if name == cmd.name:
                aliases = getattr(cmd, "aliases", None)
                display_name = name

                if aliases is not None:
                    aliases_list = (
                        [aliases] if isinstance(aliases, str) else aliases
                    )
                    valid_aliases = [a for a in aliases_list if a]
                    if valid_aliases:
                        display_name = f"{name} ({', '.join(valid_aliases)})"

                commands[display_name] = cmd

        rows: list[tuple[str, str]] = [
            (name, cmd.get_short_help_str()) for name, cmd in commands.items()
        ]

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """
        Format the help text, including aliases if present.

        Args:
            ctx (click.Context):
                The Click context.
            formatter (click.HelpFormatter):
                The formatter to write help text to.
        """
        original_name = self.name

        if self.aliases:
            aliases_list = (
                [self.aliases]
                if isinstance(self.aliases, str)
                else self.aliases
            )
            valid_aliases = [a for a in aliases_list if a]
            if valid_aliases:
                self.name = f"{self.name} ({', '.join(valid_aliases)})"

        super().format_help(ctx, formatter)

        self.name = original_name


class ClickExtendedGroup(RootNodeWrapper):
    """
    Extended Click Group wrapper with only `add()` and `visualize()` exposed.
    """

    def __init__(
        self,
        underlying_group: click.Group,
        instance: RootNode,
    ):
        """
        Initialize a new `ClickExtendedGroup` wrapper.

        Args:
            underlying_group (click.Group):
                The underlying `click.Group` instance.
            instance (RootNode):
                The RootNode instance for tree visualization.
        """
        super().__init__(instance)
        self.group = underlying_group

    def add(self: T, cls: "ClickExtendedCommand | ClickExtendedGroup") -> T:
        """
        Add a `Command` or `Group` to this group.

        This method only accepts `Command` or `Group` instances
        (which are `click.Command` or `click.Group` at runtime).
        Aliases are automatically registered.

        Args:
            cls (ClickExtendedCommand | ClickExtendedGroup):
                A `Command` or `Group` instance to add.

        Returns:
            T:
                The group instance for method chaining.

        Raises:
            TypeError:
                If cls is not a `ClickExtendedCommand` or `ClickExtendedGroup`.
        """
        if isinstance(cls, ClickExtendedGroup):
            actual_cls = cls.group
        else:
            actual_cls = cls.command

        self.group.add_command(actual_cls)
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Allow the group to be called like a regular Click group."""
        return self.group(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate all other attribute access to the underlying group."""
        return getattr(self.group, name)


class Group(RootNode):
    """Group implementation for the `click_extended` library."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Initialize a new Group instance.

        Args:
            name (str):
                The name of the group.
            **kwargs (Any):
                Additional keyword arguments (ignored, used by wrap method).
        """
        super().__init__(name=name)

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: RootNode,
        **kwargs: Any,
    ) -> ClickExtendedGroup:
        """
        Apply `click.group` wrapping after value injection.

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the group.
            instance (RootNode):
                The RootNode instance that owns this tree.
            **kwargs (Any):
                Additional arguments to pass to click.Group.

        Returns:
            ClickExtendedGroup:
                A `ClickExtendedGroup` instance with added functionality.
        """
        underlying_group = click.group(name=name, cls=AliasedGroup, **kwargs)(
            wrapped_func
        )

        return ClickExtendedGroup(
            underlying_group=underlying_group,
            instance=instance,
        )


def group(
    name: str | None = None,
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ClickExtendedGroup]:
    """
    Decorator to create a click group with value injection from parent nodes.

    Args:
        name (str, optional):
            The name of the group. If `None`, uses the
            decorated function's name.
        aliases (str | list[str], optional):
            Alternative name(s) for the group. Can be a single
            string or a list of strings.
        help (str, optional):
            The help message for the group. If not provided,
            uses the function's docstring.
        **kwargs (Any):
            Additional arguments to pass to `click.Group`.

    Returns:
        Callable:
            A decorator function that returns a `ClickExtendedGroup`.
    """
    if aliases is not None:
        kwargs["aliases"] = aliases
    if help is not None:
        kwargs["help"] = help
    return Group.as_decorator(name, **kwargs)
