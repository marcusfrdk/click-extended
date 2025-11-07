"""Representation of a failure."""

from typing import Any


class Failure:
    """Representation of a failure during execution."""

    def __init__(
        self, value: Any, message: str, parent_name: str | None = None
    ) -> None:
        """Initialize a new Failure instance."""
        self.value = value
        self.message = message
        self.parent_name = parent_name

    def __str__(self) -> str:
        """Format the failure message."""
        suffix = f" ({self.parent_name})" if self.parent_name else ""
        return f"{self.message}{suffix}"
