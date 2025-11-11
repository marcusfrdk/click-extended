"""Command implementation for the `click_extended` library."""

from typing import Any, Callable

import click

from click_extended.core._root_node import RootNode, RootNodeWrapper


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
        underlying_command = click.command(name=name, **kwargs)(wrapped_func)

        return ClickExtendedCommand(
            underlying_command=underlying_command,
            instance=instance,
        )


def command(
    name: str | None = None, /, **kwargs: Any
) -> Callable[[Callable[..., Any]], ClickExtendedCommand]:
    """
    Decorator to create a click command with value injection from parent nodes.

    Args:
        name (str):
            The name of the command. If `None`, uses the
            decorated function's name.
        **kwargs (Any):
            Additional arguments to pass to `click.Command`.

    Returns:
        Callable:
            A decorator function that returns a `ClickExtendedCommand`.
    """
    return Command.as_decorator(name, **kwargs)
