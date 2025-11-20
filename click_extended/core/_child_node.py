"""The node used as a child node.."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-return-statements
# pylint: disable=too-few-public-methods
# pylint: disable=broad-exception-caught

from abc import ABC, abstractmethod
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ParamSpec,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from click_extended.core._node import Node
from click_extended.core._tree import queue_child
from click_extended.errors import TypeMismatchError, ValidationError
from click_extended.utils.transform import Transform

if TYPE_CHECKING:
    from click_extended.core._parent_node import ParentNode
    from click_extended.core.tag import Tag
    from click_extended.types import Decorator

P = ParamSpec("P")
T = TypeVar("T")


class ProcessContext:
    """
    Context provided to `ChildNode.process()` containing
    all processing information.
    """

    def __init__(
        self,
        parent: "ParentNode | Tag",
        siblings: list[str],
        tags: dict[str, "Tag"],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize a new ProcessContext instance.

        Args:
            parent (ParentNode | Tag):
                The parent node (ParentNode or Tag) this child is
                attached to.
            siblings (list[str]):
                List of unique class names of all sibling child nodes.
            tags (dict[str, Tag]):
                Dictionary mapping tag names to Tag instances.
            args (tuple[Any, ...]):
                Additional positional arguments from `as_decorator`.
            kwargs (dict[str, Any]):
                Additional keyword arguments from `as_decorator`.
        """
        self.parent = parent
        self.siblings = siblings
        self.tags = tags
        self.args = args
        self.kwargs = kwargs

    def is_tag(self) -> bool:
        """Check if parent is a Tag."""
        return self.parent.__class__.__name__ == "Tag"

    def is_option(self) -> bool:
        """Check if parent is an Option."""
        return self.parent.__class__.__name__ == "Option"

    def is_argument(self) -> bool:
        """Check if parent is an Argument."""
        return self.parent.__class__.__name__ == "Argument"

    def is_env(self) -> bool:
        """Check if parent is an Env."""
        return self.parent.__class__.__name__ == "Env"

    def get_tag_values(self) -> dict[str, Any]:
        """
        Get all values from tag's parent nodes.

        Returns:
            dict[str, Any]:
                Dictionary mapping parent node names to their values.

        Raises:
            ValueError:
                If parent is not a Tag.
        """
        if not self.is_tag():
            raise ValueError("Parent is not a Tag")
        tag = cast("Tag", self.parent)
        return {pn.name: pn.get_value() for pn in tag.parent_nodes}


class ChildNode(Node, ABC):
    """The node used as a child node."""

    parent: "ParentNode"

    def __init__(
        self,
        name: str,
        process_args: tuple[Any, ...] | None = None,
        process_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a new `ChildNode` instance.

        Args:
            name (str):
                The name of the node.
            process_args (tuple):
                Positional arguments to pass to the process method.
            process_kwargs (dict[str, Any]):
                Keyword arguments to pass to the process method.
        """
        super().__init__(name=name, children=None)
        self.children = None
        self.process_args = process_args or ()
        self.process_kwargs = process_kwargs or {}

    def get_supported_types(self) -> list[type]:
        """
        Get supported types from the `process()` method's value type hint.

        Returns:
            list[type]:
                List of supported types. Empty list means all types
                accepted.
        """
        try:
            hints = get_type_hints(self.process)
            if "value" not in hints:
                return []

            value_hint = hints["value"]

            if value_hint is Any:
                return []

            origin = get_origin(value_hint)

            if origin is Union or isinstance(value_hint, UnionType):
                return [t for t in get_args(value_hint) if t is not type(None)]

            args = get_args(value_hint)
            if args:
                return [t for t in args if t is not type(None)]

            if value_hint is not type(None):
                return [value_hint]

            return []
        except Exception:
            return []

    def should_skip_none(self) -> bool:
        """
        Determine if `None` values should be skipped based on type
        hints.

        Returns:
            bool:
                `True` if `None` is not in the value type hint,
                `False` otherwise. Returns `False` for `Any` type
                (accepts everything including None).
        """
        try:
            hints = get_type_hints(self.process)
            if "value" not in hints:
                return True

            value_hint = hints["value"]

            if value_hint is Any:
                return False

            origin = get_origin(value_hint)

            if origin is Union or isinstance(value_hint, UnionType):
                args = get_args(value_hint)
                return type(None) not in args

            return value_hint is not type(None)
        except Exception:
            return True

    def _matches_single_value(self, member: type, parent_type: type) -> bool:
        """Check if union member matches single value structure."""
        member_origin = get_origin(member)
        return member_origin is not tuple and member == parent_type

    def _matches_flat_tuple(self, member: type, parent_type: type) -> bool:
        """Check if union member matches flat tuple structure."""
        member_origin = get_origin(member)
        member_args = get_args(member)

        if member_origin is not tuple or not member_args:
            return False

        inner_types = [
            t for t in member_args if t is not type(...) and t != Ellipsis
        ]

        if not inner_types or any(get_origin(t) is tuple for t in inner_types):
            return False

        expanded_inner = self._expand_union_types(inner_types)

        return parent_type in expanded_inner

    def _matches_nested_tuple(self, member: type, parent_type: type) -> bool:
        """Check if union member matches nested tuple structure."""
        member_origin = get_origin(member)
        member_args = get_args(member)

        if member_origin is not tuple or not member_args:
            return False

        inner_types = [
            t for t in member_args if t is not type(...) and t != Ellipsis
        ]

        for inner_type in inner_types:
            inner_origin = get_origin(inner_type)
            if inner_origin is not tuple:
                continue

            inner_args = get_args(inner_type)
            if not inner_args:
                continue

            innermost = [
                t for t in inner_args if t is not type(...) and t != Ellipsis
            ]

            if not innermost or any(get_origin(t) is tuple for t in innermost):
                continue

            expanded = self._expand_union_types(innermost)

            if parent_type in expanded:
                return True

        return False

    def _expand_union_types(self, types: list[type]) -> list[type]:
        """Expand union types in a list of types."""
        expanded = []
        for t in types:
            t_origin = get_origin(t)
            if t_origin is Union or isinstance(t, UnionType):
                expanded.extend(
                    [arg for arg in get_args(t) if arg is not type(None)]
                )
            else:
                expanded.append(t)
        return expanded

    def _collect_relevant_types(
        self,
        value_hint: Any,
        parent_nargs: int,
        parent_multiple: bool,
    ) -> list[type]:
        """Collect types relevant to the current structure."""
        relevant_types = []
        union_members = [t for t in get_args(value_hint) if t is not type(None)]

        for member in union_members:
            member_origin = get_origin(member)
            member_args = get_args(member)

            # Single value case
            if not parent_multiple and parent_nargs == 1:
                if member_origin is not tuple:
                    relevant_types.append(member)

            # Flat tuple case
            elif not parent_multiple and (
                parent_nargs > 1 or parent_nargs == -1
            ):
                if member_origin is tuple and member_args:
                    inner_types = [
                        t
                        for t in member_args
                        if t is not type(...) and t != Ellipsis
                    ]
                    if inner_types and all(
                        get_origin(t) is not tuple for t in inner_types
                    ):
                        relevant_types.extend(
                            self._expand_union_types(inner_types)
                        )

            # Nested tuple case
            elif parent_multiple:
                if member_origin is tuple and member_args:
                    inner_types = [
                        t
                        for t in member_args
                        if t is not type(...) and t != Ellipsis
                    ]
                    for inner_type in inner_types:
                        inner_origin = get_origin(inner_type)
                        if inner_origin is tuple:
                            inner_args = get_args(inner_type)
                            if inner_args:
                                innermost = [
                                    t
                                    for t in inner_args
                                    if t is not type(...) and t != Ellipsis
                                ]
                                if innermost and all(
                                    get_origin(t) is not tuple
                                    for t in innermost
                                ):
                                    relevant_types.extend(
                                        self._expand_union_types(innermost)
                                    )

        seen = set()
        unique_types = []
        for t in relevant_types:
            if t not in seen:
                seen.add(t)
                unique_types.append(t)

        return unique_types

    def validate_type(self, parent: "ParentNode") -> None:
        """
        Validate that the parent's type is supported by this child
        node.

        Uses type hints from the `process()` method to determine
        supported types. Empty list means all types are supported.

        - Case 1: nargs=1, multiple=False → value: T (single value)
        - Case 2: nargs>1, multiple=False → value: tuple[T, ...]
                  (flat tuple)
        - Case 3: multiple=True → value: tuple[tuple[T, ...], ...]
                  (ALWAYS nested)

        Args:
            parent (ParentNode):
                The parent node to validate against.

        Raises:
            TypeMismatchError:
                If the parent's type is not supported by this child
                node.
            ValidationError:
                If the child's type hint doesn't match the parent's
                value structure.
        """
        supported_types = self.get_supported_types()

        if not supported_types:
            return

        parent_type = getattr(parent, "type", None)
        parent_nargs = getattr(parent, "nargs", 1)
        parent_multiple = getattr(parent, "multiple", False)

        if parent_type is None:
            return

        try:
            hints = get_type_hints(self.process)
            if "value" not in hints:
                return

            value_hint = hints["value"]
            origin = get_origin(value_hint)
            args = get_args(value_hint)

            valid_member_found = False
            is_union_type = origin is Union or isinstance(value_hint, UnionType)

            if is_union_type:
                union_members = [
                    t for t in get_args(value_hint) if t is not type(None)
                ]

                for member in union_members:
                    try:
                        if not parent_multiple and parent_nargs == 1:
                            if self._matches_single_value(member, parent_type):
                                valid_member_found = True
                                break
                        elif not parent_multiple and (
                            parent_nargs > 1 or parent_nargs == -1
                        ):
                            if self._matches_flat_tuple(member, parent_type):
                                valid_member_found = True
                                break
                        elif parent_multiple:
                            if self._matches_nested_tuple(member, parent_type):
                                valid_member_found = True
                                break
                    except Exception:
                        continue

                if valid_member_found:
                    return

        except Exception:
            return

        if is_union_type and not valid_member_found:
            relevant_types = self._collect_relevant_types(
                value_hint, parent_nargs, parent_multiple
            )

            raise TypeMismatchError(
                name=self.name,
                parent_name=parent.name,
                parent_type=parent_type,
                supported_types=(
                    relevant_types if relevant_types else supported_types
                ),
            )

        # Singlular value or tuple value
        if not parent_multiple:
            if parent_nargs == 1:
                if origin is tuple:
                    raise ValidationError(
                        f"Type mismatch for '{self.name}' attached to "
                        f"'{parent.name}': parent has nargs=1 and "
                        f"multiple=False, which produces a single "
                        f"value, but process() expects tuple type. "
                        f"Use 'value: {parent_type.__name__}' instead."
                    )

                if parent_type not in supported_types:
                    raise TypeMismatchError(
                        name=self.name,
                        parent_name=parent.name,
                        parent_type=parent_type,
                        supported_types=supported_types,
                    )
            else:
                if origin is not tuple:
                    raise ValidationError(
                        f"Type mismatch for '{self.name}' attached to "
                        f"'{parent.name}': parent has nargs={parent_nargs} "
                        f"and multiple=False, which produces a flat "
                        f"tuple, but process() expects non-tuple type. "
                        f"Use 'value: tuple[{parent_type.__name__}, "
                        f"...]' instead."
                    )

                if args:
                    inner_types = [
                        t for t in args if t is not type(...) and t != Ellipsis
                    ]
                    if inner_types:
                        for inner_type in inner_types:
                            if get_origin(inner_type) is tuple:
                                raise ValidationError(
                                    f"Type mismatch for '{self.name}' "
                                    f"attached to '{parent.name}': parent "
                                    f"has nargs={parent_nargs} and "
                                    f"multiple=False, which produces a flat "
                                    f"tuple, but process() expects nested "
                                    f"tuple type. Use 'value: "
                                    f"tuple[{parent_type.__name__}]' instead."
                                )

                        expanded_types = []
                        for inner_type in inner_types:
                            inner_origin = get_origin(inner_type)
                            if inner_origin is Union or isinstance(
                                inner_type, UnionType
                            ):
                                union_args = get_args(inner_type)
                                expanded_types.extend(
                                    [
                                        t
                                        for t in union_args
                                        if t is not type(None)
                                    ]
                                )
                            else:
                                expanded_types.append(inner_type)

                        if expanded_types and parent_type not in expanded_types:
                            raise TypeMismatchError(
                                name=self.name,
                                parent_name=parent.name,
                                parent_type=parent_type,
                                supported_types=expanded_types,
                            )

        # Nested tuple
        elif parent_multiple:
            if origin is not tuple:
                raise ValidationError(
                    f"Type mismatch for '{self.name}' attached to "
                    f"'{parent.name}': parent has multiple=True, which "
                    f"ALWAYS produces a nested tuple, but process() "
                    f"expects non-tuple type. Use 'value: "
                    f"tuple[tuple[{parent_type.__name__}]]' instead."
                )

            if args:
                inner_types = [
                    t for t in args if t is not type(...) and t != Ellipsis
                ]
                if not inner_types:
                    return

                found_nested = False
                for inner_type in inner_types:
                    inner_origin = get_origin(inner_type)
                    if inner_origin is tuple:
                        found_nested = True
                        inner_args = get_args(inner_type)
                        if inner_args:
                            innermost_types = [
                                t
                                for t in inner_args
                                if t is not type(...) and t != Ellipsis
                            ]

                            expanded_types = []
                            for itype in innermost_types:
                                itype_origin = get_origin(itype)
                                if itype_origin is Union or isinstance(
                                    itype, UnionType
                                ):
                                    union_args = get_args(itype)
                                    expanded_types.extend(
                                        [
                                            t
                                            for t in union_args
                                            if t is not type(None)
                                        ]
                                    )
                                else:
                                    expanded_types.append(itype)

                            if (
                                expanded_types
                                and parent_type not in expanded_types
                            ):
                                raise TypeMismatchError(
                                    name=self.name,
                                    parent_name=parent.name,
                                    parent_type=parent_type,
                                    supported_types=expanded_types,
                                )
                        break

                if not found_nested:
                    raise ValidationError(
                        f"Type mismatch for '{self.name}' attached to "
                        f"'{parent.name}': parent has multiple=True, "
                        f"which ALWAYS produces a nested tuple, but "
                        f"process() expects flat tuple type. Use "
                        f"'value: tuple[tuple[{parent_type.__name__}, "
                        f"...], ...]' instead."
                    )

    def get(self, name: str) -> None:
        """
        The `ChildNode` has no children, thus this method
        returns `None`.

        Args:
            name (str):
                The name of the child.

        Returns:
            None:
                Always returns `None` as the `ChildNode` has no children.
        """
        return None

    def __getitem__(self, name: str | int) -> Node:
        raise KeyError("A ChildNode instance has no children.")

    @classmethod
    def as_decorator(cls, *args: Any, **kwargs: Any) -> "Decorator":
        """
        Return a decorator representation of the child node.

        The provided args and kwargs are stored and later passed to the
        process method when called by the `ParentNode`.

        Args:
            *args (Any):
                Positional arguments to pass to the process method.
            **kwargs (Any):
                Keyword arguments to pass to the process method.

        Returns:
            Callable:
                A decorator function that registers the child node.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The actual decorator that wraps the function."""
            name = Transform(cls.__name__).to_snake_case()
            instance = cls(name=name, process_args=args, process_kwargs=kwargs)
            queue_child(instance)
            return func

        return decorator

    @abstractmethod
    def process(self, value: Any, context: ProcessContext) -> Any:
        """
        Process the value and return the processed result.

        Args:
            value (Any):
                The value to process (from previous child or parent).
                Subclasses can override the type annotation for
                value.
            context (ProcessContext):
                Context containing parent, siblings, tags, and
                decorator args.

        Returns:
            Any:
                The processed value, or None to leave the value
                unchanged.
        """
        raise NotImplementedError


__all__ = ["ChildNode", "ProcessContext"]
