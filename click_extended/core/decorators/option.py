"""`ParentNode` that represents a Click option."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=redefined-builtin

import asyncio
from builtins import type as builtins_type
from functools import wraps
from typing import Any, Callable, ParamSpec, Type, TypeVar, cast

from click_extended.core.nodes.option_node import OptionNode
from click_extended.core.other.context import Context
from click_extended.utils.naming import is_long_flag, is_short_flag, validate_name

P = ParamSpec("P")
T = TypeVar("T")

SUPPORTED_TYPES = (str, int, float, bool)


class Option(OptionNode):
    """`OptionNode` that represents a Click option."""

    def __init__(
        self,
        name: str,
        *flags: str,
        param: str | None = None,
        is_flag: bool = False,
        type: Any = None,
        nargs: int = 1,
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
            name (str):
                The option name (parameter name) in snake_case,
                SCREAMING_SNAKE_CASE, or kebab-case. Examples: \"config_file\",
                \"CONFIG_FILE\", \"config-file\"
            *flags (str):
                Optional flags for the option. Can include any number of short
                flags (e.g., \"-p\", \"-P\") and long flags (e.g., \"--port\",
                \"--p\"). If no long flags provided, auto-generates
                "--kebab-case(name)".
            param (str, optional):
                Custom parameter name for the function.
                If not provided, uses the name directly.
            is_flag (bool):
                Whether this is a boolean flag (no value needed).
                Defaults to `False`.
            type (Any, optional):
                The type to convert the value to (int, str, float, etc.).
            nargs (int):
                Number of arguments each occurrence accepts. Defaults to `1`.
            multiple (bool):
                Whether the option can be provided multiple times.
                Defaults to `False`.
            help (str, optional):
                Help text for this option.
            required (bool):
                Whether this option is required. Defaults to `False`.
            default (Any):
                Default value if not provided. Defaults to None.
            tags (str | list[str], optional):
                Tag(s) to associate with this option for grouping.
            **kwargs (Any):
                Additional Click option parameters.
        """
        all_args = [name] + list(flags)
        short_flags_found: list[str] = []
        long_flags_found: list[str] = []
        explicit_name = None

        for arg in all_args:
            if is_long_flag(arg):
                long_flags_found.append(arg)
            elif is_short_flag(arg):
                short_flags_found.append(arg)
            elif not arg.startswith("-"):
                if explicit_name is not None:
                    raise ValueError(
                        "Multiple non-flag arguments provided: "
                        f"'{explicit_name}' and '{arg}'. "
                        "Only one explicit name is allowed."
                    )
                explicit_name = arg
            else:
                if arg.startswith("--"):
                    raise ValueError(
                        f"Invalid long flag '{arg}'. "
                        "Must be format: --word "
                        "(lowercase, hyphens allowed, e.g., --port, "
                        "--config-file)"
                    )
                raise ValueError(
                    f"Invalid short flag '{arg}'. Must be format: -X "
                    f"(letters/numbers, e.g., -p, -v, -lws)"
                )

        if explicit_name is not None:
            validate_name(explicit_name, "option name")
            derived_name = explicit_name
        elif long_flags_found:
            derived_name = long_flags_found[0][2:].replace("-", "_")
        else:
            raise ValueError(
                "No explicit name or long flag provided. "
                "Provide either a snake_case name or a long flag (e.g., "
                "--flag) to derive the parameter name."
            )

        flags = tuple(short_flags_found + long_flags_found)
        short_flags_list = short_flags_found
        long_flags_list = long_flags_found

        param_name = param if param is not None else derived_name

        validate_name(param_name, "parameter name")

        if is_flag and type is not None and type != bool:
            raise ValueError(
                f"Cannot specify both is_flag=True and "
                f"type={type.__name__ if hasattr(type, '__name__') else type}. "
                f"Flags are always boolean."
            )

        if is_flag and default is None:
            default = False

        if type is None:
            if is_flag:
                type = bool
            elif default is not None and not (multiple and default == ()):
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
            type = str

        if multiple and default is None:
            default = ()

        super().__init__(
            name=derived_name,
            param=param_name,
            short_flags=short_flags_list,
            long_flags=long_flags_list,
            is_flag=is_flag,
            type=type,
            nargs=nargs,
            multiple=multiple,
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
            The first long flag if available, otherwise the first flag.
        :rtype: str
        """
        if self.long_flags:
            return self.long_flags[0]
        if self.short_flags:
            return self.short_flags[0]
        return self.name

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Load and return the CLI option value.

        :param value:
            The parsed CLI option value from Click.
        :param context:
            The current context instance.
        :param \\*args:
            Optional positional arguments.
        :param \\*\\*kwargs:
            Optional keyword arguments.

        :returns:
            The option value to inject into the function.
        :rtype: Any
        """
        return value


def option(
    name: str,
    *flags: str,
    param: str | None = None,
    is_flag: bool = False,
    type: Type[Any] | Any = None,
    nargs: int = 1,
    multiple: bool = False,
    help: str | None = None,
    required: bool = False,
    default: Any = None,
    tags: str | list[str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A ``ParentNode`` decorator to create a Click option with value injection.

    :param name:
        The option name (parameter name) in snake_case.
        Examples: "verbose", "config_file"
    :param \\*flags:
        Optional flags for the option. Can include any number of short flags
        (e.g., "-v", "-V") and long flags (e.g., "--verbose", "--verb").
        If no long flags provided, auto-generates "--kebab-case(name)".
        Examples:
            @option("verbose", "-v")
            @option("config", "-c", "--cfg", "--config")
            @option("verbose", "-v", "-V", "--verbose", "--verb")
    :param param:
        Custom parameter name for the function.
        If not provided, uses the name directly.
    :param is_flag:
        Whether this is a boolean flag (no value needed).
        Defaults to ``False``.
    :param type:
        The type to convert the value to.
    :param nargs:
        Number of arguments each occurrence accepts. Defaults to ``1``.
    :param multiple:
        Whether the option can be provided multiple times.
        Defaults to ``False``.
    :param help:
        Help text for this option.
    :param required:
        Whether this option is required. Defaults to ``False``.
    :param default:
        Default value if not provided. Defaults to None.
    :param tags:
        Tag(s) to associate with this option for grouping.
    :param \\*\\*kwargs:
        Additional Click option parameters.

    :returns:
        A decorator function that registers the option parent node.
    :rtype: Callable

    Examples:

        ```python
        # Simple: name only (auto-generates --verbose)
        @option("verbose", is_flag=True)
        def my_func(verbose):
            print(f"Verbose: {verbose}")

        # Name with short flag
        @option("port", "-p", type=int, default=8080)
        def my_func(port):
            print(f"Port: {port}")

        # Multiple short and long flags
        @option("verbose", "-v", "-V", "--verb", is_flag=True)
        def my_func(verbose):  # Accepts: -v, -V, --verbose, --verb
            print("Verbose mode")

        # Custom parameter name
        @option("configuration_file", "-c", param="cfg")
        def my_func(cfg):  # param: cfg, CLI: -c, --configuration-file
            print(f"Config: {cfg}")
        ```
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """The actual decorator that wraps the function."""
        from click_extended.core.other._tree import Tree

        instance = Option(
            name,
            *flags,
            param=param,
            is_flag=is_flag,
            type=type,
            nargs=nargs,
            multiple=multiple,
            help=help,
            required=required,
            default=default,
            tags=tags,
            **kwargs,
        )
        Tree.queue_parent(instance)

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Async wrapper that preserves the original function."""
                result = await func(*call_args, **call_kwargs)
                return cast(T, result)

            return cast(Callable[P, T], async_wrapper)

        @wraps(func)
        def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
            """Wrapper that preserves the original function."""
            return func(*call_args, **call_kwargs)

        return wrapper

    return decorator
