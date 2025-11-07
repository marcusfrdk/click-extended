"""Raised when a decorator is used incorrectly."""

from click_extended.errors.click_extended_error import ClickExtendedError


class UsageError(ClickExtendedError):
    """Raised when a decorator is used incorrectly."""
