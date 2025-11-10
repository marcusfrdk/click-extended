"""Exception raised when there is no `RootNode` defined."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NoRootError(ClickExtendedError):
    """Exception raised when there is no `RootNode` defined."""

    def __init__(self) -> None:
        """Initialize a new `NoRootError` instance."""
        message = "There is no root node defined in the tree."
        super().__init__(message)
