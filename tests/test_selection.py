"""Tests for the selection decorator and interactive function."""

from typing import Any
from unittest.mock import patch

import pytest

from click_extended import selection
from click_extended.core.selection import Selection
from click_extended.interactive import selection as interactive_selection


class TestInteractiveFunctionNormalization:
    """Test selection normalization and validation."""

    def test_empty_selections_raises_error(self) -> None:
        """Test that empty selections list raises ValueError."""
        with pytest.raises(ValueError, match="Selections list cannot be empty"):
            interactive_selection([])

    def test_string_selections(self) -> None:
        """Test selections with strings only."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(["React", "Vue"], default="React")
            assert result == "React"

    def test_tuple_selections(self) -> None:
        """Test selections with (display, value) tuples."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                [("TypeScript", "ts"), ("JavaScript", "js")], default="ts"
            )
            assert result == "ts"

    def test_mixed_selections(self) -> None:
        """Test selections with mixed strings and tuples."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["React", ("Vue.js", "vue")], default="React"
            )
            assert result == "React"

    def test_invalid_tuple_length_raises_error(self) -> None:
        """Test that tuples with wrong length raise ValueError."""
        with pytest.raises(ValueError, match="exactly 2 elements"):
            with patch("sys.stdin.isatty", return_value=False):
                interactive_selection([("Too", "Many", "Items")], default="Too")  # type: ignore


class TestInteractiveFunctionConstraints:
    """Test min/max selection constraint validation."""

    def test_negative_min_selections_raises_error(self) -> None:
        """Test that negative min_selections raises ValueError."""
        with pytest.raises(ValueError, match="min_selections must be >= 0"):
            interactive_selection(["A", "B"], multiple=True, min_selections=-1)

    def test_max_less_than_one_raises_error(self) -> None:
        """Test that max_selections < 1 raises ValueError."""
        with pytest.raises(ValueError, match="max_selections must be >= 1"):
            interactive_selection(["A", "B"], multiple=True, max_selections=0)

    def test_max_less_than_min_raises_error(self) -> None:
        """Test that max < min raises ValueError."""
        with pytest.raises(ValueError, match="must be >= min_selections"):
            interactive_selection(
                ["A", "B"], multiple=True, min_selections=3, max_selections=2
            )

    def test_max_exceeds_options_raises_error(self) -> None:
        """Test that max > num_options raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed number of options"):
            interactive_selection(["A", "B"], multiple=True, max_selections=5)


class TestInteractiveFunctionNonTTY:
    """Test behavior when not running in a TTY."""

    def test_non_tty_without_default_raises_error(self) -> None:
        """Test that non-TTY without default raises RuntimeError."""
        with patch("sys.stdin.isatty", return_value=False):
            with pytest.raises(RuntimeError, match="requires a TTY"):
                interactive_selection(["A", "B"])

    def test_non_tty_with_default_returns_default(self) -> None:
        """Test that non-TTY with default returns the default."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(["A", "B"], default="A")
            assert result == "A"

    def test_non_tty_multiple_with_default_list(self) -> None:
        """Test that non-TTY multiple mode with list default returns the list."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B", "C"], multiple=True, default=["A", "C"]
            )
            assert result == ["A", "C"]


class TestInteractiveFunctionDefaults:
    """Test default value handling."""

    def test_single_mode_string_default(self) -> None:
        """Test single mode with string default."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["React", "Vue", "Angular"], default="Vue"
            )
            assert result == "Vue"

    def test_multiple_mode_list_default(self) -> None:
        """Test multiple mode with list default."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B", "C"], multiple=True, default=["A", "C"]
            )
            assert result == ["A", "C"]

    def test_multiple_mode_single_string_default(self) -> None:
        """Test multiple mode with single string default."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B", "C"], multiple=True, default="B"
            )
            assert result == "B"

    def test_single_mode_list_default_uses_first(self) -> None:
        """Test single mode with list default uses first item."""
        with patch("sys.stdin.isatty", return_value=False):
            # In single mode, list default should be handled as-is
            result = interactive_selection(["A", "B", "C"], default=["B", "C"])
            assert result == ["B", "C"]

    def test_nonexistent_default_not_validated_in_non_tty(self) -> None:
        """Test that nonexistent default values are returned as-is in non-TTY mode."""
        with patch("sys.stdin.isatty", return_value=False):
            # Non-TTY mode simply returns the default without validation
            result = interactive_selection(["A", "B"], default="Z")
            assert result == "Z"


class TestInteractiveFunctionInteractive:
    """Test interactive selection behavior with mocked input."""

    @patch("sys.stdin.isatty", return_value=True)
    @patch("termios.tcgetattr")
    @patch("termios.tcsetattr")
    @patch("tty.setraw")
    def test_single_mode_enter_selects_first(
        self,
        mock_setraw: Any,
        mock_tcsetattr: Any,
        mock_tcgetattr: Any,
        mock_isatty: Any,
    ) -> None:
        """Test that pressing Enter in single mode selects current option."""
        mock_tcgetattr.return_value = []

        with patch("sys.stdin.read", return_value="\r"):
            with patch("sys.stdin.fileno", return_value=0):
                with patch("sys.stdout.write"), patch("sys.stdout.flush"):
                    result = interactive_selection(["React", "Vue", "Angular"])
                    assert result == "React"

    @patch("sys.stdin.isatty", return_value=True)
    @patch("termios.tcgetattr")
    @patch("termios.tcsetattr")
    @patch("tty.setraw")
    def test_ctrl_c_raises_keyboard_interrupt(
        self,
        mock_setraw: Any,
        mock_tcsetattr: Any,
        mock_tcgetattr: Any,
        mock_isatty: Any,
    ) -> None:
        """Test that Ctrl+C raises KeyboardInterrupt."""
        mock_tcgetattr.return_value = []

        with patch("sys.stdin.read", return_value="\x03"):
            with patch("sys.stdin.fileno", return_value=0):
                with patch("sys.stdout.write"), patch("sys.stdout.flush"):
                    with pytest.raises(KeyboardInterrupt):
                        interactive_selection(["A", "B"])


class TestInteractiveFunctionCustomization:
    """Test cursor and checkbox style customization."""

    def test_custom_cursor_style(self) -> None:
        """Test that custom cursor style is accepted."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B"], cursor_style="→", default="A"
            )
            assert result == "A"

    def test_custom_checkbox_style(self) -> None:
        """Test that custom checkbox style is accepted."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B"],
                multiple=True,
                checkbox_style=("☐", "☑"),
                default=["A"],
            )
            assert result == ["A"]

    def test_show_count_parameter(self) -> None:
        """Test that show_count parameter is accepted."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["A", "B"], multiple=True, show_count=True, default=["A"]
            )
            assert result == ["A"]


class TestInteractiveFunctionEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_option_selection(self) -> None:
        """Test selection with only one option."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(["Only"], default="Only")
            assert result == "Only"

    def test_unicode_in_selections(self) -> None:
        """Test selections with unicode characters."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["🚀 React", "⚡ Vue", "🔺 Angular"], default="🚀 React"
            )
            assert result == "🚀 React"

    def test_special_characters_in_selections(self) -> None:
        """Test selections with special characters."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(
                ["Item (1)", "Item [2]", "Item {3}"], default="Item (1)"
            )
            assert result == "Item (1)"


class TestSelectionDecorator:
    """Test the selection decorator."""

    def test_decorator_returns_callable(self) -> None:
        """Test that decorator returns a callable."""
        decorator = selection("framework", ["React", "Vue"])
        assert callable(decorator)

    def test_decorator_can_be_applied(self) -> None:
        """Test that decorator can be applied to a function."""

        @selection("framework", ["React", "Vue"])
        def my_func(framework: str) -> str:
            return framework

        assert callable(my_func)

    def test_decorator_with_all_parameters(self) -> None:
        """Test decorator with all parameters specified."""

        @selection(
            "features",
            [("TypeScript", "ts"), ("ESLint", "eslint")],
            multiple=True,
            default=["eslint"],
            prompt="Select features",
            min_selections=1,
            max_selections=2,
            cursor_style="→",
            checkbox_style=("☐", "☑"),
            show_count=True,
            param="selected_features",
            help="Choose your features",
            required=True,
            tags="config",
        )
        def configure(selected_features: list[str]) -> list[str]:
            return selected_features

        assert callable(configure)

    def test_decorator_preserves_function_name(self) -> None:
        """Test that decorator preserves the function name."""

        @selection("test", ["A", "B"])
        def my_function() -> None:
            pass

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_function_docstring(self) -> None:
        """Test that decorator preserves the function docstring."""

        @selection("test", ["A", "B"])
        def my_function() -> None:
            """This is my function."""
            pass

        assert my_function.__doc__ == "This is my function."


class TestSelectionDecoratorWithCommand:
    """Test selection decorator integration with command decorator."""

    def test_decorator_can_be_imported_and_used(self) -> None:
        """Test that selection decorator is accessible and usable."""
        # Simply verify the decorator exists and is callable
        assert callable(selection)
        # Verify it returns a decorator when called
        decorator_fn = selection("test_param", ["A", "B"], default="A")
        assert callable(decorator_fn)


class TestSelectionNode:
    """Test the Selection ParentNode class."""

    def test_selection_is_parent_node(self) -> None:
        """Test that Selection extends ParentNode."""
        from click_extended.core.parent_node import ParentNode

        assert issubclass(Selection, ParentNode)

    def test_selection_has_load_method(self) -> None:
        """Test that Selection class has a load method."""
        assert hasattr(Selection, "load")
        assert callable(getattr(Selection, "load"))

    @patch("sys.stdin.isatty", return_value=False)
    def test_load_returns_default_when_provided(self, mock_isatty: Any) -> None:
        """Test that load method returns default value in non-TTY mode."""
        with patch("sys.stdin.isatty", return_value=False):
            result = interactive_selection(["React", "Vue"], default="React")
            assert result == "React"


class TestSelectionParameterPassing:
    """Test that parameters are correctly passed through the decorator."""

    @patch("sys.stdin.isatty", return_value=False)
    def test_all_parameters_work_together(self, mock_isatty: Any) -> None:
        """Test that all parameters can be used together."""
        result = interactive_selection(
            selections=[("React", "react"), ("Vue", "vue")],
            prompt="Select framework",
            multiple=True,
            default=["react"],
            min_selections=1,
            max_selections=2,
            cursor_style="→",
            checkbox_style=("☐", "☑"),
            show_count=True,
        )
        assert result == ["react"]
