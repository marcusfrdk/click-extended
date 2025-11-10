"""Parent node."""

from abc import ABC, abstractmethod
from typing import Any

from click_extended.core._child_node import ChildNode


class ParentNode(ABC):
    """Node that tags a decorator as a parameter (option, argument, env, tag)"""

    def __init__(
        self,
        cls: Any,  # This should be click.Option, click.Argument, etc.
        name: str,
        required: bool = False,
        type: type | None = None,
        default: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new `ParentNode` instance.

        Args:
            name (str):
                The name of the `ParentNode`.
            required (bool, optional):
                If the `ParentNode` is required, defaults to `False`.
            type (type | None, optional):
                The type of the `ParentNode`, defaults to `None`.
            default (Any, optional):
                The default value of the `ParentNode`, default to `None`.
            *args (Any):
                The positional arguments provided.
            **kwargs (Any):
                The keyword arguments provided.
        """
        self.name = name
        self.required = required
        self.type = type
        self.default = default
        self.children: list[ChildNode] = []
        self.args = args
        self.kwargs = kwargs

    def add_child(self, child: ChildNode) -> None:
        """
        Add a child to the list of children.

        Args:
            child (ChildNode):
                The `ChildNode` to add to the list of children.
        """
        self.children.append(child)

    def get_value(self) -> Any:
        """
        Get the value of the `ParentNode`.

        This method calls the `process` method of all children in the chain
        and returns the processed value.
        """
        # Get the value of the underlying click.option (@option),
        # click.argument (@argument) or os.getenv (@env).
        value = None

        for child in self.children:
            value = child.process(value, *child.args, **child.kwargs)

        return value
