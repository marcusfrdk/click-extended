"""Exceptions used in the `click_extended` library."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import inspect
from typing import IO, Any

import click
from click import ClickException
from click._compat import get_text_stderr
from click.utils import echo

from click_extended.utils.format import format_list


class ClickExtendedError(Exception):
    """Base exception for exceptions defined in the `click_extended` library."""


# Catchable errors
class CatchableError(ClickExtendedError):
    """Base exception for exceptions raised inside a child node.

    These exceptions are caught by the framework and reformatted with
    parameter context before being displayed to the user.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize a CatchableError.

        Args:
            message: The error message describing what went wrong.
        """
        super().__init__(message)


class ChildNodeProcessError(CatchableError):
    """
    Base class for exceptions which must be raised inside
    the `process()` method of a `ChildNode`.
    """

    def __init__(self, message: str, **kwargs: str) -> None:
        """
        Initialize a new `ChildNodeProcessError` instance.

        Args:
            message (str):
                The error message. If child_name is found, it will be
                prefixed automatically. Subclasses can access child_name
                via self.child_name to format custom messages.

        Raises:
            RuntimeError:
                If raised outside a ChildNode context.
        """
        self.child_name: str | None = None
        frame = inspect.currentframe()

        if frame:
            current_frame = frame.f_back
            depth = 0
            max_depth = 10

            while current_frame and depth < max_depth:
                caller_locals = current_frame.f_locals
                if "self" in caller_locals:
                    self_obj = caller_locals["self"]
                    if hasattr(self_obj, "name") and hasattr(
                        self_obj, "process"
                    ):
                        self.child_name = self_obj.name
                        break
                current_frame = current_frame.f_back
                depth += 1

        if not self.child_name:
            raise RuntimeError(
                f"{self.__class__.__name__} must be raised from within a "
                f"ChildNode.process() method. The exception was raised outside "
                f"a valid ChildNode context."
            )

        formatted_message = message.format(name=self.child_name, **kwargs)
        super().__init__(formatted_message)


class UnhandledValueError(ChildNodeProcessError):
    """Exception raised when a value in the `process()` method is unexpected."""

    def __init__(self, value: Any) -> None:
        """
        Initialize a new `UnhandledValueError` instance.

        Args:
            value (Any):
                The unexpected value.
        """
        message = "Received unexpected value for '{name}' of type '{type}'"
        super().__init__(message, type=type(value).__name__)


class ValidationError(CatchableError):
    """Exception raised when validation fails in a child node."""


class TransformError(CatchableError):
    """Exception raised when transformation fails in a child node."""


class UnknownError(ChildNodeProcessError):
    """
    Exception raised when an unexpected error occurs or parts of code
    which is unhandled.
    """


class ParameterError(ClickException):
    """Exception raised when parameter validation or transformation fails.

    This exception is raised by the framework after catching a CatchableError
    and adding parameter context information.
    """

    exit_code = 2

    def __init__(
        self,
        message: str,
        param_hint: str | None = None,
        ctx: click.Context | None = None,
    ) -> None:
        """
        Initialize a ParameterError.

        Args:
            message (str):
                The error message from the validator/transformer.
            param_hint (str, optional):
                The parameter name (e.g., '--config', 'PATH').
            ctx (click.Context, optional):
                The Click context for displaying usage information.
        """
        super().__init__(message)
        self.param_hint = param_hint
        self.ctx = ctx

    def format_message(self) -> str:
        """Format the error message with parameter context."""
        if self.param_hint:
            return f"({self.param_hint}): {self.message}"
        return self.message

    def show(self, file: IO[Any] | None = None) -> None:
        """Display the error with usage information (like Click does)."""
        if file is None:
            file = get_text_stderr()

        color = None

        if self.ctx is not None:
            color = self.ctx.color

            echo(self.ctx.get_usage(), file=file, color=color)

            if self.ctx.command.get_help_option(self.ctx) is not None:
                hint = (
                    f"Try '{self.ctx.command_path} "
                    f"{self.ctx.help_option_names[0]}' for help."
                )
                echo(hint, file=file, color=color)

            echo("", file=file)

        echo(f"Error {self.format_message()}", file=file, color=color)


# Node errors
class NoParentError(ClickExtendedError):
    """Exception raised when no `ParentNode` has been defined."""

    def __init__(self, name: str) -> None:
        """
        Initialize a new `NoParentError` instance.

        Args:
            name (str):
                The name of the child node.
        """

        message = (
            f"Failed to register the child node '{name}' as no parent is "
            "defined. Ensure a parent node is registered before registering a "
            "child node."
        )
        super().__init__(message)


class NoRootError(ClickExtendedError):
    """Exception raised when there is no `RootNode` defined."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize a new `NoRootError` instance."""
        super().__init__(message or "No root node is defined in the tree.")


class ParentNodeExistsError(ClickExtendedError):
    """Exception raised when a parent node already exists with the same name."""

    def __init__(self, name: str) -> None:
        """
        Initialize a new `ParentNodeExistsError` instance.

        Args:
            name (str):
                The name of the parent node.
        """
        message = (
            f"Cannot register parent node '{name}' as a parent node with this "
            "name already exists. "
            f"Parent node names must be unique within the tree."
        )
        super().__init__(message)


class RootNodeExistsError(ClickExtendedError):
    """Exception raised when a root node already exists for the tree."""

    def __init__(self) -> None:
        """Initialize a new `RootNodeExistsError` instance."""
        message = (
            "Cannot register root node as a root node has already been "
            "defined. Only one root node is allowed per tree instance."
        )
        super().__init__(message)


class InvalidChildOnTagError(ClickExtendedError):
    """Exception raised when a transformation child is attached to a tag."""

    def __init__(self, child_name: str, tag_name: str) -> None:
        """
        Initialize a new `InvalidChildOnTagError` instance.

        Args:
            child_name (str):
                The name of the child node.
            tag_name (str):
                The name of the tag.
        """
        message = (
            f"Cannot attach transformation child '{child_name}' to tag "
            f"'{tag_name}'. Tags can only have validation-only children "
            "(no return statement or return None)."
        )
        super().__init__(message)


class DuplicateNameError(ClickExtendedError):
    """Exception raised when a name collision is detected."""

    def __init__(
        self, name: str, type1: str, type2: str, location1: str, location2: str
    ) -> None:
        """
        Initialize a new `DuplicateNameError` instance.

        Args:
            name (str):
                The conflicting name.
            type1 (str):
                The type of the first node (e.g., "option", "tag").
            type2 (str):
                The type of the second node.
            location1 (str):
                Description of where the first node is defined.
            location2 (str):
                Description of where the second node is defined.
        """
        message = (
            f"The name '{name}' is used by both "
            f"{type1} {location1} and {type2} {location2}. "
            f"All names (options, arguments, environment variables, and tags) "
            f"must be unique within a command."
        )
        super().__init__(message)


class TypeMismatchError(ClickExtendedError):
    """Exception raised when a child node doesn't support the parent's type."""

    def __init__(
        self,
        name: str,
        parent_name: str,
        parent_type: type | None,
        supported_types: list[type],
    ) -> None:
        """
        Initialize a new `TypeMismatchError` instance.

        Args:
            name (str):
                The name of the decorator.
            parent_name (str):
                The name of the parent node.
            parent_type (type | None):
                The actual type of the parent.
            supported_types (list[type]):
                List of types supported by the child node.
        """

        def get_type_name(type_obj: type) -> str:
            """Get type name, handling both regular types and UnionType."""
            return getattr(type_obj, "__name__", str(type_obj))

        parent_type_name = get_type_name(parent_type) if parent_type else "None"

        type_names = [get_type_name(t) for t in supported_types]
        formatted_types = format_list(
            type_names,
            prefix_singular="Supported type is ",
            prefix_plural="Supported types are ",
            wrap=("<", ">"),
        )

        message = (
            f"Decorator '{name}' does not support "
            f"parent '{parent_name}' with type '{parent_type_name}'. "
            f"{formatted_types}"
        )
        super().__init__(message)
