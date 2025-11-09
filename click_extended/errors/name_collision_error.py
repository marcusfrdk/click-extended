"""Exception for when a parent node is not found."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NameCollisionError(ClickExtendedError):
    """Exception for when the name of two or more parents collide."""

    def __init__(self, name: str):
        """
        Initialize a new `NameCollisionError`.

        Args:
            name (str):
                The name that collides.
        """
        msg = f"Found multiple parents with the name '{name}'."
        super().__init__(msg)
