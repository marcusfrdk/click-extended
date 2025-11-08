"""Tests for transform utilities."""

import pytest

from click_extended.utils.transform import to_screaming_snake_case, to_snake_case


class TestToSnakeCase:
    """Test class for transform utilities."""

    def test_transformations(self):
        """Test the cases where input values are valid."""
        cases: list[tuple[str, str]] = [
            ("Hello world", "hello_world"),
            ("Hello-world!", "hello_world"),
            ("hello_world", "hello_world"),
            ("Hello, world. This is a string.", "hello_world_this_is_a_string"),
            ("... This is a string", "this_is_a_string"),
        ]

        for left, right in cases:
            assert to_snake_case(left) == right

    def test_invalid_input_type(self):
        """Test the case where the input value is not a string."""
