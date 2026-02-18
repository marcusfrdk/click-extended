"""Child decorator to remove a suffix from a string."""

from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RemoveSuffix(ChildNode):
    """Child decorator to remove a suffix from a string."""

    def handle_str(
        self, value: str, context: Context, *args: Any, **kwargs: Any
    ) -> str:
        suffix: str = kwargs["suffix"]

        if value.endswith(suffix):
            return value[: -len(suffix)]

        return value


def remove_suffix(suffix: str) -> Decorator:
    """
    Remove a suffix from a string if it exists.

    Type: `ChildNode`

    Supports: `str`

    :param suffix: The suffix to remove from the end of the string.
    :returns: The decorator function.
    :rtype: Decorator

    Examples:
        ```python
        @command()
        @option("filename", default="document.txt")
        @remove_suffix(".txt")
        def cmd(filename: str) -> None:
            click.echo(f"Name: {filename}")  # Output: Name: document
        ```

        ```python
        @command()
        @option("url", default="example.com/")
        @remove_suffix("/")
        def cmd(url: str) -> None:
            click.echo(f"URL: {url}")  # Output: URL: example.com
        ```
    """
    return RemoveSuffix.as_decorator(suffix=suffix)
