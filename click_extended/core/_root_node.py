"""The node used as a root node."""

# pylint: disable=invalid-name
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

import asyncio
from functools import wraps
from typing import Any, Callable, Generic, Mapping, ParamSpec, TypeVar, cast

import click

from click_extended.core._node import Node
from click_extended.core._parent_node import ParentNode
from click_extended.core._tree import Tree
from click_extended.core.argument import Argument
from click_extended.core.option import Option
from click_extended.core.tag import Tag
from click_extended.errors import DuplicateNameError, NoRootError
from click_extended.utils.process import process_children
from click_extended.utils.visualize import visualize_tree

P = ParamSpec("P")
T = TypeVar("T")

WrapperType = TypeVar("WrapperType")
ClickType = TypeVar("ClickType", bound=click.Command)


class RootNodeWrapper(Generic[ClickType]):
    """
    Generic wrapper class for Click commands/groups with visualize() support.

    This wrapper delegates all attribute access to the underlying Click object
    while also providing access to the tree visualization functionality.
    """

    def __init__(self, underlying: ClickType, instance: "RootNode") -> None:
        """
        Initialize the wrapper.

        Args:
            underlying (ClickType):
                The underlying Click Command or Group instance.
            instance (RootNode):
                The `RootNode` instance to wrap.
        """
        self._underlying = underlying
        self._root_instance = instance

    def visualize(self) -> None:
        """Visualize the tree structure."""
        self._root_instance.visualize()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Allow the wrapper to be called like the underlying Click object."""
        return self._underlying(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate all other attribute access to the underlying object."""
        return getattr(self._underlying, name)


class RootNode(Node):
    """The node used as a root node."""

    parent: None
    tree: Tree

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a new `RootNode` instance.

        Args:
            name (str):
                The name of the node.
            *args (Any):
                Additional positional arguments (stored but not passed to Node).
            **kwargs (Any):
                Additional keyword arguments (stored but not passed to Node).
        """
        super().__init__(name=name)
        self.children = {}
        self.tree = Tree()
        self.extra_args = args
        self.extra_kwargs = kwargs

    @property
    def children(
        self,
    ) -> Mapping[str | int, "ParentNode"]:
        """Get the children with proper ParentNode typing."""
        return cast(Mapping[str | int, "ParentNode"], self._children)

    @children.setter
    def children(self, value: dict[str | int, Node] | None) -> None:
        """Set the children storage."""
        self._children = value

    @classmethod
    def _get_click_decorator(cls) -> Callable[..., Any]:
        """
        Return the Click decorator (command or group) to use.

        Subclasses must override this to specify which Click decorator to use.

        Returns:
            Callable:
                The Click decorator function (e.g.,
                `click.command`, `click.group`).
        """
        raise NotImplementedError(
            "Subclasses must implement _get_click_decorator()"
        )

    @classmethod
    def _get_click_cls(cls) -> type[click.Command]:
        """
        Return the Click class to use for aliasing.

        Subclasses must override this to specify which aliased
        Click class to use.

        Returns:
            type[click.Command]:
                The Click class (e.g., `AliasedCommand`, `AliasedGroup`).
        """
        raise NotImplementedError("Subclasses must implement _get_click_cls()")

    @classmethod
    def as_decorator(
        cls, name: str | None = None, /, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Any]:
        """
        Return a decorator representation of the root node.

        The root node is the top-level decorator that triggers tree building
        and collects values from all parent nodes. When the decorated function
        is called, it injects parent node values as keyword arguments.

        Args:
            name (str, optional):
                The name of the root node. If None, uses the decorated
                function's name.
            **kwargs (Any):
                Additional keyword arguments for the specific root type.

        Returns:
            Callable:
                A decorator function that registers the root node
                and builds the tree.
        """

        def decorator(func: Callable[..., Any]) -> Any:
            """The actual decorator that wraps the function."""
            node_name = name if name is not None else func.__name__
            instance = cls(name=node_name, **kwargs)
            instance.tree.register_root(instance)
            original_func = func

            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                def sync_func(*sync_args: Any, **sync_kwargs: Any) -> Any:
                    """Synchronous wrapper for async function."""
                    return asyncio.run(original_func(*sync_args, **sync_kwargs))

                func = sync_func

            @wraps(func)
            def wrapper(*call_args: Any, **call_kwargs: Any) -> Any:
                """Wrapper that collects parent values and injects them."""
                parent_values: dict[str, Any] = {}

                if instance.tree.root is None:
                    raise NoRootError

                assert instance.tree.root.children is not None

                all_tag_names: set[str] = set()
                for parent_node in instance.tree.root.children.values():
                    if isinstance(
                        parent_node, (Option, Argument, type(parent_node))
                    ):
                        all_tag_names.update(parent_node.tags)

                tags_dict: dict[str, "Tag"] = {}
                for tag_name, tag in instance.tree.tags.items():
                    tags_dict[tag_name] = tag
                    tag.parent_nodes = []

                for tag_name in all_tag_names:
                    if tag_name not in tags_dict:
                        auto_tag = Tag(name=tag_name)
                        tags_dict[tag_name] = auto_tag
                        auto_tag.parent_nodes = []

                for parent_node in instance.tree.root.children.values():
                    if isinstance(
                        parent_node, (Option, Argument, type(parent_node))
                    ):
                        for tag_name in parent_node.tags:
                            if tag_name in tags_dict:
                                tags_dict[tag_name].parent_nodes.append(
                                    parent_node
                                )

                seen_names: dict[str, tuple[str, str]] = {}

                for parent_node in instance.tree.root.children.values():
                    if isinstance(
                        parent_node, (Option, Argument, type(parent_node))
                    ):
                        node_type = parent_node.__class__.__name__.lower()
                        node_desc = f"'{parent_node.name}'"

                        if parent_node.name in seen_names:
                            prev_type, prev_desc = seen_names[parent_node.name]
                            raise DuplicateNameError(
                                parent_node.name,
                                prev_type,
                                node_type,
                                prev_desc,
                                node_desc,
                            )
                        seen_names[parent_node.name] = (node_type, node_desc)

                for tag_name in tags_dict:
                    if tag_name in seen_names:
                        prev_type, prev_desc = seen_names[tag_name]
                        raise DuplicateNameError(
                            tag_name,
                            prev_type,
                            "tag",
                            prev_desc,
                            f"'{tag_name}'",
                        )
                    seen_names[tag_name] = ("tag", f"'{tag_name}'")

                for (
                    parent_name,
                    parent_node,
                ) in instance.tree.root.children.items():
                    if isinstance(parent_name, str):
                        if isinstance(parent_node, (Option, Argument)):
                            raw_value = call_kwargs.get(parent_name)
                            was_provided = (
                                parent_name in call_kwargs
                                and raw_value != parent_node.default
                            )
                            parent_node.set_raw_value(raw_value, was_provided)

                            if parent_node.children:
                                parent_values[parent_name] = process_children(
                                    raw_value,
                                    parent_node.children,
                                    parent_node,
                                    tags_dict,
                                )
                            else:
                                parent_values[parent_name] = raw_value
                        else:
                            parent_values[parent_name] = parent_node.get_value()

                for tag_name, tag in instance.tree.tags.items():
                    if tag.children:
                        process_children(None, tag.children, tag, tags_dict)

                merged_kwargs: dict[str, Any] = {**call_kwargs, **parent_values}

                return func(*call_args, **merged_kwargs)

            return cls.wrap(wrapper, node_name, instance, **kwargs)

        return decorator

    @classmethod
    def wrap(
        cls,
        wrapped_func: Callable[..., Any],
        name: str,
        instance: "RootNode",
        **kwargs: Any,
    ) -> Any:
        """
        Apply Click wrapping after value injection.

        This method applies the appropriate Click decorator (command or group)
        and wraps it in a RootNodeWrapper for tree visualization support.

        Args:
            wrapped_func (Callable):
                The function already wrapped with value injection.
            name (str):
                The name of the root node.
            instance (RootNode):
                The `RootNode` instance that owns this tree.
            **kwargs (Any):
                Additional keyword arguments passed to the Click decorator.

        Returns:
            RootNodeWrapper:
                A wrapper containing the Click object with visualize() support.
        """
        func = wrapped_func
        if instance.tree.root and instance.tree.root.children:
            parent_items = list(instance.tree.root.children.items())
            for _parent_name, parent_node in reversed(parent_items):
                if isinstance(parent_node, Option):
                    params: list[str] = []
                    if parent_node.short:
                        params.append(parent_node.short)
                    params.append(parent_node.long)

                    func = click.option(
                        *params,
                        type=parent_node.type,
                        default=parent_node.default,
                        required=parent_node.required,
                        is_flag=parent_node.is_flag,
                        multiple=parent_node.multiple,
                        help=parent_node.help,
                        **parent_node.extra_kwargs,
                    )(func)

                elif isinstance(parent_node, Argument):
                    func = click.argument(
                        parent_node.name,
                        type=parent_node.type,
                        default=parent_node.default,
                        nargs=parent_node.nargs,
                        **parent_node.extra_kwargs,
                    )(func)

        click_decorator = cls._get_click_decorator()
        click_cls = cls._get_click_cls()

        underlying = click_decorator(name=name, cls=click_cls, **kwargs)(func)

        return RootNodeWrapper(underlying=underlying, instance=instance)

    def visualize(self) -> None:
        """Visualize the tree structure."""
        visualize_tree(self.tree.root)
