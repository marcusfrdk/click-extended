"""Command implementation for the `click_extended` library."""

from typing import Any, Callable

import click

from click_extended.core._root_node import RootNode, RootNodeWrapper


class AliasedCommand(click.Command):
    """A Click command that supports aliasing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new AliasedCommand instance.

        Args:
            *args (Any):
                Positional arguments for the base click.Command class.
            **kwargs (Any):
                Keyword arguments for the base click.Command class.
        """
        self.aliases: str | list[str] | None = kwargs.pop("aliases", None)
        super().__init__(*args, **kwargs)

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


class ClickExtendedCommand(RootNodeWrapper):
    """Extended Click Command wrapper with only `visualize()` exposed."""

    def __init__(
        self,
        underlying_command: click.Command,
        instance: RootNode,
    ):
        """
        Initialize a new `ClickExtendedCommand` wrapper.

        Args:
            underlying_command (click.Command):
                The underlying `click.Command` instance.
            instance (RootNode):
                The RootNode instance for tree visualization.
        """
        super().__init__(instance)
        self.command = underlying_command

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Allow the command to be called like a regular Click command."""
        return self.command(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate all other attribute access to the underlying command."""
        return getattr(self.command, name)


class Command(RootNode):
    """Command implementation for the `click_extended` library."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Initialize a new Command instance.

        Args:
            name (str):
                The name of the command.
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
    ) -> ClickExtendedCommand:
        """
        Apply `click.command` wrapping after value injection.

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the command.
            instance (RootNode):
                The RootNode instance that owns this tree.
            **kwargs (Any):
                Additional arguments to pass to click.Command.

        Returns:
            ClickExtendedCommand:
                A `ClickExtendedCommand` instance.
        """
        underlying_command = click.command(
            name=name, cls=AliasedCommand, **kwargs
        )(wrapped_func)

        return ClickExtendedCommand(
            underlying_command=underlying_command,
            instance=instance,
        )


def command(
    name: str | None = None,
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ClickExtendedCommand]:
    """
    Decorator to create a click command with value injection from parent nodes.

    Args:
        name (str, optional):
            The name of the command. If `None`, uses the
            decorated function's name.
        aliases (str | list[str], optional):
            Alternative name(s) for the command. Can be a single
            string or a list of strings.
        help (str, optional):
            The help message for the command. If not provided,
            uses the function's docstring.
        **kwargs (Any):
            Additional arguments to pass to `click.Command`.

    Returns:
        Callable:
            A decorator function that returns a `ClickExtendedCommand`.
    """
    if aliases is not None:
        kwargs["aliases"] = aliases
    if help is not None:
        kwargs["help"] = help
    return Command.as_decorator(name, **kwargs)
