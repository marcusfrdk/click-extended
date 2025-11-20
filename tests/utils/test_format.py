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
        assert format_list([True, False]) == "True and False"

    def test_three_items(self) -> None:
        """Test formatting three items."""
        assert format_list(["str", "int", "float"]) == "str, int and float"
        assert format_list([1, 2, 3]) == "1, 2 and 3"

    def test_four_items(self) -> None:
        """Test formatting four items."""
        assert format_list(["a", "b", "c", "d"]) == "a, b, c and d"

    def test_many_items(self) -> None:
        """Test formatting many items."""
        result = format_list(["a", "b", "c", "d", "e", "f"])
        assert result == "a, b, c, d, e and f"

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

    def test_three_items_with_prefix(self) -> None:
        """Test three items with plural prefix."""
        result = format_list(
            ["str", "int", "float"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Types: str, int and float"

    def test_professional_prefix(self) -> None:
        """Test with professional prefix format."""
        result = format_list(
            ["str", "int", "float"],
            prefix_singular="Supported type: ",
            prefix_plural="Supported types: ",
        )
        assert result == "Supported types: str, int and float"

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
            format_list([{"key": "value"}])  # type: ignore

    def test_mixed_invalid_type_raises_error(self) -> None:
        """Test that mixed list with non-primitive raises TypeError."""
        with pytest.raises(TypeError, match="All items must be primitives"):
            format_list(["str", [1, 2, 3]])  # type: ignore

    def test_mixed_primitive_types(self) -> None:
        """Test formatting mixed primitive types."""
        result = format_list(["str", 42, 3.14, True])
        assert result == "str, 42, 3.14 and True"

    def test_numeric_types(self) -> None:
        """Test formatting numeric types."""
        assert format_list([1, 2, 3]) == "1, 2 and 3"
        assert format_list([1.5, 2.5]) == "1.5 and 2.5"

    def test_boolean_types(self) -> None:
        """Test formatting boolean types."""
        assert format_list([True, False]) == "True and False"
        assert format_list([True]) == "True"

    def test_string_numbers(self) -> None:
        """Test formatting string representations of numbers."""
        assert format_list(["1", "2", "3"]) == "1, 2 and 3"

    def test_special_characters_in_strings(self) -> None:
        """Test strings with special characters."""
        result = format_list(["hello-world", "foo_bar", "baz.qux"])
        assert result == "hello-world, foo_bar and baz.qux"

    def test_wrap_single_item(self) -> None:
        """Test wrapping a single item."""
        assert format_list(["str"], wrap="'") == "'str'"
        assert format_list(["str"], wrap='"') == '"str"'
        assert format_list(["str"], wrap="`") == "`str`"

    def test_wrap_two_items(self) -> None:
        """Test wrapping two items."""
        assert format_list(["str", "int"], wrap="'") == "'str' and 'int'"
        assert format_list(["x", "y"], wrap='"') == '"x" and "y"'

    def test_wrap_three_items(self) -> None:
        """Test wrapping three items."""
        result = format_list(["str", "int", "float"], wrap="'")
        assert result == "'str', 'int' and 'float'"

    def test_wrap_many_items(self) -> None:
        """Test wrapping many items."""
        result = format_list(["a", "b", "c", "d", "e"], wrap="'")
        assert result == "'a', 'b', 'c', 'd' and 'e'"

    def test_wrap_with_prefix(self) -> None:
        """Test wrap with prefix."""
        result = format_list(
            ["Alice", "Bob", "Charlie"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap="'",
        )
        assert result == "People: 'Alice', 'Bob' and 'Charlie'"

    def test_wrap_single_with_prefix(self) -> None:
        """Test wrap single item with prefix."""
        result = format_list(
            ["Alice"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap='"',
        )
        assert result == 'Person: "Alice"'

    def test_wrap_with_backticks(self) -> None:
        """Test wrapping with backticks (useful for code/markdown)."""
        result = format_list(["str", "int", "float"], wrap="`")
        assert result == "`str`, `int` and `float`"

    def test_wrap_with_brackets(self) -> None:
        """Test wrapping with brackets."""
        result = format_list(["a", "b"], wrap="[")
        assert result == "[a[ and [b["

    def test_wrap_with_empty_string(self) -> None:
        """Test wrap with empty string (should be same as no wrap)."""
        result = format_list(["str", "int"], wrap="")
        assert result == "str and int"

    def test_wrap_with_multichar_wrapper(self) -> None:
        """Test wrapping with multi-character wrapper."""
        result = format_list(["a", "b", "c"], wrap="**")
        assert result == "**a**, **b** and **c**"

    def test_wrap_preserves_numbers(self) -> None:
        """Test that wrap works with numeric types."""
        result = format_list([1, 2, 3], wrap="'")
        assert result == "'1', '2' and '3'"

    def test_wrap_with_special_chars(self) -> None:
        """Test wrap with special characters in items."""
        result = format_list(["hello-world", "foo_bar"], wrap='"')
        assert result == '"hello-world" and "foo_bar"'

    def test_wrap_tuple_single_item(self) -> None:
        """Test wrapping a single item with tuple (left, right)."""
        assert format_list(["str"], wrap=("<", ">")) == "<str>"
        assert format_list(["x"], wrap=("[", "]")) == "[x]"
        assert format_list(["foo"], wrap=("(", ")")) == "(foo)"

    def test_wrap_tuple_two_items(self) -> None:
        """Test wrapping two items with tuple."""
        assert format_list(["str", "int"], wrap=("<", ">")) == "<str> and <int>"
        assert format_list(["x", "y"], wrap=("[", "]")) == "[x] and [y]"

    def test_wrap_tuple_three_items(self) -> None:
        """Test wrapping three items with tuple."""
        result = format_list(["str", "int", "float"], wrap=("<", ">"))
        assert result == "<str>, <int> and <float>"

    def test_wrap_tuple_many_items(self) -> None:
        """Test wrapping many items with tuple."""
        result = format_list(["a", "b", "c", "d", "e"], wrap=("{", "}"))
        assert result == "{a}, {b}, {c}, {d} and {e}"

    def test_wrap_tuple_with_prefix(self) -> None:
        """Test tuple wrap with prefix."""
        result = format_list(
            ["Alice", "Bob", "Charlie"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap=("<", ">"),
        )
        assert result == "People: <Alice>, <Bob> and <Charlie>"

    def test_wrap_tuple_single_with_prefix(self) -> None:
        """Test tuple wrap single item with prefix."""
        result = format_list(
            ["Alice"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap=("[", "]"),
        )
        assert result == "Person: [Alice]"

    def test_wrap_tuple_asymmetric(self) -> None:
        """Test asymmetric tuple wrapping."""
        result = format_list(["a", "b", "c"], wrap=("<< ", " >>"))
        assert result == "<< a >>, << b >> and << c >>"

    def test_wrap_tuple_with_numbers(self) -> None:
        """Test tuple wrap with numeric types."""
        result = format_list([1, 2, 3], wrap=("(", ")"))
        assert result == "(1), (2) and (3)"

    def test_wrap_tuple_html_tags(self) -> None:
        """Test wrapping with HTML-like tags."""
        result = format_list(["bold", "italic"], wrap=("<b>", "</b>"))
        assert result == "<b>bold</b> and <b>italic</b>"

    def test_wrap_tuple_empty_strings(self) -> None:
        """Test tuple wrap with empty strings (same as no wrap)."""
        result = format_list(["str", "int"], wrap=("", ""))
        assert result == "str and int"
