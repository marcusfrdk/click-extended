"""Raised when parents or children are used without a main node."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NoMainNodeError(ClickExtendedError):
    """Raised when parents or children are used without a main node."""
