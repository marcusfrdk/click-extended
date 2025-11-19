"""The node used as a root node."""

# pylint: disable=invalid-name
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=protected-access

import asyncio
from functools import wraps
from typing import Any, Callable, Generic, Mapping, ParamSpec, TypeVar, cast

import click

from click_extended.core._node import Node
from click_extended.core._parent_node import ParentNode
from click_extended.core._tree import Tree
from click_extended.core.argument import Argument
from click_extended.core.env import Env
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

                for global_node in instance.tree.globals:
                    if global_node.inject_name is not None:
                        if global_node.inject_name in seen_names:
                            prev_type, prev_desc = seen_names[
                                global_node.inject_name
                            ]
                            raise DuplicateNameError(
                                global_node.inject_name,
                                prev_type,
                                "global",
                                prev_desc,
                                f"'{global_node.inject_name}'",
                            )
                        seen_names[global_node.inject_name] = (
                            "global",
                            f"'{global_node.inject_name}'",
                        )

                global_values: dict[str, Any] = {}
                parent_list = [
                    cast("ParentNode", p)
                    for p in instance.tree.root.children.values()
                    if isinstance(p, (Option, Argument, Env))
                ]

                for global_node in instance.tree.globals:
                    has_delay = global_node.delay
                    has_executed = global_node._executed  # type: ignore
                    if not has_delay and not has_executed:
                        result = global_node.process(
                            instance.tree,
                            instance,
                            parent_list,
                            tags_dict,
                            instance.tree.globals,
                            call_args,
                            call_kwargs,
                            *global_node.process_args,
                            **global_node.process_kwargs,
                        )

                        if global_node.inject_name is not None:
                            global_values[global_node.inject_name] = result

                missing_env_vars: list[str] = []
                for parent_node in instance.tree.root.children.values():
                    if isinstance(parent_node, Env):
                        missing_var = parent_node.check_required()
                        if missing_var:
                            missing_env_vars.append(missing_var)

                if missing_env_vars:
                    match len(missing_env_vars):
                        case 1:
                            error_msg = (
                                f"Required environment variable "
                                f"'{missing_env_vars[0]}' is not set."
                            )
                        case 2:
                            error_msg = (
                                f"Required environment variables "
                                f"'{missing_env_vars[0]}' and "
                                f"'{missing_env_vars[1]}' are not set."
                            )
                        case _:
                            vars_list = "', '".join(missing_env_vars[:-1])
                            error_msg = (
                                f"Required environment variables "
                                f"'{vars_list}' and '{missing_env_vars[-1]}' "
                                f"are not set."
                            )

                    raise ValueError(error_msg)

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
                        for parent_node in tag.parent_nodes:
                            for child in tag.children.values():
                                child.validate_type(parent_node)

                            value = parent_node.get_value()
                            process_children(
                                value, tag.children, tag, tags_dict
                            )

                for global_node in instance.tree.globals:
                    if global_node.delay:
                        result = global_node.process(
                            instance.tree,
                            instance,
                            parent_list,
                            tags_dict,
                            instance.tree.globals,
                            call_args,
                            call_kwargs,
                            *global_node.process_args,
                            **global_node.process_kwargs,
                        )

                        if global_node.inject_name is not None:
                            global_values[global_node.inject_name] = result

                merged_kwargs: dict[str, Any] = {
                    **call_kwargs,
                    **parent_values,
                    **global_values,
                }

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
        h_flag_taken = False
        if instance.tree.root and instance.tree.root.children:
            seen_short_flags: dict[str, str] = {}
            for parent_node in instance.tree.root.children.values():
                if isinstance(parent_node, Option) and parent_node.short:
                    if parent_node.short == "-h":
                        h_flag_taken = True
                    if parent_node.short in seen_short_flags:
                        prev_name = seen_short_flags[parent_node.short]
                        raise DuplicateNameError(
                            parent_node.short,
                            "option",
                            "option",
                            f"'{prev_name}' ({parent_node.short})",
                            f"'{parent_node.name}' ({parent_node.short})",
                        )
                    seen_short_flags[parent_node.short] = parent_node.name

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
                    arg_kwargs: dict[str, Any] = {
                        "type": parent_node.type,
                        "required": parent_node.required,
                        "nargs": parent_node.nargs,
                        **parent_node.extra_kwargs,
                    }

                    if (
                        not parent_node.required
                        or parent_node.default is not None
                    ):
                        arg_kwargs["default"] = parent_node.default

                    func = click.argument(
                        parent_node.name,
                        **arg_kwargs,
                    )(func)

        if not h_flag_taken:
            if "context_settings" not in kwargs:
                kwargs["context_settings"] = {}
            if "help_option_names" not in kwargs["context_settings"]:
                kwargs["context_settings"]["help_option_names"] = [
                    "-h",
                    "--help",
                ]

        click_decorator = cls._get_click_decorator()
        click_cls = cls._get_click_cls()

        underlying = click_decorator(name=name, cls=click_cls, **kwargs)(func)

        return RootNodeWrapper(underlying=underlying, instance=instance)

    def visualize(self) -> None:
        """Visualize the tree structure."""
        visualize_tree(self.tree.root)
