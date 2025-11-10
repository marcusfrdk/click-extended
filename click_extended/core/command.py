"""Command implementation for the `click_extended` library."""

from typing import Any, Callable

import click

from click_extended.core._root_node import RootNode


class Command(RootNode):
    """Command implementation for the `click_extended` library."""

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: RootNode,
        **kwargs: Any,
    ) -> click.Command:
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
            click.Command:
                A `click.Command` instance.
        """
        command_obj = click.command(name=name, **kwargs)(wrapped_func)
        # Attach the visualize method to the command object
        command_obj.visualize = instance.visualize  # type: ignore
        return command_obj


def command(
    name_or_func: str | Callable[..., Any] | None = None, /, **kwargs: Any
) -> Any:
    """
    Decorator to create a click command with value injection from parent nodes.

    Args:
        name_or_func (str | Callable):
            Either the name of the command or the function being
            decorated. If `None`, uses the decorated function's name.
        **kwargs (Any):
            Additional arguments to pass to `click.Command`.

    Returns:
        Any:
            A decorator function or the decorated `click.Command`.
    """
    return Command.as_decorator(name_or_func, **kwargs)
