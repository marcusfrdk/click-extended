"""Abstract class representing a parent node."""

from abc import ABC
from typing import Any

from click_extended.core._child import Child
from click_extended.core._context import Context
from click_extended.core._main import Main
from click_extended.errors import NoMainNodeError


class Parent(ABC):  # noqa: B024
    """
    Abstract class representing a parent node (Option/Argument/Env/Tag).

    Parent nodes register with Main, collect children, and orchestrate
    child execution. They do not execute logic themselves.
    """

    def __init__(self, name: str | None = None, tags: list[str] | None = None) -> None:
        """Initialize a new Parent instance."""
        self.name = name
        self.tags = tags or []
        self.children: list[Any] = []
        self.value: Any = None
        self.pending_func: Any = None
        self.wrapped_parent: Parent | None = None  # Track parent-to-parent chains

    def add_child(self, child: Any) -> None:
        """Register a child node with this parent."""
        self.children.append(child)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handle decorator chaining or raise error if called as
        function without Main.

        Validates that parent is being applied to a Main
        node, Child, or function.
        """

        if len(args) == 0 or len(args) > 1 or kwargs:
            raise NoMainNodeError(
                "Parent decorators (option, argument, env, tag) require a main node "
                "(command or group) to be defined. Cannot execute without a main node."
            )

        target = args[0]

        if isinstance(target, Child):
            self.add_child(target)
            if hasattr(target, "wrapped_parent") and target.wrapped_parent:
                self.wrapped_parent = target.wrapped_parent
                if hasattr(target.wrapped_parent, "pending_func"):
                    self.pending_func = target.wrapped_parent.pending_func
            elif hasattr(target, "pending_func"):
                self.pending_func = target.pending_func
            return self

        if isinstance(target, Parent):
            self.wrapped_parent = target
            if hasattr(target, "pending_func"):
                self.pending_func = target.pending_func
            return self

        if isinstance(target, Main):
            return self

        if callable(target):
            self.pending_func = target
            return self

        raise NoMainNodeError(
            "Parent decorators (option, argument, env, tag) require a main node "
            "(command or group) to be defined. Cannot execute without a main node."
        )

    def execute(self, ctx: Context) -> None:
        """Execute all children with the current context."""
        parent_info = {
            "name": self.name,
            "tags": self.tags,
            "value": self.value,
        }
        ctx.parents.append(parent_info)

        for child in self.children:
            is_tagged = len(self.tags) > 0 or self.__class__.__name__ == "Tag"

            if is_tagged:
                values = {self.name: self.value} if self.name else {}
                child.before_multiple(values, ctx)
                child.after_multiple(values, ctx)
            else:
                child.before_single(self.value, ctx)
                result = child.after_single(self.value, ctx)
                self.value = result
