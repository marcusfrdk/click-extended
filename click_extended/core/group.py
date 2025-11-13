"""Group implementation for the `click_extended` library."""

# pylint: disable=protected-access
# pylint: disable=redefined-builtin

from typing import TYPE_CHECKING, Any, Callable, TypeVar

import click

from click_extended.core._aliased import AliasedGroup
from click_extended.core._root_node import RootNode, RootNodeWrapper

T = TypeVar("T", bound="GroupWrapper")

if TYPE_CHECKING:
    pass


class GroupWrapper(RootNodeWrapper[click.Group]):
    """
    Extended wrapper for Click Groups that adds the `add()` method.

    This wrapper extends RootNodeWrapper to provide group-specific
    functionality for adding commands and subgroups.
    """

    def add(self: T, cls: RootNodeWrapper[click.Command]) -> T:
        """
        Add a `Command` or `Group` to this group.

        This method accepts any `RootNodeWrapper` instance (Command or Group).
        Aliases are automatically registered.

        Args:
            cls (RootNodeWrapper[click.Command]):
                A wrapped Command or Group instance to add.

        Returns:
            T:
                The group instance for method chaining.
        """
        self._underlying.add_command(cls._underlying)
        return self


class Group(RootNode):
    """Group implementation for the `click_extended` library."""

    @classmethod
    def _get_click_decorator(cls) -> Callable[..., Any]:
        """Return the click.group decorator."""
        return click.group

    @classmethod
    def _get_click_cls(cls) -> type[click.Command]:
        """Return the AliasedGroup class."""
        return AliasedGroup

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: "RootNode",
        **kwargs: Any,
    ) -> GroupWrapper:
        """
        Apply Click wrapping and return a GroupWrapper.

        This overrides the parent to return a GroupWrapper instead of
        a generic RootNodeWrapper, providing the add() method.

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the root node.
            instance (RootNode):
                The RootNode instance that owns this tree.
            **kwargs (Any):
                Additional keyword arguments passed to the Click decorator.

        Returns:
            GroupWrapper:
                A wrapper with group-specific functionality.
        """
        click_decorator = cls._get_click_decorator()
        click_cls = cls._get_click_cls()

        underlying = click_decorator(name=name, cls=click_cls, **kwargs)(
            wrapped_func
        )

        return GroupWrapper(underlying=underlying, instance=instance)


def group(
    name: str | None = None,
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], GroupWrapper]:
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
            A decorator function that returns a `GroupWrapper`.
    """
    if aliases is not None:
        kwargs["aliases"] = aliases
    if help is not None:
        kwargs["help"] = help
    return Group.as_decorator(name, **kwargs)
