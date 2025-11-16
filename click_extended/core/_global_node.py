"""Global node for tree-level observation and value injection."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-builtin

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from click_extended.core._node import Node
from click_extended.core._tree import queue_global

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode
    from click_extended.core._root_node import RootNode
    from click_extended.core._tree import Tree
    from click_extended.core.tag import Tag

P = ParamSpec("P")
T = TypeVar("T")


class GlobalNode(Node, ABC):
    """
    A node that executes at the tree level for observation or value injection.

    GlobalNodes can execute at two different points in the tree lifecycle:
    - Early execution (delay=False): After name validation, before env checks
    - Late execution (delay=True): After parent value collection,
      before function call

    They can operate in two modes:
    - Observer mode (name=None): Execute logic without injecting values
    - Injection mode (name="var"): Execute and inject return value into
      function.
    """

    def __init__(
        self,
        name: str | None = None,
        delay: bool = False,
    ) -> None:
        """
        Initialize a new `GlobalNode` instance.

        Args:
            name (str | None):
                The parameter name to inject the return value into.
                If `None`, runs in observer mode (no injection).
            delay (bool):
                Whether to delay execution until after parent value collection.
                If `False`, executes early in the tree lifecycle.
                Defaults to `False`.
        """
        internal_name = name if name is not None else f"_global_{id(self)}"
        super().__init__(name=internal_name, children=None)

        self.inject_name = name
        self.delay = delay
        self.process_args: tuple[Any, ...] = ()
        self.process_kwargs: dict[str, Any] = {}
        self._executed = False

    @abstractmethod
    def process(
        self,
        tree: "Tree",
        root: "RootNode",
        parents: list["ParentNode"],
        tags: dict[str, "Tag"],
        globals: list["GlobalNode"],
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the global node logic.

        This method is called at the appropriate point in the tree lifecycle
        based on the `delay` setting.

        Args:
            tree (Tree):
                The tree object.
            root (RootNode):
                The root node (`Command` or `Group`).
            parents (list[ParentNode]):
                List of all `ParentNode` instances
                (`Option`, `Argument`, `Env`).
            tags (dict[str, Tag]):
                Dictionary mapping tag names to `Tag` instances.
            globals (list[GlobalNode]):
                List of all registered `GlobalNode` instances (including self).
            call_args (tuple):
                Positional arguments passed to the Click command.
            call_kwargs (dict):
                Keyword arguments passed to the Click command.
            *args (Any):
                Additional positional arguments from `as_decorator`.
            **kwargs (Any):
                Additional keyword arguments from `as_decorator`.

        Returns:
            Any:
                If `name` is set, this value will be injected into
                the function (including `None`). If name is `None`,
                the return value is ignored.
        """
        raise NotImplementedError

    @classmethod
    def as_decorator(
        cls,
        name: str | None = None,
        /,
        delay: bool = False,
        **kwargs: Any,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """
        Return a decorator representation of the global node.

        Args:
            name (str | None):
                The parameter name to inject the return value into.
                If `None`, runs in observer mode.
            delay (bool):
                Whether to delay execution until after parent value collection.
                Defaults to `False`.
            **kwargs (Any):
                Additional keyword arguments stored and passed to process
                method.

        Returns:
            Callable:
                A decorator function that registers the global node.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            """The actual decorator that wraps the function."""
            instance = cls(name=name, delay=delay)
            instance.process_kwargs = kwargs
            queue_global(instance)

            @wraps(func)
            def wrapper(*call_args: P.args, **call_kwargs: P.kwargs) -> T:
                """Wrapper that preserves the original function."""
                return func(*call_args, **call_kwargs)

            return wrapper

        return decorator
