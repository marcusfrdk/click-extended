"""Exception raised when a parent node already exists with the same name."""

from click_extended.errors.click_extended_error import ClickExtendedError


class ParentNodeExistsError(ClickExtendedError):
    """Exception raised when a parent node already exists with the same name."""

    def __init__(self, name: str) -> None:
        """
        Initialize a new `ParentNodeExistsError` instance.

        Args:
            name (str):
                The name of the parent node.
        """
        message = f"A parent node already exists with the name '{name}'."
        super().__init__(message)
