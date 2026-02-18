"""OptionNode abstract base class for CLI option nodes."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin
# pylint: disable=arguments-differ
# pylint: disable=line-too-long

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, Type, TypeVar

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.utils.casing import Casing

if TYPE_CHECKING:
    from click_extended.core.other.context import Context

P = ParamSpec("P")
T = TypeVar("T")


class OptionNode(ParentNode, ABC):
    """
    Abstract base class for nodes that receive CLI option values.

    OptionNode extends ParentNode to handle command-line options (flags).
    The key difference is that the `load()` method receives a `value`
    parameter containing the parsed CLI option value.
    """

    def __init__(
        self,
        name: str,
        param: str | None = None,
        short_flags: list[str] | None = None,
        long_flags: list[str] | None = None,
        is_flag: bool = False,
        type: Type[Any] | None = None,
        nargs: int = 1,
        multiple: bool = False,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ):
        r"""
        Initialize a new ``OptionNode`` instance.

        :param name: The option name (parameter name for injection).
        :param param: Custom parameter name for the function.
            If not provided, uses ``name``.
        :param short_flags: Short flags for the option (e.g., ["-p", "-P"]).
        :param long_flags: Long flags for the option (e.g., ["--port", "--p"]).
            If not provided, auto-generates ["--kebab-case(name)"].
        :param is_flag: Whether this is a boolean flag (no value needed).
            Defaults to ``False``.
        :param type: The type to convert the value to (``int``, ``str``, ``float``, ``bool``).
        :param nargs: Number of arguments each occurrence accepts. Defaults to ``1``.
        :param multiple: Whether the option can be provided multiple times.
            Defaults to ``False``.
        :param help: Help text for this option.
        :param required: Whether this option is required. Defaults to ``False``.
        :param default: Default value if not provided. Defaults to ``None``.
        :param tags: Tag(s) to associate with this option for grouping.
        :param \*\*kwargs: Additional keyword arguments passed to parent class.
        """
        super().__init__(
            name=param if param is not None else name,
            param=param,
            help=help,
            required=required,
            default=default,
            tags=tags,
            **kwargs,
        )
        self.short_flags = short_flags if short_flags is not None else []
        self.long_flags = (
            long_flags
            if long_flags is not None and len(long_flags) > 0
            else [f"--{Casing.to_kebab_case(name)}"]
        )
        self.is_flag = is_flag
        self.type = type
        self.nargs = nargs
        self.multiple = multiple

    @abstractmethod
    def load(
        self,
        value: str | int | float | bool | None,
        context: "Context",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        r"""
        Load and process the CLI option value.

        This method is called with the parsed CLI option value and should
        return the processed value to be injected into the function.

        :param value: The parsed CLI option value from Click.
        :param context: The current context instance.
        :param \*args: Optional positional arguments.
        :param \*\*kwargs: Optional keyword arguments.

        :returns: The processed value to inject into the function.
        """
        raise NotImplementedError

    @classmethod
    def as_decorator(
        cls,
        *,
        name: str,
        param: str | None = None,
        short_flags: list[str] | None = None,
        long_flags: list[str] | None = None,
        is_flag: bool = False,
        type: Type[Any] | None = None,
        nargs: int = 1,
        multiple: bool = False,
        help: str | None = None,
        required: bool = False,
        default: Any = None,
        tags: str | list[str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        r"""
        Return a decorator representation of the option node.

        :param name: The option name (parameter name for injection).
        :param param: Custom parameter name for the function.
            If not provided, uses ``name``.
        :param short_flags: Short flags for the option (e.g., ["-p", "-P"]).
        :param long_flags: Long flags for the option (e.g., ["--port", "--p"]).
        :param is_flag: Whether this is a boolean flag (no value needed).
            Defaults to ``False``.
        :param type: The type to convert the value to (``int``, ``str``, ``float``, ``bool``).
        :param nargs: Number of arguments each occurrence accepts. Defaults to ``1``.
        :param multiple: Whether the option can be provided multiple times.
            Defaults to ``False``.
        :param help: Help text for this option.
        :param required: Whether this option is required. Defaults to ``False``.
        :param default: Default value if not provided. Defaults to ``None``.
        :param tags: Tag(s) to associate with this option for grouping.
        :param \*\*kwargs: Additional keyword arguments passed to __init__ and load().

        :returns: A decorator function that registers the option node.
        :rtype: Callable
        """
        return super().as_decorator(
            name=name,
            param=param,
            short_flags=short_flags,
            long_flags=long_flags,
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


__all__ = ["OptionNode"]
