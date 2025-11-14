"""Utility functions for tree visualization."""

# pylint: disable=import-outside-toplevel

from typing import TYPE_CHECKING

from click_extended.errors import NoRootError

if TYPE_CHECKING:
    from click_extended.core._root_node import RootNode


def visualize_tree(root: "RootNode | None") -> None:
    """
    Visualize a tree structure by printing its hierarchy.

    Args:
        root (RootNode):
            The root node of the tree to visualize.
    """

    if root is None:
        raise NoRootError

    print(root.name)
    assert root.children is not None
    for parent in root.children.values():
        print(f"  {parent.name}")
        assert parent.children is not None
        for child in parent.children.values():
            print(f"    {child.name}")
