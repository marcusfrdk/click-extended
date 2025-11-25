"""Tests for format utility functions."""

import pytest

from click_extended.utils.humanize import humanize_iterable, humanize_type


class TestHumanizeList:
    """Tests for the humanize_iterable function."""

    def test_single_item(self) -> None:
        """Test formatting a single item."""
        assert humanize_iterable(["str"]) == "str"
        assert humanize_iterable([42]) == "42"
        assert humanize_iterable([3.14]) == "3.14"
        assert humanize_iterable([True]) == "True"

    def test_two_items(self) -> None:
        """Test formatting two items."""
        assert humanize_iterable(["str", "int"]) == "str and int"
        assert humanize_iterable([1, 2]) == "1 and 2"
        assert humanize_iterable([True, False]) == "True and False"

    def test_three_items(self) -> None:
        """Test formatting three items."""
        assert (
            humanize_iterable(["str", "int", "float"]) == "str, int and float"
        )
        assert humanize_iterable([1, 2, 3]) == "1, 2 and 3"

    def test_four_items(self) -> None:
        """Test formatting four items."""
        assert humanize_iterable(["a", "b", "c", "d"]) == "a, b, c and d"

    def test_many_items(self) -> None:
        """Test formatting many items."""
        result = humanize_iterable(["a", "b", "c", "d", "e", "f"])
        assert result == "a, b, c, d, e and f"

    def test_single_item_with_prefix(self) -> None:
        """Test single item with singular prefix."""
        result = humanize_iterable(
            ["str"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Type: str"

    def test_two_items_with_prefix(self) -> None:
        """Test two items with plural prefix."""
        result = humanize_iterable(
            ["str", "int"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Types: str and int"

    def test_three_items_with_prefix(self) -> None:
        """Test three items with plural prefix."""
        result = humanize_iterable(
            ["str", "int", "float"],
            prefix_singular="Type: ",
            prefix_plural="Types: ",
        )
        assert result == "Types: str, int and float"

    def test_professional_prefix(self) -> None:
        """Test with professional prefix format."""
        result = humanize_iterable(
            ["str", "int", "float"],
            prefix_singular="Supported type: ",
            prefix_plural="Supported types: ",
        )
        assert result == "Supported types: str, int and float"

    def test_empty_list_raises_error(self) -> None:
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot format an empty iterable"):
            humanize_iterable([])

    def test_only_singular_prefix_raises_error(self) -> None:
        """Test that providing only singular prefix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both prefix_singular and prefix_plural must be provided together",
        ):
            humanize_iterable(["str"], prefix_singular="Type: ")

    def test_only_plural_prefix_raises_error(self) -> None:
        """Test that providing only plural prefix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both prefix_singular and prefix_plural must be provided together",
        ):
            humanize_iterable(["str", "int"], prefix_plural="Types: ")

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-primitive types raise TypeError."""
        with pytest.raises(TypeError, match="All items must be primitives"):
            humanize_iterable([{"key": "value"}])  # type: ignore

    def test_mixed_invalid_type_raises_error(self) -> None:
        """Test that mixed list with non-primitive raises TypeError."""
        with pytest.raises(TypeError, match="All items must be primitives"):
            humanize_iterable(["str", [1, 2, 3]])  # type: ignore

    def test_mixed_primitive_types(self) -> None:
        """Test formatting mixed primitive types."""
        result = humanize_iterable(["str", 42, 3.14, True])
        assert result == "str, 42, 3.14 and True"

    def test_numeric_types(self) -> None:
        """Test formatting numeric types."""
        assert humanize_iterable([1, 2, 3]) == "1, 2 and 3"
        assert humanize_iterable([1.5, 2.5]) == "1.5 and 2.5"

    def test_boolean_types(self) -> None:
        """Test formatting boolean types."""
        assert humanize_iterable([True, False]) == "True and False"
        assert humanize_iterable([True]) == "True"

    def test_string_numbers(self) -> None:
        """Test formatting string representations of numbers."""
        assert humanize_iterable(["1", "2", "3"]) == "1, 2 and 3"

    def test_special_characters_in_strings(self) -> None:
        """Test strings with special characters."""
        result = humanize_iterable(["hello-world", "foo_bar", "baz.qux"])
        assert result == "hello-world, foo_bar and baz.qux"

    def test_wrap_single_item(self) -> None:
        """Test wrapping a single item."""
        assert humanize_iterable(["str"], wrap="'") == "'str'"
        assert humanize_iterable(["str"], wrap='"') == '"str"'
        assert humanize_iterable(["str"], wrap="`") == "`str`"

    def test_wrap_two_items(self) -> None:
        """Test wrapping two items."""
        assert humanize_iterable(["str", "int"], wrap="'") == "'str' and 'int'"
        assert humanize_iterable(["x", "y"], wrap='"') == '"x" and "y"'

    def test_wrap_three_items(self) -> None:
        """Test wrapping three items."""
        result = humanize_iterable(["str", "int", "float"], wrap="'")
        assert result == "'str', 'int' and 'float'"

    def test_wrap_many_items(self) -> None:
        """Test wrapping many items."""
        result = humanize_iterable(["a", "b", "c", "d", "e"], wrap="'")
        assert result == "'a', 'b', 'c', 'd' and 'e'"

    def test_wrap_with_prefix(self) -> None:
        """Test wrap with prefix."""
        result = humanize_iterable(
            ["Alice", "Bob", "Charlie"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap="'",
        )
        assert result == "People: 'Alice', 'Bob' and 'Charlie'"

    def test_wrap_single_with_prefix(self) -> None:
        """Test wrap single item with prefix."""
        result = humanize_iterable(
            ["Alice"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap='"',
        )
        assert result == 'Person: "Alice"'

    def test_wrap_with_backticks(self) -> None:
        """Test wrapping with backticks (useful for code/markdown)."""
        result = humanize_iterable(["str", "int", "float"], wrap="`")
        assert result == "`str`, `int` and `float`"

    def test_wrap_with_brackets(self) -> None:
        """Test wrapping with brackets."""
        result = humanize_iterable(["a", "b"], wrap="[")
        assert result == "[a[ and [b["

    def test_wrap_with_empty_string(self) -> None:
        """Test wrap with empty string (should be same as no wrap)."""
        result = humanize_iterable(["str", "int"], wrap="")
        assert result == "str and int"

    def test_wrap_with_multichar_wrapper(self) -> None:
        """Test wrapping with multi-character wrapper."""
        result = humanize_iterable(["a", "b", "c"], wrap="**")
        assert result == "**a**, **b** and **c**"

    def test_wrap_preserves_numbers(self) -> None:
        """Test that wrap works with numeric types."""
        result = humanize_iterable([1, 2, 3], wrap="'")
        assert result == "'1', '2' and '3'"

    def test_wrap_with_special_chars(self) -> None:
        """Test wrap with special characters in items."""
        result = humanize_iterable(["hello-world", "foo_bar"], wrap='"')
        assert result == '"hello-world" and "foo_bar"'

    def test_wrap_tuple_single_item(self) -> None:
        """Test wrapping a single item with tuple (left, right)."""
        assert humanize_iterable(["str"], wrap=("<", ">")) == "<str>"
        assert humanize_iterable(["x"], wrap=("[", "]")) == "[x]"
        assert humanize_iterable(["foo"], wrap=("(", ")")) == "(foo)"

    def test_wrap_tuple_two_items(self) -> None:
        """Test wrapping two items with tuple."""
        assert (
            humanize_iterable(["str", "int"], wrap=("<", ">"))
            == "<str> and <int>"
        )
        assert humanize_iterable(["x", "y"], wrap=("[", "]")) == "[x] and [y]"

    def test_wrap_tuple_three_items(self) -> None:
        """Test wrapping three items with tuple."""
        result = humanize_iterable(["str", "int", "float"], wrap=("<", ">"))
        assert result == "<str>, <int> and <float>"

    def test_wrap_tuple_many_items(self) -> None:
        """Test wrapping many items with tuple."""
        result = humanize_iterable(["a", "b", "c", "d", "e"], wrap=("{", "}"))
        assert result == "{a}, {b}, {c}, {d} and {e}"

    def test_wrap_tuple_with_prefix(self) -> None:
        """Test tuple wrap with prefix."""
        result = humanize_iterable(
            ["Alice", "Bob", "Charlie"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap=("<", ">"),
        )
        assert result == "People: <Alice>, <Bob> and <Charlie>"

    def test_wrap_tuple_single_with_prefix(self) -> None:
        """Test tuple wrap single item with prefix."""
        result = humanize_iterable(
            ["Alice"],
            prefix_singular="Person: ",
            prefix_plural="People: ",
            wrap=("[", "]"),
        )
        assert result == "Person: [Alice]"

    def test_wrap_tuple_asymmetric(self) -> None:
        """Test asymmetric tuple wrapping."""
        result = humanize_iterable(["a", "b", "c"], wrap=("<< ", " >>"))
        assert result == "<< a >>, << b >> and << c >>"

    def test_wrap_tuple_with_numbers(self) -> None:
        """Test tuple wrap with numeric types."""
        result = humanize_iterable([1, 2, 3], wrap=("(", ")"))
        assert result == "(1), (2) and (3)"

    def test_wrap_tuple_html_tags(self) -> None:
        """Test wrapping with HTML-like tags."""
        result = humanize_iterable(["bold", "italic"], wrap=("<b>", "</b>"))
        assert result == "<b>bold</b> and <b>italic</b>"

    def test_wrap_tuple_empty_strings(self) -> None:
        """Test tuple wrap with empty strings (same as no wrap)."""
        result = humanize_iterable(["str", "int"], wrap=("", ""))
        assert result == "str and int"

    def test_suffix_single_item(self) -> None:
        """Test single item with singular suffix."""
        result = humanize_iterable(
            ["apple"],
            suffix_singular=" is available",
            suffix_plural=" are available",
        )
        assert result == "apple is available"

    def test_suffix_multiple_items(self) -> None:
        """Test multiple items with plural suffix."""
        result = humanize_iterable(
            ["apple", "banana"],
            suffix_singular=" is available",
            suffix_plural=" are available",
        )
        assert result == "apple and banana are available"

    def test_only_singular_suffix_raises_error(self) -> None:
        """Test that providing only singular suffix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both suffix_singular and suffix_plural must be provided together",
        ):
            humanize_iterable(["str"], suffix_singular="!")

    def test_only_plural_suffix_raises_error(self) -> None:
        """Test that providing only plural suffix raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Both suffix_singular and suffix_plural must be provided together",
        ):
            humanize_iterable(["str", "int"], suffix_plural="!")

    def test_prefix_and_suffix_together(self) -> None:
        """Test using both prefix and suffix."""
        result = humanize_iterable(
            ["apple"],
            prefix_singular="The item ",
            prefix_plural="The items ",
            suffix_singular=" is ready",
            suffix_plural=" are ready",
        )
        assert result == "The item apple is ready"

        result = humanize_iterable(
            ["apple", "banana"],
            prefix_singular="The item ",
            prefix_plural="The items ",
            suffix_singular=" is ready",
            suffix_plural=" are ready",
        )
        assert result == "The items apple and banana are ready"


class TestHumanizeType:
    """Tests for the humanize_type function."""

    def test_basic_type(self) -> None:
        """Test basic type formatting."""
        assert humanize_type(str) == "str"
        assert humanize_type(int) == "int"
        assert humanize_type(float) == "float"
        assert humanize_type(bool) == "bool"

    def test_union_two_types(self) -> None:
        """Test union of two types."""
        assert humanize_type(str | int) == "str and int"
        assert humanize_type(int | float) == "int and float"

    def test_union_three_types(self) -> None:
        """Test union of three types."""
        assert humanize_type(str | int | float) == "str, int and float"
        assert humanize_type(int | float | bool) == "int, float and bool"

    def test_list_with_single_type(self) -> None:
        """Test list with single inner type."""
        assert humanize_type(list[str]) == "list[str]"
        assert humanize_type(list[int]) == "list[int]"

    def test_list_with_union(self) -> None:
        """Test list with union of inner types."""
        assert humanize_type(list[str | int]) == "list[str | int]"
        assert humanize_type(list[int | float]) == "list[int | float]"

    def test_dict_with_types(self) -> None:
        """Test dict with key and value types."""
        assert humanize_type(dict[str, int]) == "dict[str, int]"
        assert humanize_type(dict[str, str | int]) == "dict[str, str | int]"

    def test_tuple_with_ellipsis(self) -> None:
        """Test tuple with ellipsis."""
        assert humanize_type(tuple[int, ...]) == "tuple[int, ...]"
        assert humanize_type(tuple[str, ...]) == "tuple[str, ...]"
        assert humanize_type(tuple[str | int, ...]) == "tuple[str | int, ...]"

    def test_tuple_with_fixed_types(self) -> None:
        """Test tuple with fixed types."""
        assert humanize_type(tuple[str, int]) == "tuple[str, int]"
        assert humanize_type(tuple[str, int, float]) == "tuple[str, int, float]"

    def test_union_of_generics(self) -> None:
        """Test union of generic types."""
        assert (
            humanize_type(list[str] | tuple[str]) == "list[str] and tuple[str]"
        )
        assert humanize_type(str | list[str]) == "str and list[str]"

    def test_complex_nested_union(self) -> None:
        """Test complex nested union in list."""
        assert (
            humanize_type(str | list[str | float])
            == "str and list[str | float]"
        )
        assert humanize_type(int | list[str | int]) == "int and list[str | int]"

    def test_deeply_nested_list(self) -> None:
        """Test deeply nested list types."""
        assert humanize_type(list[list[str]]) == "list[list[str]]"
        assert humanize_type(list[list[str | int]]) == "list[list[str | int]]"

    def test_set_type(self) -> None:
        """Test set types."""
        assert humanize_type(set[str]) == "set[str]"
        assert humanize_type(set[int | str]) == "set[int | str]"

    def test_none_type(self) -> None:
        """Test None type formatting."""
        assert humanize_type(type(None)) == "None"
        assert humanize_type(str | None) == "str and None"
        assert humanize_type(int | None) == "int and None"

    def test_type_without_name_attribute(self) -> None:
        """Test type that doesn't have __name__ attribute."""

        class MockType:
            def __str__(self) -> str:
                return "MockCustomType"

        mock_type = MockType()
        result = humanize_type(mock_type)  # type: ignore[arg-type]
        assert result == "MockCustomType"
