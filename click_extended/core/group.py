"""Group implementation for the `click_extended` library."""

# pylint: disable=protected-access
# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals

from typing import TYPE_CHECKING, Any, Callable, TypeVar

import click

from click_extended.core._aliased import AliasedGroup
from click_extended.core._root_node import RootNode, RootNodeWrapper
from click_extended.core.argument import Argument
from click_extended.core.option import Option
from click_extended.errors import DuplicateNameError

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
        func = wrapped_func
        h_flag_taken = False
        if instance.tree.root and instance.tree.root.children:
            seen_short_flags: dict[str, str] = {}
            for parent_node in instance.tree.root.children.values():
                if isinstance(parent_node, Option) and parent_node.short:
                    if parent_node.short == "-h":
                        h_flag_taken = True
                    if parent_node.short in seen_short_flags:
                        prev_name = seen_short_flags[parent_node.short]

                        raise DuplicateNameError(
                            parent_node.short,
                            "option",
                            "option",
                            f"'{prev_name}' ({parent_node.short})",
                            f"'{parent_node.name}' ({parent_node.short})",
                        )
                    seen_short_flags[parent_node.short] = parent_node.name

            parent_items = list(instance.tree.root.children.items())
            for _parent_name, parent_node in reversed(parent_items):
                if isinstance(parent_node, Option):
                    params: list[str] = []
                    if parent_node.short:
                        params.append(parent_node.short)
                    params.append(parent_node.long)

                    func = click.option(
                        *params,
                        type=parent_node.type,
                        default=parent_node.default,
                        required=parent_node.required,
                        is_flag=parent_node.is_flag,
                        multiple=parent_node.multiple,
                        help=parent_node.help,
                        **parent_node.extra_kwargs,
                    )(func)

                elif isinstance(parent_node, Argument):
                    func = click.argument(
                        parent_node.name,
                        type=parent_node.type,
                        default=parent_node.default,
                        nargs=parent_node.nargs,
                        **parent_node.extra_kwargs,
                    )(func)

        if not h_flag_taken:
            if "context_settings" not in kwargs:
                kwargs["context_settings"] = {}
            if "help_option_names" not in kwargs["context_settings"]:
                kwargs["context_settings"]["help_option_names"] = [
                    "-h",
                    "--help",
                ]

        click_decorator = cls._get_click_decorator()
        click_cls = cls._get_click_cls()

        underlying = click_decorator(name=name, cls=click_cls, **kwargs)(func)

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
            uses the first line of the function's docstring.
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

    def decorator(func: Callable[..., Any]) -> GroupWrapper:
        if help is None and func.__doc__:
            first_line = func.__doc__.strip().split("\n")[0].strip()
            if first_line:
                kwargs["help"] = first_line
        wrapper: GroupWrapper = Group.as_decorator(name, **kwargs)(func)
        return wrapper

    return decorator
