"""Initialization file for the 'click_extended' module."""

from click_extended.core.argument import argument
from click_extended.core.command import command
from click_extended.core.env import env
from click_extended.core.group import group
from click_extended.core.option import option
from click_extended.core.prompt import prompt
from click_extended.core.tag import tag

__all__ = [
    "argument",
    "command",
    "env",
    "group",
    "option",
    "prompt",
    "tag",
]
