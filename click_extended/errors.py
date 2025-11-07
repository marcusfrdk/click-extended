"""Errors and exceptions used in Click Extended."""


class ClickExtendedError(Exception):
    """Base exception for all click_extended errors."""


class DecoratorImplementationError(ClickExtendedError):
    """Raised when a decorator is improperly implemented."""


class NoMainNodeError(ClickExtendedError):
    """Raised when parents or children are used without a main node."""


class NoParentNodeError(ClickExtendedError):
    """Raised when a child decorator is used without a parent decorator."""


class TaggedEnvironmentError(ClickExtendedError):
    """Raised when child used in tagged environment without implementation."""


class UsageError(ClickExtendedError):
    """Raised when a decorator is used incorrectly."""
