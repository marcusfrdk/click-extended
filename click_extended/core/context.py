"""Context with a unified all contextual information across the context."""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from click import Context as ClickContext

    from click_extended.core._root_node import RootNode
    from click_extended.core.child_node import ChildNode
    from click_extended.core.node import Node
    from click_extended.core.parent_node import ParentNode
    from click_extended.core.tag import Tag
    from click_extended.decorators.parents.argument import Argument
    from click_extended.decorators.parents.env import Env
    from click_extended.decorators.parents.option import Option


@dataclass(frozen=True)
class Context:
    """
    Context with a unified all contextual information across the context.

    Attributes:
      root (RootNode):
        The root command node of the entire CLI tree.
      current (Node | None):
        The current node being processed.
      parent (ParentNode | Tag):
        The parent node (Option, Argument, Env, or Tag) that contains
        the current child.
      click_context (ClickContext):
        The Click context object.
      nodes (dict[str, Node]):
        All registered nodes in the tree.
      parents (dict[str, ParentNode]):
        All parent nodes (Option/Argument/Env).
      tags (dict[str, Tag]):
        All tag instances by name.
      children (dict[str, ChildNode]):
        All child node instances.
      data (dict[str, Any]):
        Shared data store accessible across all nodes. Use this to pass
        custom data between nodes.
      debug (bool):
        Debug mode flag. When `True`, handler exceptions show full tracebacks.
        Set via `@debug()` decorator.
    """

    root: "RootNode"
    current: "Node | None"
    parent: "ParentNode | Tag | None"
    click_context: "ClickContext"
    nodes: dict[str, "Node"]
    parents: dict[str, "ParentNode"]
    tags: dict[str, "Tag"]
    children: dict[str, "ChildNode"]
    data: dict[str, Any]
    debug: bool = False

    def is_root(self) -> bool:
        """
        Check if the current node is a `RootNode` instance.

        Returns:
            bool:
                `True` if current node is a `RootNode`, `False` otherwise.
        """
        from click_extended.core._root_node import RootNode

        return isinstance(self.current, RootNode)

    def is_parent(self) -> bool:
        """
        Check if the current node is a `ParentNode` instance.

        Returns:
            bool:
                `True` if current node is a `ParentNode`, `False` otherwise.
        """
        from click_extended.core.parent_node import ParentNode

        return isinstance(self.current, ParentNode)

    def is_tag(self) -> bool:
        """
        Check if the parent node is a `Tag` instance.

        Returns:
            bool:
                `True` if parent is a `Tag`, `False` otherwise.
        """
        from click_extended.core.tag import Tag

        return isinstance(self.parent, Tag)

    def is_child(self) -> bool:
        """
        Check if the current node is a `ChildNode` instance.

        Returns:
            bool:
                `True` if current node is a `ChildNode`, `False` otherwise.
        """
        from click_extended.core.child_node import ChildNode

        return isinstance(self.current, ChildNode)

    def is_argument(self) -> bool:
        """
        Check if the current node is an `Argument` instance.

        Returns:
            bool:
                `True` if current node is an `Argument`, `False` otherwise.
        """
        from click_extended.decorators.parents.argument import Argument

        return isinstance(self.current, Argument)

    def is_option(self) -> bool:
        """
        Check if the current node is an `Option` instance.

        Returns:
            bool:
                `True` if current node is an `Option`, `False` otherwise.
        """
        from click_extended.decorators.parents.option import Option

        return isinstance(self.current, Option)

    def is_env(self) -> bool:
        """
        Check if the current node is an `Env` instance.

        Returns:
            bool:
                `True` if current node is an `Env`, `False` otherwise.
        """
        from click_extended.decorators.parents.env import Env

        return isinstance(self.current, Env)

    def is_tagged(self) -> bool:
        """
        Check if the current instance is tagged.

        Returns:
            bool:
                `True` if current node has tags, `False` otherwise.
        """
        from click_extended.core.parent_node import ParentNode

        if isinstance(self.current, ParentNode):
            return len(self.current.tags) > 0
        return False

    def get_root(self) -> "RootNode":
        """
        Get the root node.

        Returns:
            RootNode:
                The root node of the tree.
        """
        return self.root

    def get_children(self, name: str | None = None) -> list["ChildNode"]:
        """
        Get a list of all children defined under the same parent.

        Args:
            name (str | None, optional):
                The parent name to get children from. If `None`,
                uses the current parent.

        Returns:
            list[ChildNode]:
                List of child nodes under the specified parent.
        """
        from click_extended.core.child_node import ChildNode
        from click_extended.core.parent_node import ParentNode

        if name is not None:
            parent = self.get_parent(name)
            if parent is None:
                return []
        elif isinstance(self.parent, ParentNode):
            parent = self.parent
        else:
            return []

        if not parent.children:
            return []

        return [
            child
            for child in parent.children.values()
            if isinstance(child, ChildNode)
        ]

    def get_siblings(self) -> list["ChildNode"]:
        """
        Get a list of all siblings in the current parent, excluding the
        current child.

        Returns:
            list[ChildNode]:
                List of sibling child nodes.
        """
        from click_extended.core.child_node import ChildNode

        if not isinstance(self.current, ChildNode):
            return []

        all_children = self.get_children()
        return [child for child in all_children if child is not self.current]

    def get_parent(self, name: str) -> "ParentNode | None":
        """
        Get a parent node by name.

        Args:
            name (str):
                The parent node name to retrieve.

        Returns:
            ParentNode | None:
                The parent node if found, `None` otherwise.
        """
        return self.parents.get(name)

    def get_node(self, name: str) -> "Node | None":
        """
        Get any node by name.

        Args:
            name (str):
                The node name to retrieve.

        Returns:
            Node | None:
                The node if found, `None` otherwise.
        """
        return self.nodes.get(name)

    def get_tag(self, name: str) -> "Tag | None":
        """
        Get a tag by name.

        Args:
            name (str):
                The tag name to retrieve.

        Returns:
            Tag | None:
                The tag if found, `None` otherwise.
        """
        return self.tags.get(name)

    def get_tagged(self) -> dict[str, list["ParentNode"]]:
        """
        Get a dictionary of tagged `ParentNode` instances.

        Returns:
            dict[str, list[ParentNode]]:
                Dictionary mapping tag names to lists of parent nodes.
        """
        result: dict[str, list["ParentNode"]] = {}
        for parent in self.parents.values():
            for tag in parent.tags:
                if tag not in result:
                    result[tag] = []
                result[tag].append(parent)
        return result

    def get_provided_arguments(self) -> list["Argument"]:
        """
        Get all provided positional arguments.

        Returns:
            list[Argument]:
                List of provided argument nodes.
        """
        from click_extended.decorators.parents.argument import Argument

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Argument) and parent.was_provided
        ]

    def get_provided_options(self) -> list["Option"]:
        """
        Get all provided keyword arguments.

        Returns:
            list[Option]:
                List of provided option nodes.
        """
        from click_extended.decorators.parents.option import Option

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Option) and parent.was_provided
        ]

    def get_provided_envs(self) -> list["Env"]:
        """
        Get all provided environment variables.

        Returns:
            list[Env]:
                List of provided env nodes.
        """
        from click_extended.decorators.parents.env import Env

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Env) and parent.was_provided
        ]

    def get_provided_value(self, name: str) -> Any:
        """
        Get the provided value of a parent node.

        Args:
            name (str):
                The parent node name.

        Returns:
            Any:
                The raw value if parent exists and was provided, `None`
                otherwise.
        """
        parent = self.get_parent(name)
        if parent is not None and parent.was_provided:
            return parent.cached_value  # type: ignore
        return None

    def get_missing_arguments(self) -> list["Argument"]:
        """
        Get all missing positional arguments.

        Returns:
            list[Argument]:
                List of all argument nodes.
        """
        from click_extended.decorators.parents.argument import Argument

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Argument) and not parent.was_provided
        ]

    def get_missing_options(self) -> list["Option"]:
        """
        Get all missing keyword arguments.

        Returns:
            list[Option]:
                List of all option nodes.
        """
        from click_extended.decorators.parents.option import Option

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Option) and not parent.was_provided
        ]

    def get_missing_envs(self) -> list["Env"]:
        """
        Get all missing environment variables.

        Returns:
            list[Env]:
                List of all env nodes.
        """
        from click_extended.decorators.parents.env import Env

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Env) and not parent.was_provided
        ]

    def get_current_tags(self) -> list[str]:
        """
        Get a list of the tags of the current node.

        Returns:
            list[str]:
                List of tag names for the current node.
        """
        from click_extended.core.parent_node import ParentNode

        if isinstance(self.current, ParentNode):
            return list(self.current.tags)
        return []

    def get_current_values(self) -> dict[str, Any]:
        """
        Get the processed value of all source nodes.

        Returns:
            dict[str, Any]:
                Dictionary mapping parent names to their processed values.
        """
        return {
            name: parent.get_value() for name, parent in self.parents.items()
        }
