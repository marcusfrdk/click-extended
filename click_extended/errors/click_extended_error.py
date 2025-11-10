"""Base exception for exceptions defined in the `click_extended` library."""


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
