"""Exceptions used in the `click_extended` library."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments


class ClickExtendedError(Exception):
    """Base exception for exceptions defined in the `click_extended` library."""

    def __init__(self, message: str) -> None:
        """
        Initialize a new `ClickExtendedError` instance.

        Args:
            message (str):
                The message to show.
        """
        super().__init__(message)


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
