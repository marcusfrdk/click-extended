"""Exceptions used in the `click_extended` library."""


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
