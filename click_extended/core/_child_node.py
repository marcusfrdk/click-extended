"""Child node class that stores information about the decorator."""

from abc import ABC, abstractmethod
from typing import Any


class ChildNode(ABC):
    """Child node class that stores information about the decorator."""

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize a new `ChildNode` instance.

        Args:
            *args (Any):
                The positional arguments.
            **kwargs (Any):
                The keyword arguments.
        """
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def process(
        self, value: Any, siblings: list[str], *args: Any, **kwargs: Any
    ) -> Any:
        """
        The function that processes the value in the chain.

        Args:
            value (Any):
                The value from the previous node in the chain.
            sublings (list[str]):
                A list of names of the siblings.
            *args (Any):
                The positional arguments provided.
            **kwargs (Any):
                The keyword arguments provided.
        """
        raise NotImplementedError
