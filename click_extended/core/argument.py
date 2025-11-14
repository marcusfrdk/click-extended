"""`ParentNode` that represents a Click argument."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from typing import Any, Callable, ParamSpec, TypeVar

from click_extended.core._parent_node import ParentNode
from click_extended.utils.transform import Transform

P = ParamSpec("P")
T = TypeVar("T")


class Argument(ParentNode):
    """`ParentNode` that represents a Click argument."""

    def __init__(
        self,
        name: str,
        nargs: int = 1,
        type: Any = None,
        help: str | None = None,
        required: bool = True,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `Argument` instance.

        Args:
            name (str):
                The name of the argument.
            nargs (int):
                Number of arguments to accept. Use `-1` for unlimited.
                Defaults to `1`.
            type (Any, optional):
                The type to convert the value to (`int`, `str`, `float`, etc.).
            help (str, optional):
                Help text for this argument.
            required (bool):
                Whether this argument is required. Defaults to `True`.
            default (Any):
                Default value if not provided. Defaults to `None`.
            tags (str | list[str], optional):
                Tag(s) to associate with this argument for grouping.
            **kwargs (Any):
                Additional keyword arguments.
        """
        name = Transform(name).to_snake_case()
        super().__init__(
            name=name,
            help=help,
            required=required,
            default=default,
            tags=tags,
        )
        self.nargs = nargs
        self.type = type
        self.extra_kwargs = kwargs


def argument(
    name: str,
    nargs: int = 1,
    type: Any = None,
    help: str | None = None,
    required: bool = True,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to create a Click argument with value injection.

    Args:
        name (str):
            The name of the argument.
        nargs (int):
            Number of arguments to accept. Use `-1` for unlimited.
            Defaults to `1`.
        type (Any, optional):
            The type to convert the value to (`int`, `str`, `float`, etc.).
        help (str, optional):
            Help text for this argument.
        required (bool):
            Whether this argument is required. Defaults to `True`.
        default (Any):
            Default value if not provided. Defaults to `None`.
        tags (str | list[str], optional):
            Tag(s) to associate with this argument for grouping.
        **kwargs (Any):
            Additional Click argument parameters.

    Returns:
        Callable:
            A decorator function that registers the argument parent node.

    Examples:

        ```python
        @argument("filename")
        def my_func(filename):
            print(f"File: {filename}")
        ```

        ```python
        @argument("files", nargs=-1, help="Files to process")
        def my_func(files):
            for file in files:
                print(f"Processing: {file}")
        ```

        ```python
        @argument("port", type=int, default=8080)
        def my_func(port):
            print(f"Port: {port}")
        ```
    """
    return Argument.as_decorator(
        name=name,
        nargs=nargs,
        type=type,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
