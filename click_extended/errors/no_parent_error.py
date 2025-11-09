"""Exception for when a parent node is not found."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NoParentError(ClickExtendedError):
    """Exception for when a parent node does not exists."""

    def __init__(self, child_name: str):
        """
        Initialize a new `ParentNotFoundError`.

        Args:
            child_name (str):
                The name of the child.
        """
        msg = (
            f"Could not add child '{child_name}', no parents exist in context."
        )
        super().__init__(msg)
