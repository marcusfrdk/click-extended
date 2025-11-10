"""Exception raised when no `ParentNode` has been defined."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NoParentError(ClickExtendedError):
    """Exception raised when no `ParentNode` has been defined."""

    def __init__(self) -> None:
        """Initialize a new `NoParentError` instance."""
        message = "There is no parent node defined in the tree."
        super().__init__(message)
