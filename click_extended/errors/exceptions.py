"""Custom exceptions for click_extended."""


class ClickExtendedError(Exception):
    """Base exception for all click_extended errors."""


class DecoratorImplementationError(ClickExtendedError):
    """Raised when a decorator is improperly implemented."""


class TaggedEnvironmentError(ClickExtendedError):
    """Raised when a child is used in a tagged environment without proper implementation."""


class UsageError(ClickExtendedError):
    """Raised when a decorator is used incorrectly."""


class NoMainNodeError(ClickExtendedError):
    """Raised when parents or children are used without a main node."""


class NoParentError(ClickExtendedError):
    """Raised when a child decorator is used without a parent decorator."""
