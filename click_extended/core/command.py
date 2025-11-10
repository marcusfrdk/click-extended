"""Command implementation for the `click_extended` library."""

from typing import Any, Callable

import click

from click_extended.core._root_node import RootNode


class Command(RootNode):
    """Command implementation for the `click_extended` library."""

    @classmethod
    def wrap(
        cls, wrapped_func: Callable[..., Any], name: str, **kwargs: Any
    ) -> click.Command:
        """
        Apply click.command wrapping after value injection.

        Args:
            wrapped_func: The function already wrapped with value injection.
            name: The name of the command.
            **kwargs: Additional arguments to pass to click.Command.

        Returns:
            A click.Command instance.
        """
        return click.command(name=name, **kwargs)(wrapped_func)  # type: ignore


def command(
    name_or_func: str | Callable[..., Any] | None = None, /, **kwargs: Any
) -> Any:
    """
    Decorator to create a click command with value injection from parent nodes.

    Args:
        name_or_func:
            Either the name of the command (str) or the function being
            decorated. If None, uses the decorated function's name.
        **kwargs (Any):
            Additional arguments to pass to click.Command.

    Returns:
        A decorator function or the decorated click.Command.
    """
    return Command.as_decorator(name_or_func, **kwargs)
