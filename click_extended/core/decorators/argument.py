"""Class to support arguments in the command line interface."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from builtins import type as builtins_type
from typing import Any, Type, cast

from click_extended.core.nodes.argument_node import ArgumentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.casing import Casing
from click_extended.utils.humanize import humanize_type
from click_extended.utils.naming import validate_name

_MISSING = object()
SUPPORTED_TYPES = (str, int, float, bool)


class Argument(ArgumentNode):
    """`ArgumentNode` that represents a Click argument."""

    def __init__(
        self,
        name: str,
        param: str | None = None,
        nargs: int = 1,
        type: Type[Any] | Any = None,
        help: str | None = None,
        required: bool = True,
        default: Any = _MISSING,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        r"""
        Initialize a new ``Argument`` instance.

        :param name:
            The argument name in snake_case.
            Examples: "filename", "input_file"
        :param param:
            Custom parameter name for the function.
            If not provided, uses the name directly.
        :param nargs:
            Number of arguments to accept. Use ``-1`` for unlimited.
            Defaults to ``1``.
        :param type:
            The type to convert the value to (``int``, ``str``, ``float``,
            etc.).
        :param help:
            Help text for this argument.
        :param required:
            Whether this argument is required. Defaults to ``True`` unless
            ``default`` is provided, which makes it optional automatically.
        :param default:
            Default value if not provided. When set, automatically makes
            the argument optional (``required=False``). Defaults to ``None``.
        :param tags:
            Tag(s) to associate with this argument for grouping.
        :param \*\*kwargs:
            Additional keyword arguments.

        :raises ValueError:
            If both ``default`` is provided and ``required=True`` is
            explicitly set (detected via kwargs inspection in
            decorator).
        """
        validate_name(name, "argument name")

        param_name = param if param is not None else name

        validate_name(param_name, "parameter name")

        if default is not _MISSING and required is True:
            required = False

        if default is _MISSING:
            default = None

        if type is None:
            if default is not None:
                inferred_type = cast(  # type: ignore
                    Type[Any],
                    builtins_type(default),
                )
                if inferred_type in SUPPORTED_TYPES:
                    type = inferred_type
                else:
                    type = str
            else:
                type = str
        elif type not in SUPPORTED_TYPES:
            types = humanize_type(type.__name__ if hasattr(type, "__name__") else type)
            raise ValueError(
                f"Argument '{name}' has unsupported type '{types}'. "
                "Only basic primitives are supported: str, int, float, bool. "
                "For complex types, use child decorators (e.g., @to_path, "
                "@to_datetime, ..)."
            )

        super().__init__(
            name=name,
            param=param if param is not None else name,
            nargs=nargs,
            type=type,
            help=help,
            required=required,
            default=default,
            tags=tags,
        )
        self.extra_kwargs = kwargs

    def get_display_name(self) -> str:
        """
        Get a formatted display name for error messages.

        :returns:
            The argument name in SCREAMING_SNAKE_CASE.
        :rtype: str
        """
        return Casing.to_screaming_snake_case(self.name)

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Load and return the CLI argument value.

        :param value:
            The parsed CLI argument value from Click.
        :param context:
            The current context instance.
        :param \*args:
            Optional positional arguments.
        :param \*\*kwargs:
            Optional keyword arguments.

        :returns:
            The argument value to inject into the function.
        :rtype: Any
        """
        return value


def argument(
    name: str,
    param: str | None = None,
    nargs: int = 1,
    type: Type[str | int | float | bool] | None = None,
    help: str | None = None,
    required: bool = True,
    default: Any = _MISSING,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Decorator:
    r"""
    A ``ParentNode`` decorator to create a Click argument with value injection.

    :param name:
        The argument name in snake_case.
        Examples: "filename", "input_file"
    :param param:
        Custom parameter name for the function.
        If not provided, uses the name directly.
    :param nargs:
        Number of arguments to accept. Use ``-1`` for unlimited.
        Defaults to ``1``.
    :param type:
        The type to convert the value to.
    :param help:
        Help text for this argument.
    :param required:
        Whether this argument is required. Defaults to ``True`` unless
        ``default`` is provided, which automatically makes it optional.
    :param default:
        Default value if not provided. When set, automatically makes
        the argument optional (``required=False``). Defaults to ``None``.
    :param tags:
        Tag(s) to associate with this argument for grouping.
    :param \*\*kwargs:
        Additional Click argument parameters.

    :returns:
        A decorator function that registers the argument parent node.
    :rtype: Decorator

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

        ```python
        # Custom parameter name
        @argument("input_file", param="infile")
        def my_func(infile):  # param: infile, CLI: INPUT_FILE
            print(f"Input: {infile}")
        ```
    """
    return Argument.as_decorator(
        name=name,
        param=param,
        nargs=nargs,
        type=type,
        help=help,
        required=required,
        default=default,
        tags=tags,
        **kwargs,
    )
