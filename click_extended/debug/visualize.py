"""Visualize the tree."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from typing import TYPE_CHECKING, Any

from click_extended.core._global_node import GlobalNode

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode
    from click_extended.core._root_node import RootNode
    from click_extended.core._tree import Tree
    from click_extended.core.tag import Tag


class Visualize(GlobalNode):
    """Visualize the tree structure."""

    def process(
        self,
        tree: "Tree",
        root: "RootNode",
        parents: list["ParentNode"],
        tags: dict[str, "Tag"],
        globals: list["GlobalNode"],
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Visualize the tree and optionally return data for injection.

        Args:
            tree: The full tree structure
            root: The root node
            parents: List of all parent nodes
            tags: Dictionary of tags
            globals: List of all global nodes
            call_args: Click function positional arguments
            call_kwargs: Click function keyword arguments
            *args: Additional arguments from decorator
            **kwargs: Additional keyword arguments from decorator

        Returns:
            If inject_name is set, returns a dict with tree information.
            Otherwise returns None.
        """
        tree.visualize()


def visualize(delay: bool = False, **kwargs: Any) -> Any:
    """
    Visualize the tree structure.

    Args:
        delay (bool, optional):
            Whether to delay execution until after parent value collection.
            Defaults to False (execute early).
        **kwargs (Any):
            Additional keyword arguments passed to the visualize process.

    Returns:
        Any:
            A decorator function.

    Examples:
        ```python
        @command()
        @visualize()  # Prints tree early
        @option("name")
        @visualize(delay=True)  # Prints tree after parent collection
        def my_command(name: str):
            pass
        ```
    """
    return Visualize.as_decorator(None, delay=delay, **kwargs)
