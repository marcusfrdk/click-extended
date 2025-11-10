"""Exception raised when a root node already exists for the tree."""

from click_extended.errors.click_extended_error import ClickExtendedError


class RootNodeExistsError(ClickExtendedError):
    """Exception raised when a root node already exists for the tree."""

    def __init__(self) -> None:
        """Initialize a new `RootNodeExistsError` instance."""
        message = "A root node is already defined."
        super().__init__(message)
