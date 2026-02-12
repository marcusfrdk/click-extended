"""Group implementation for the `click_extended` library."""

# pylint: disable=protected-access
# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches

from typing import Any, Callable

import click

from click_extended.core.nodes._root_node import RootNode
from click_extended.core.other._click_group import ClickGroup


class Group(RootNode):
    """Group implementation for the `click_extended` library."""

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new `Group` instance.

        Args:
            name (str):
                The name of the group.
            *args (Any):
                Additional positional arguments.
            **kwargs (Any):
                Additional keyword arguments.
                May include 'invoke_on_subcommand' to control whether
                the group callback is invoked when a subcommand runs.
        """
        self.invoke_on_subcommand = kwargs.pop("invoke_on_subcommand", True)
        super().__init__(name, *args, **kwargs)

    @classmethod
    def _get_click_decorator(cls) -> Callable[..., Any]:
        """Return the click.group decorator (no longer used)."""
        return click.group

    @classmethod
    def _get_click_cls(cls) -> type[click.Command]:  # type: ignore[override]
        """Return the ClickGroup class."""
        return ClickGroup

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: RootNode,
        **kwargs: Any,
    ) -> ClickGroup:
        """Override to return proper ClickGroup type."""
        return super().wrap(
            wrapped_func,
            name,
            instance,
            **kwargs,
        )  # type: ignore[return-value]

    @classmethod
    def as_decorator(
        cls, name: str | None = None, /, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], ClickGroup]:
        """Override to return proper ClickGroup type."""
        return super().as_decorator(
            name,
            **kwargs,
        )  # type: ignore[return-value]


def group(
    name: str | None = None,
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    invoke_on_subcommand: bool = True,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ClickGroup]:
    """
    A `RootNode` decorator to create a click group with value injection
    from parent nodes.

    Args:
        name (str, optional):
            The name of the group. If `None`, uses the
            decorated function's name.
        aliases (str | list[str], optional):
            Alternative name(s) for the group. Can be a single
            string or a list of strings.
        help (str, optional):
            The help message for the group. If not provided,
            uses the first line of the function's docstring.
        invoke_on_subcommand (bool, optional):
            Whether to invoke the group's callback function when a
            subcommand is executed. Defaults to `True` (current behavior).
            When `False`, the group callback is only invoked when the group
            itself is called directly, not when running nested subcommands.
        **kwargs (Any):
            Additional arguments to pass to `click.Group`.

    Returns:
        Callable:
            A decorator function that returns a ClickGroup.
    """
    if aliases is not None:
        kwargs["aliases"] = aliases
    if help is not None:
        kwargs["help"] = help
    kwargs["invoke_on_subcommand"] = invoke_on_subcommand

    def decorator(func: Callable[..., Any]) -> ClickGroup:
        if help is None and func.__doc__:
            kwargs["help"] = func.__doc__
        return Group.as_decorator(name, **kwargs)(func)

    return decorator
