"""Context with a unified all contextual information across the context."""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from click import Context as ClickContext

    from click_extended.core.decorators.argument import Argument
    from click_extended.core.decorators.env import Env
    from click_extended.core.decorators.option import Option
    from click_extended.core.decorators.tag import Tag
    from click_extended.core.nodes._root_node import RootNode
    from click_extended.core.nodes.child_node import ChildNode
    from click_extended.core.nodes.node import Node
    from click_extended.core.nodes.parent_node import ParentNode


@dataclass(frozen=True)
class Context:
    """
    Context with a unified all contextual information across the context.

    :Attributes:
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
        Debug mode flag. When ``True``, handler exceptions show full tracebacks.
        Set via ``@debug()`` decorator.
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
        Check if the current node is a ``RootNode`` instance.

        :returns:
            ``True`` if current node is a ``RootNode``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.nodes._root_node import RootNode

        return isinstance(self.current, RootNode)

    def is_parent(self) -> bool:
        """
        Check if the current node is a ``ParentNode`` instance.

        :returns:
            ``True`` if current node is a ``ParentNode``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.nodes.parent_node import ParentNode

        return isinstance(self.current, ParentNode)

    def is_tag(self) -> bool:
        """
        Check if the parent node is a ``Tag`` instance.

        :returns:
            ``True`` if parent is a ``Tag``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.decorators.tag import Tag

        return isinstance(self.parent, Tag)

    def is_child(self) -> bool:
        """
        Check if the current node is a ``ChildNode`` instance.

        :returns:
            ``True`` if current node is a ``ChildNode``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.nodes.child_node import ChildNode

        return isinstance(self.current, ChildNode)

    def is_argument(self) -> bool:
        """
        Check if the current node is an ``Argument`` instance.

        :returns:
            ``True`` if current node is an ``Argument``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.decorators.argument import Argument

        return isinstance(self.current, Argument)

    def is_option(self) -> bool:
        """
        Check if the current node is an ``Option`` instance.

        :returns:
            ``True`` if current node is an ``Option``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.decorators.option import Option

        return isinstance(self.current, Option)

    def is_env(self) -> bool:
        """
        Check if the current node is an ``Env`` instance.

        :returns:
            ``True`` if current node is an ``Env``, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.decorators.env import Env

        return isinstance(self.current, Env)

    def is_tagged(self) -> bool:
        """
        Check if the current instance is tagged.

        :returns:
            ``True`` if current node has tags, ``False`` otherwise.
        :rtype: bool
        """
        from click_extended.core.nodes.parent_node import ParentNode

        if isinstance(self.current, ParentNode):
            return len(self.current.tags) > 0
        return False

    def get_root(self) -> "RootNode":
        """
        Get the root node.

        :returns:
            The root node of the tree.
        :rtype: RootNode
        """
        return self.root

    def get_children(self, name: str | None = None) -> list["ChildNode"]:
        """
        Get a list of all children defined under the same parent.

        :param name:
            The parent name to get children from. If ``None``,
            uses the current parent.

        :returns:
            List of child nodes under the specified parent.
        :rtype: list[ChildNode]
        """
        from click_extended.core.decorators.tag import Tag
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.nodes.parent_node import ParentNode

        if name is not None:
            parent: "ParentNode | Tag | None" = self.get_parent(name)
            if parent is None:
                return []
        elif isinstance(self.parent, (ParentNode, Tag)):
            parent = self.parent
        else:
            return []

        if not parent.children:
            return []

        return [
            child for child in parent.children.values() if isinstance(child, ChildNode)
        ]

    def get_siblings(self) -> list["ChildNode"]:
        """
        Get a list of all siblings in the current parent, excluding the
        current child.

        :returns:
            List of sibling child nodes.
        :rtype: list[ChildNode]
        """
        from click_extended.core.nodes.child_node import ChildNode

        if not isinstance(self.current, ChildNode):
            return []

        all_children = self.get_children()
        return [child for child in all_children if child is not self.current]

    def get_parent(self, name: str) -> "ParentNode | None":
        """
        Get a parent node by name.

        :param name:
            The parent node name to retrieve.

        :returns:
            The parent node if found, ``None`` otherwise.
        :rtype: ParentNode | None
        """
        return self.parents.get(name)

    def get_node(self, name: str) -> "Node | None":
        """
        Get any node by name.

        :param name:
            The node name to retrieve.

        :returns:
            The node if found, ``None`` otherwise.
        :rtype: Node | None
        """
        return self.nodes.get(name)

    def get_tag(self, name: str) -> "Tag | None":
        """
        Get a tag by name.

        :param name:
            The tag name to retrieve.

        :returns:
            The tag if found, ``None`` otherwise.
        :rtype: Tag | None
        """
        return self.tags.get(name)

    @overload
    def get_tagged(self) -> dict[str, list["ParentNode"]]: ...

    @overload
    def get_tagged(self, name: str) -> list["ParentNode"]: ...

    def get_tagged(
        self, name: str | None = None
    ) -> dict[str, list["ParentNode"]] | list["ParentNode"]:
        """
        Get tagged parent nodes, either all tags or a specific tag.

        :param name:
            The tag name to get parents for. If ``None``, returns all tags.

        :returns:
            If ``name`` is ``None``, returns a dictionary mapping tag names to
            lists of parent nodes. If ``name`` is provided, returns a list
            of parent nodes with that tag.
        :rtype: dict[str, list[ParentNode]] | list[ParentNode]
        """
        result: dict[str, list["ParentNode"]] = {}

        for parent in self.parents.values():
            for tag in parent.tags:
                if tag not in result:
                    result[tag] = []
                result[tag].append(parent)

        if name is None:
            return result

        return result.get(name, [])

    def get_values(self) -> dict[str, Any]:
        """
        Get the processed value of all source nodes.

        :returns:
            Dictionary mapping parent names to their processed values.
        :rtype: dict[str, Any]
        """
        return {name: parent.get_value() for name, parent in self.parents.items()}

    def get_provided_arguments(self) -> list["Argument"]:
        """
        Get all provided positional arguments.

        :returns:
            List of provided argument nodes.
        :rtype: list[Argument]
        """
        from click_extended.core.decorators.argument import Argument

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Argument) and parent.was_provided
        ]

    def get_provided_options(self) -> list["Option"]:
        """
        Get all provided keyword arguments.

        :returns:
            List of provided option nodes.
        :rtype: list[Option]
        """
        from click_extended.core.decorators.option import Option

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Option) and parent.was_provided
        ]

    def get_provided_envs(self) -> list["Env"]:
        """
        Get all provided environment variables.

        :returns:
            List of provided env nodes.
        :rtype: list[Env]
        """
        from click_extended.core.decorators.env import Env

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Env) and parent.was_provided
        ]

    def get_provided_value(self, name: str) -> Any:
        """
        Get the provided raw value of a parent node (before processing).

        :param name:
            The parent node name.

        :returns:
            The raw value if parent exists and was provided, ``None``
            otherwise.
        :rtype: Any
        """
        parent = self.get_parent(name)
        if parent is not None and parent.was_provided:
            return parent.raw_value  # type: ignore
        return None

    def get_provided_values(self) -> dict[str, Any]:
        """
        Get the provided raw values in the context (before processing).

        :returns:
            The provided raw values in the context.
        :rtype: dict[str, Any]
        """
        provided: dict[str, Any] = {}
        for name, parent in self.parents.items():
            if parent.was_provided:
                provided[name] = parent.raw_value
        return provided

    def get_missing_arguments(self) -> list["Argument"]:
        """
        Get all missing positional arguments.

        :returns:
            List of all argument nodes.
        :rtype: list[Argument]
        """
        from click_extended.core.decorators.argument import Argument

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Argument) and not parent.was_provided
        ]

    def get_missing_options(self) -> list["Option"]:
        """
        Get all missing keyword arguments.

        :returns:
            List of all option nodes.
        :rtype: list[Option]
        """
        from click_extended.core.decorators.option import Option

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Option) and not parent.was_provided
        ]

    def get_missing_envs(self) -> list["Env"]:
        """
        Get all missing environment variables.

        :returns:
            List of all env nodes.
        :rtype: list[Env]
        """
        from click_extended.core.decorators.env import Env

        return [
            parent
            for parent in self.parents.values()
            if isinstance(parent, Env) and not parent.was_provided
        ]

    def get_current_tags(self) -> list[str]:
        """
        Get a list of the tags of the current node.

        :returns:
            List of tag names for the current node.
        :rtype: list[str]
        """
        from click_extended.core.nodes.parent_node import ParentNode

        if isinstance(self.current, ParentNode):
            return list(self.current.tags)
        return []

    def get_current_parent_as_parent(self) -> "ParentNode":
        """
        Get the current parent node as a ``ParentNode``.

        :returns:
            The current parent node.
        :rtype: ParentNode

        :raises RuntimeError:
            If called outside child node context or the parent is a ``Tag``.
        """
        from click_extended.core.decorators.tag import Tag

        if self.parent is None:
            raise RuntimeError("No parent node in current context")
        if isinstance(self.parent, Tag):
            raise RuntimeError("Parent node is not a ParentNode instance.")
        return self.parent

    def get_current_parent_as_tag(self) -> "Tag":
        """
        Get the current parent node as a ``Tag``.

        :returns:
            The current parent node.
        :rtype: Tag

        :raises RuntimeError:
            If called outside child node context or
            the parent is a ``ParentNode``.
        """
        from click_extended.core.nodes.parent_node import ParentNode

        if self.parent is None:
            raise RuntimeError("No parent node in current context")
        if isinstance(self.parent, ParentNode):
            raise RuntimeError("Parent node is not a Tag instance.")
        return self.parent
