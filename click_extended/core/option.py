"""`ParentNode` that represents a Click option."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

import re
from typing import Any, Callable, ParamSpec, TypeVar

from click_extended.core._parent_node import ParentNode
from click_extended.utils.transform import Transform

P = ParamSpec("P")
T = TypeVar("T")

LONG_FLAG_PATTERN = re.compile(r"^--[a-z][a-z0-9-]*$")
SHORT_FLAG_PATTERN = re.compile(r"^-[a-zA-Z]$")


class Option(ParentNode):
    """`ParentNode` that represents a Click option."""

    def __init__(
        self,
        long: str,
        short: str | None = None,
        is_flag: bool = False,
        type: Any = None,
        multiple: bool = False,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a new `Option` instance.

        Args:
            long (str):
                The long flag for the option (e.g., "--port").
                The parameter name is extracted from this by removing
                the -- prefix and replacing hyphens with underscores.
            short (str, optional):
                The short flag for the option (e.g., "-p").
            is_flag (bool):
                Whether this is a boolean flag (no value needed).
                Defaults to False.
            type (Any, optional):
                The type to convert the value to (int, str, float, etc.).
            multiple (bool):
                Whether to allow multiple values. Defaults to False.
            help (str, optional):
                Help text for this option.
            required (bool):
                Whether this option is required. Defaults to False.
            default (Any):
                Default value if not provided. Defaults to None.
            tags (str | list[str], optional):
                Tag(s) to associate with this option for grouping.
            **kwargs (Any):
                Additional Click option parameters.
        """
        if not re.match(LONG_FLAG_PATTERN, long):
            raise ValueError(
                f"Invalid long flag '{long}'. "
                "Must be format: --word "
                "(lowercase, hyphens allowed, e.g., --port, "
                "--config-file)"
            )

        if short is not None and not re.match(SHORT_FLAG_PATTERN, short):
            raise ValueError(
                f"Invalid short flag '{short}'. Must be format: -X "
                f"(e.g., -p, -v, -h)"
            )

        if is_flag and default is None:
            default = False

        name = Transform(long).to_snake_case()
        super().__init__(
            name=name, help=help, required=required, default=default, tags=tags
        )
        self.long = long
        self.short = short
        self.is_flag = is_flag
        self.type = type
        self.multiple = multiple
        self.extra_kwargs = kwargs


def option(
    long: str,
    short: str | None = None,
    is_flag: bool = False,
    type: Any = None,
    multiple: bool = False,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to create a Click option with value injection.

    The parameter name is automatically extracted from the long flag.

    Args:
        long (str):
            The long flag for the option (e.g., "--port", "--config-file").
        short (str, optional):
            The short flag for the option (e.g., "-p", "-c").
        is_flag (bool):
            Whether this is a boolean flag (no value needed).
            Defaults to False.
        type (Any, optional):
            The type to convert the value to (int, str, float, etc.).
        multiple (bool):
            Whether to allow multiple values. Defaults to False.
        help (str, optional):
            Help text for this option.
        required (bool):
            Whether this option is required. Defaults to False.
        default (Any):
            Default value if not provided. Defaults to None.
        tags (str | list[str], optional):
            Tag(s) to associate with this option for grouping.
        **kwargs (Any):
            Additional Click option parameters.

    Returns:
        Callable:
            A decorator function that registers the option parent node.

    Examples:

        ```python
        @option("--port", short="-p", type=int, default=8080)
        def my_func(port):
            print(f"Port: {port}")
        ```

        ```python
        @option("--verbose", short="-v", is_flag=True)
        def my_func(verbose):
            if verbose:
                print("Verbose mode enabled")
        ```

        ```python
        @option("--config-file", help="Path to configuration file")
        def my_func(config_file):
            print(f"Config: {config_file}")
        ```
    """
    return Option.as_decorator(
        long=long,
        short=short,
        is_flag=is_flag,
        type=type,
        multiple=multiple,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
