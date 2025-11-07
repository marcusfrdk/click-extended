"""Raised when a child is used in a tagged environment without proper implementation."""

from click_extended.errors.click_extended_error import ClickExtendedError


class TaggedEnvironmentError(ClickExtendedError):
    """Raised when a child is used in a tagged environment without proper implementation."""
