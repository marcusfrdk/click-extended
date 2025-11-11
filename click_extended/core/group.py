"""Group implementation for the `click_extended` library."""

from typing import TYPE_CHECKING, Any, Callable, TypeVar

import click

from click_extended.core._root_node import RootNode, RootNodeWrapper

T = TypeVar("T", bound="ClickExtendedGroup")

if TYPE_CHECKING:
    from click_extended.core.command import ClickExtendedCommand


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
        underlying_group = click.group(name=name, **kwargs)(wrapped_func)

        return ClickExtendedGroup(
            underlying_group=underlying_group,
            instance=instance,
        )


def group(
    name: str | None = None, /, **kwargs: Any
) -> Callable[[Callable[..., Any]], ClickExtendedGroup]:
    """
    Decorator to create a click group with value injection from parent nodes.

    Args:
        name (str, optional):
            The name of the group. If `None`, uses the
            decorated function's name.
        **kwargs (Any):
            Additional arguments to pass to `click.Group`.

    Returns:
        Callable:
            A decorator function that returns a `ClickExtendedGroup`.
    """
    return Group.as_decorator(name, **kwargs)
