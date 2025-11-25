"""`ParentNode` that represents a Click option."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin
# pylint: disable=too-many-locals

from builtins import type as builtins_type
from typing import Any, Callable, ParamSpec, Type, TypeVar, cast

from click_extended.core.context import Context
from click_extended.core.option_node import OptionNode
from click_extended.utils.casing import Casing
from click_extended.utils.naming import (
    is_long_flag,
    is_short_flag,
    validate_name,
)

P = ParamSpec("P")
T = TypeVar("T")


class Option(OptionNode):
    """`OptionNode` that represents a Click option."""

    def __init__(
        self,
        name: str,
        *,
        short: str | None = None,
        long: str | None = None,
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
                The option name in snake_case, SCREAMING_SNAKE_CASE,
                or kebab-case. Examples: "config_file", "CONFIG_FILE",
                "config-file"

                Can also be a long flag directly
                (e.g., "--config-file"). If a long flag is provided,
                the parameter name is derived from it.
            short (str, optional):
                The short flag for the option (e.g., "-p").
            long (str, optional):
                Explicit long flag override (e.g., "--cfg").
                If not provided, auto-generated from name as "--kebab-case".
            param (str, optional):
                Custom parameter name for the function.
                If not provided, derived from name as `snake_case`.
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
        # When @option("--my-option")
        if is_long_flag(name):
            derived_name = name[2:]
            long_flag = name if long is None else long

        # When @option("my_option") or @option("my-option")
        else:
            validate_name(name, "option name")
            derived_name = name
            long_flag = (
                long if long is not None else f"--{Casing.to_kebab_case(name)}"
            )

        if not is_long_flag(long_flag):
            raise ValueError(
                f"Invalid long flag '{long_flag}'. "
                "Must be format: --word "
                "(lowercase, hyphens allowed, e.g., --port, --config-file)"
            )

        if short is not None and not is_short_flag(short):
            raise ValueError(
                f"Invalid short flag '{short}'. Must be format: -X "
                f"(e.g., -p, -v, -h)"
            )

        param_name = (
            param if param is not None else Casing.to_snake_case(derived_name)
        )

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
            if default is not None:
                type = cast(Type[Any], builtins_type(default))  # type: ignore
            else:
                type = str

        super().__init__(
            name=derived_name,
            param=param_name,
            short=short,
            long=long_flag,
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

    def load(
        self,
        value: str | int | float | bool | None,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Load and return the CLI option value.

        Args:
            value (str | int | float | bool | None):
                The parsed CLI option value from Click.
            context (Context):
                The current context instance.
            *args (Any):
                Optional positional arguments.
            **kwargs (Any):
                Optional keyword arguments.

        Returns:
            Any:
                The option value to inject into the function.
        """
        return value


def option(
    name: str,
    short: str | None = None,
    long: str | None = None,
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
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to create a Click option with value injection.

    Args:
        name (str):
            The option name in snake_case, SCREAMING_SNAKE_CASE, or kebab-case.
            Can also be a long flag (e.g., "--config-file").
        short (str, optional):
            The short flag for the option (e.g., "-p", "-c").
        long (str, optional):
            Explicit long flag override (e.g., "--cfg").
            If not provided, auto-generated from name as "--kebab-case".
        param (str, optional):
            Custom parameter name for the function.
            If not provided, derived from name as snake_case.
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

    Returns:
        Callable:
            A decorator function that registers the option parent node.

    Examples:

        ```python
        # Simple: name derives everything
        @option("port", short="-p", type=int, default=8080)
        def my_func(port):  # param: port, CLI: --port
            print(f"Port: {port}")

        # Using long flag directly
        @option("--verbose", short="-v", is_flag=True)
        def my_func(verbose):  # param: verbose, CLI: --verbose
            if verbose:
                print("Verbose mode enabled")

        # Custom long flag
        @option("config_file", long="--cfg", help="Config file")
        def my_func(config_file):  # param: config_file, CLI: --cfg
            print(f"Config: {config_file}")

        # Custom parameter name
        @option("configuration_file", param="cfg")
        def my_func(cfg):  # param: cfg, CLI: --configuration-file
            print(f"Config: {cfg}")
        ```
    """
    return Option.as_decorator(
        name=name,
        short=short,
        long=long,
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
