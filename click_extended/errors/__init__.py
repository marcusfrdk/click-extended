"""Initialization file for the 'click_extended.errors' package."""

from click_extended.errors.click_extended_error import ClickExtendedError
from click_extended.errors.decorator_implementation_error import (
    DecoratorImplementationError,
)
from click_extended.errors.no_main_node_error import NoMainNodeError
from click_extended.errors.no_parent_node_error import NoParentNodeError
from click_extended.errors.tagged_environment_error import TaggedEnvironmentError
from click_extended.errors.usage_error import UsageError

__all__ = [
    "ClickExtendedError",
    "DecoratorImplementationError",
    "NoMainNodeError",
    "NoParentNodeError",
    "TaggedEnvironmentError",
    "UsageError",
]
