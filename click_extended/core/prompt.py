"""Parent decorator that prompts the user for a value."""

from getpass import getpass
from typing import Any

from click_extended.core.context import Context
from click_extended.core.parent_node import ParentNode
from click_extended.types import Decorator


class Prompt(ParentNode):
    """Parent decorator that prompts the user for a value."""

    def load(
        self,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        if kwargs["hide"]:
            return getpass(kwargs["text"])
        return input(kwargs["text"])


def prompt(
    name: str,
    text: str = "",
    hide: bool = False,
) -> Decorator:
    """
    Prompt the user for input.

    Args:
        name (str):
            The name of the parent node.
        text (str):
            The text to show.
        hide (bool):
            Whether to hide the input, defaults to `False`.


    Returns:
        Decorator:
            The decorator function.
    """
    return Prompt.as_decorator(
        name=name,
        text=text,
        hide=hide,
    )
