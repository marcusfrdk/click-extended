"""Raised when a child decorator is used without a parent decorator."""

from click_extended.errors.click_extended_error import ClickExtendedError


class NoParentNodeError(ClickExtendedError):
    """Raised when a child decorator is used without a parent decorator."""
