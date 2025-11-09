"""Base exception for all custom click-extended errors."""

import click


class ClickExtendedError(click.ClickException):
    """Base exception for all custom click-extended errors."""

    def __init__(self, message: str) -> None:
        """
        Initialize a new `ClickExtendedError` instance.

        Args:
            message (str):
                The message to show.
        """
        super().__init__(message)
