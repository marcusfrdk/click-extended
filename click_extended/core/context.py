"""Context with a unified all contextual information across the context."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from click import Context as ClickContext

    from click_extended.core._root_node import RootNode
    from click_extended.core.argument import Argument
    from click_extended.core.child_node import ChildNode
    from click_extended.core.env import Env
    from click_extended.core.global_node import GlobalNode
    from click_extended.core.node import Node
    from click_extended.core.option import Option
    from click_extended.core.parent_node import ParentNode
    from click_extended.core.tag import Tag


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
@dataclass(frozen=True)
class Context:
    """
    Context with a unified all contextual information across the context.

    Attributes:
      root (RootNode):
        The root command node of the entire CLI tree.
      parent (ParentNode | Tag):
        The parent node (Option, Argument, Env, or Tag) that contains
        the current child.
      child (ChildNode):
        The current child node being processed.
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
      globals (dict[str, GlobalNode]):
        All global node instances.
      data (dict[str, Any]):
        Shared data store accessible across all nodes. Use this to pass
        custom data between global nodes and child nodes.
      debug (bool):
        Debug mode flag. When `True`, handler exceptions show full tracebacks.
        Set via `@debug()` decorator.
    """

    root: "RootNode"
    parent: "ParentNode | Tag | None"
    child: "ChildNode | None"
    click_context: "ClickContext"
    nodes: dict[str, "Node"]
    parents: dict[str, "ParentNode"]
    tags: dict[str, "Tag"]
    children: dict[str, "ChildNode"]
    globals: dict[str, "GlobalNode"]
    data: dict[str, Any]
    debug: bool = False

    def is_tag(self, name: str | None = None) -> bool:
        """
        Check if the parent node is a `Tag`, optionally with a specific name.

        Args:
          name (str | None, optional):
            Optional tag name to check for. If `None`, only checks
            if parent is a `Tag`.

        Returns:
          bool:
            `True` if parent is a `Tag`, `False` otherwise.

        Examples:
            ```python
            if context.is_tag():
                print("Parent is a tag")

            if context.is_tag("api_url"):
                print("Parent is the api_url tag")
            ```
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.tag import Tag

        if not isinstance(self.parent, Tag):
            return False

        if name is None:
            return True

        return self.parent.name == name

    def is_option(self) -> bool:
        """
        Check if the parent node is an `Option`.

        Returns:
            bool:
                `True` if parent is an `Option`, `False` otherwise.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.option import Option

        return isinstance(self.parent, Option)

    def is_argument(self) -> bool:
        """
        Check if the parent node is an `Argument`.

        Returns:
            bool:
                `True` if parent is an `Argument`, `False` otherwise.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.argument import Argument

        return isinstance(self.parent, Argument)

    def is_env(self) -> bool:
        """
        Check if the parent node is an `Env`.

        Returns:
            bool:
                `True` if parent is an `Env`, `False` otherwise.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.env import Env

        return isinstance(self.parent, Env)

    def get_parent(self, name: str) -> "ParentNode | None":
        """
        Get a parent node by name.

        Args:
            name (str):
                The parent node name to retrieve.

        Returns:
            ParentNode|None:
                The parent node if found, `None` otherwise.
        """
        return self.parents.get(name)

    def get_child(self, name: str) -> "ChildNode | None":
        """
        Get a child node by name.

        Args:
            name (str):
                The child node name to retrieve.

        Returns:
            ChildNode|None:
                The child node if found, `None` otherwise.
        """
        return self.children.get(name)

    def get_tag(self, name: str) -> "Tag | None":
        """
        Get a tag by name.

        Args:
            name (str):
                The tag name to retrieve.

        Returns:
            Tag|None:
                The tag if found, `None` otherwise.
        """
        return self.tags.get(name)

    def get_global(self, name: str) -> "GlobalNode | None":
        """
        Get a global node by name.

        Args:
            name (str):
                The global node name to retrieve.

        Returns:
            GlobalNode|None:
                The global node if found, `None` otherwise.
        """
        return self.globals.get(name)

    def get_node(self, name: str) -> "Node | None":
        """
        Get any node by name.

        Args:
            name (str):
                The node name to retrieve.

        Returns:
            Node|None:
                The node if found, `None` otherwise.
        """
        return self.nodes.get(name)

    def has_parent(self, name: str) -> bool:
        """
        Check if a parent node with the given name exists.

        Args:
            name (str):
                The parent node name to check.

        Returns:
            bool:
                `True` if the parent exists, `False` otherwise.
        """
        return name in self.parents

    def is_provided(self, name: str) -> bool:
        """
        Check if a parent node was provided by the user.

        Args:
            name (str):
                The parent node name to check.

        Returns:
            bool:
                `True` if the parent exists and was provided, `False` otherwise.
        """
        parent = self.get_parent(name)
        return parent is not None and parent.was_provided()

    def get_missing(self, names: list[str]) -> list[str]:
        """
        Get list of parent names that were NOT provided.

        Args:
            names (list[str]):
                List of parent names to check.

        Returns:
            list[str]:
                List of names that were not provided by the user.

        Examples:
            ```python
            if (missing := context.get_missing(["username", "password"])):
                raise ValueError(f"Missing required parameters: {missing}")
            ```
        """
        return [name for name in names if not self.is_provided(name)]

    def count_provided(self, tag: str | None = None) -> int:
        """
        Count how many parent nodes were provided.

        Args:
            tag (str | None, optional):
                Optional tag name to filter by. If `None`, counts all parents.

        Returns:
            int:
                Number of provided parent nodes.

        Examples:
            ```python
            # At least one auth method required
            if context.count_provided(tag="auth") < 1:
                raise ValueError("At least one auth method required")

            # Exactly one payment method
            if context.count_provided(tag="payment") != 1:
                raise ValueError("Exactly one payment method required")
            ```
        """
        if tag is None:
            return sum(1 for p in self.parents.values() if p.was_provided())

        return sum(
            1
            for p in self.parents.values()
            if tag in p.tags and p.was_provided()
        )

    def get_raw_values(self) -> dict[str, Any]:
        """
        Get all parent node values as a dictionary.

        Returns:
            dict[str, Any]:
                Dictionary mapping parent names to their values
                (including `None` values).

        Examples:
            ```python
            values = context.get_raw_values()
            # {"username": "alice", "password": "secret", "api_key": None}
            ```
        """
        return {
            name: parent.get_value() for name, parent in self.parents.items()
        }

    def get_provided_parents(
        self, tag: str | None = None
    ) -> dict[str, "ParentNode"]:
        """
        Get only provided parent nodes as a dictionary.

        Args:
            tag (str | None, optional):
                Optional tag name to filter by. If `None`,
                returns all provided parents.

        Returns:
            dict[str, ParentNode]:
                Dictionary mapping parent names to `ParentNode` instances
                (only provided).

        Examples:
            ```python
            # All provided params
            provided = context.get_provided_parents()

            # Only provided auth params
            auth_provided = context.get_provided_parents(tag="auth")
            if len(auth_provided) > 1:
                raise ValueError("Only one auth method allowed")
            ```
        """
        if tag is None:
            return {
                name: parent
                for name, parent in self.parents.items()
                if parent.was_provided()
            }

        return {
            name: parent
            for name, parent in self.parents.items()
            if tag in parent.tags and parent.was_provided()
        }

    def get_provided_keys(self, tag: str | None = None) -> list[str]:
        """
        Get list of provided parent names.

        Args:
            tag (str | None, optional):
                Optional tag name to filter by. If `None`,
                returns all provided names.

        Returns:
            list[str]:
                List of parent names that were provided.

        Examples:
            ```python
            provided_names = context.get_provided_keys(tag="auth")
            # ["username", "password"]
            ```
        """
        return list(self.get_provided_parents(tag=tag).keys())

    def get_provided_values(self, tag: str | None = None) -> dict[str, Any]:
        """
        Get values of provided parent nodes as a dictionary.

        Args:
            tag (str | None, optional):
                Optional tag name to filter by. If `None`,
                returns all provided values.

        Returns:
            dict[str, Any]:
                Dictionary mapping parent names to their values (only provided).

        Examples:
            ```python
            # All provided values
            values = context.get_provided_values()
            # {"username": "alice", "password": "secret"}

            # Only auth values
            auth_values = context.get_provided_values(tag="auth")
            ```
        """
        return {
            name: parent.get_value()
            for name, parent in self.get_provided_parents(tag=tag).items()
        }

    def get_tagged(self, tag: str) -> dict[str, "ParentNode"]:
        """
        Get all parent nodes with a specific tag (not just provided).

        Args:
            tag (str):
                Tag name to filter by.

        Returns:
            dict[str, ParentNode]:
                Dictionary mapping parent names to `ParentNode` instances.

        Examples:
            ```python
            # All auth-tagged parameters (provided or not)
            auth_params = context.get_tagged("auth")
            # {"username": <Option>, "password": <Option>, "api_key": <Option>}
            ```
        """
        return {
            name: parent
            for name, parent in self.parents.items()
            if tag in parent.tags
        }

    def get_options(self) -> dict[str, "Option"]:
        """
        Get all `Option` nodes as a dictionary.

        Returns:
            dict[str, Option]:
                Dictionary mapping option names to `Option` instances.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.option import Option

        return {
            name: parent
            for name, parent in self.parents.items()
            if isinstance(parent, Option)
        }

    def get_arguments(self) -> dict[str, "Argument"]:
        """
        Get all `Argument` nodes as a dictionary.

        Returns:
            dict[str, Argument]:
                Dictionary mapping argument names to `Argument` instances.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.argument import Argument

        return {
            name: parent
            for name, parent in self.parents.items()
            if isinstance(parent, Argument)
        }

    def get_envs(self) -> dict[str, "Env"]:
        """
        Get all `Env` nodes as a dictionary.

        Returns:
            dict[str, Env]:
                Dictionary mapping env names to `Env` instances.
        """
        # pylint: disable=import-outside-toplevel
        from click_extended.core.env import Env

        return {
            name: parent
            for name, parent in self.parents.items()
            if isinstance(parent, Env)
        }

    def with_child(self, child: "ChildNode") -> "Context":
        """
        Create a new `Context` with a different child node.

        This is useful when you need to process a child recursively
        or delegate to another child's handlers.

        Args:
            child (ChildNode):
                The new child node.

        Returns:
            Context:
                A new `Context` instance with the updated child.
        """
        return Context(
            root=self.root,
            parent=self.parent,
            child=child,
            click_context=self.click_context,
            nodes=self.nodes,
            parents=self.parents,
            tags=self.tags,
            children=self.children,
            globals=self.globals,
            data=self.data,
            debug=self.debug,
        )

    def with_parent(self, parent: "ParentNode | Tag") -> "Context":
        """
        Create a new `Context` with a different parent node.

        This is useful in advanced scenarios where you need to process
        a value in the context of a different parent.

        Args:
            parent (ParentNode | Tag):
                The new parent node (`ParentNode` or `Tag`).

        Returns:
            Context:
                A new `Context` instance with the updated parent.
        """
        return Context(
            root=self.root,
            parent=parent,
            child=self.child,
            click_context=self.click_context,
            nodes=self.nodes,
            parents=self.parents,
            tags=self.tags,
            children=self.children,
            globals=self.globals,
            data=self.data,
            debug=self.debug,
        )
