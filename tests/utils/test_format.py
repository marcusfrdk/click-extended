"""Tests for format utility functions."""

import pytest

from click_extended.utils.format import format_list


class TestFormatList:
    """Tests for the format_list function."""

    def test_single_item(self) -> None:
        """Test formatting a single item."""
        assert format_list(["str"]) == "str"
        assert format_list([42]) == "42"
        assert format_list([3.14]) == "3.14"
        assert format_list([True]) == "True"

    def test_two_items(self) -> None:
        """Test formatting two items."""
        assert format_list(["str", "int"]) == "str and int"
        assert format_list([1, 2]) == "1 and 2"

    def test_three_items(self) -> None:
        """Test formatting three items."""
        assert format_list(["str", "int", "float"]) == "str, int and float"

    def test_single_item_with_prefix(self) -> None:
        """Test single item with singular prefix."""
        result = format_list(
            ["str"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Type: str"

    def test_two_items_with_prefix(self) -> None:
        """Test two items with plural prefix."""
        result = format_list(
            ["str", "int"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Types: str and int"

    def test_empty_list_raises_error(self) -> None:
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot format an empty list"):
            format_list([])

    def test_only_singular_prefix_raises_error(self) -> None:
        """Test that providing only singular prefix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both prefix_singular and prefix_plural must be provided together",
        ):
            format_list(["str"], prefix_singular="Type: ")

    def test_only_plural_prefix_raises_error(self) -> None:
        """Test that providing only plural prefix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both prefix_singular and prefix_plural must be provided together",
        ):
            format_list(["str", "int"], prefix_plural="Types: ")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-primitive types raise TypeError."""
        with pytest.raises(TypeError, match="All items must be primitives"):
            format_list([{"key": "value"}])  # type: ignore[list-item]

    def test_wrap_single_item(self) -> None:
        """Test wrapping a single item."""
        assert format_list(["str"], wrap="'") == "'str'"

    def test_wrap_two_items(self) -> None:
        """Test wrapping two items."""
        assert format_list(["str", "int"], wrap="'") == "'str' and 'int'"

    def test_wrap_three_items(self) -> None:
        """Test wrapping three items."""
        result = format_list(["str", "int", "float"], wrap="'")
        assert result == "'str', 'int' and 'float'"

    def test_wrap_tuple_single_item(self) -> None:
        """Test wrapping a single item with tuple."""
        assert format_list(["str"], wrap=("<", ">")) == "<str>"

    def test_wrap_tuple_two_items(self) -> None:
        """Test wrapping two items with tuple."""
        assert format_list(["str", "int"], wrap=("<", ">")) == "<str> and <int>"

    def test_wrap_tuple_three_items(self) -> None:
        """Test wrapping three items with tuple."""
        result = format_list(["str", "int", "float"], wrap=("<", ">"))
        assert result == "<str>, <int> and <float>"
