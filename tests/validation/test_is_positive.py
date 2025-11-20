"""Test the `is_positive` validation decorator."""

import pytest
from click.testing import CliRunner

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.errors import TypeMismatchError, ValidationError
from click_extended.validation.is_positive import IsPositive, is_positive


def make_context(parent_name: str = "test") -> ProcessContext:
    """Helper to create a ProcessContext for testing."""
    from unittest.mock import MagicMock

    parent = MagicMock()
    parent.name = parent_name
    return ProcessContext(
        parent=parent,
        siblings=[],
        tags={},
        args=(),
        kwargs={},
    )


class TestIsPositive:
    """Test IsPositive validation child node."""

    def test_positive_integer_passes(self) -> None:
        """Test that positive integers pass validation."""
        validator = IsPositive(name="test_validator")
        context = make_context("count")
        validator.process(5, context)  # Should not raise

    def test_positive_float_passes(self) -> None:
        """Test that positive floats pass validation."""
        validator = IsPositive(name="test_validator")
        context = make_context("ratio")
        validator.process(3.14, context)  # Should not raise

    def test_zero_fails(self) -> None:
        """Test that zero fails validation."""
        validator = IsPositive(name="test_validator")
        context = make_context("count")
        with pytest.raises(ValidationError) as exc_info:
            validator.process(0, context)
        assert "0 is not positive" in str(exc_info.value)

    def test_negative_integer_fails(self) -> None:
        """Test that negative integers fail validation."""
        validator = IsPositive(name="test_validator")
        context = make_context("amount")
        with pytest.raises(ValidationError) as exc_info:
            validator.process(-5, context)
        assert "-5 is not positive" in str(exc_info.value)

    def test_negative_float_fails(self) -> None:
        """Test that negative floats fail validation."""
        validator = IsPositive(name="test_validator")
        context = make_context("value")
        with pytest.raises(ValidationError) as exc_info:
            validator.process(-2.5, context)
        assert "-2.5 is not positive" in str(exc_info.value)

    def test_error_message_includes_parent_name(self) -> None:
        """Test that error message includes the invalid value."""
        validator = IsPositive(name="test_validator")
        context = make_context("port")
        with pytest.raises(ValidationError) as exc_info:
            validator.process(-1, context)
        assert "-1 is not positive" in str(exc_info.value)

    def test_error_message_includes_value(self) -> None:
        """Test that error message includes the invalid value."""
        validator = IsPositive(name="test_validator")
        context = make_context("count")
        with pytest.raises(ValidationError) as exc_info:
            validator.process(-100, context)
        assert "-100" in str(exc_info.value)

    def test_large_positive_value(self) -> None:
        """Test with very large positive value."""
        validator = IsPositive(name="test_validator")
        context = make_context("large_number")
        validator.process(1_000_000, context)  # Should not raise

    def test_small_positive_float(self) -> None:
        """Test with very small positive float."""
        validator = IsPositive(name="test_validator")
        context = make_context("epsilon")
        validator.process(0.0001, context)  # Should not raise

    def test_validator_is_child_node(self) -> None:
        """Test that IsPositive is a ChildNode subclass."""
        validator = IsPositive(name="test_validator")
        assert isinstance(validator, ChildNode)

    def test_validator_has_name(self) -> None:
        """Test that validator has a name attribute."""
        validator = IsPositive(name="custom_name")
        assert validator.name == "custom_name"

    def test_none_value_is_skipped(self) -> None:
        """Test that None values are skipped via skip_none mechanism."""
        validator = IsPositive(name="test_validator")
        assert validator.should_skip_none() is True


class TestIsPositiveDecorator:
    """Test is_positive decorator in CLI context."""

    def test_decorator_with_positive_value(self) -> None:
        """Test decorator allows positive values in CLI."""

        @command()
        @option("--count", "-c", type=int, default=1)
        @is_positive()
        def test_cmd(count: int) -> None:
            """Test command."""
            print(f"Count: {count}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--count", "5"])  # type: ignore

        assert result.exit_code == 0
        assert "Count: 5" in result.output

    def test_decorator_with_zero_value(self) -> None:
        """Test decorator rejects zero in CLI."""

        @command()
        @option("--count", "-c", type=int, default=1)
        @is_positive()
        def test_cmd(count: int) -> None:
            """Test command."""
            print(f"Count: {count}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--count", "0"])  # type: ignore

        assert result.exit_code != 0
        assert "0 is not positive" in result.output

    def test_decorator_with_negative_value(self) -> None:
        """Test decorator rejects negative values in CLI."""

        @command()
        @option("--amount", "-a", type=int, default=10)
        @is_positive()
        def test_cmd(amount: int) -> None:
            """Test command."""
            print(f"Amount: {amount}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--amount", "-5"])  # type: ignore

        assert result.exit_code != 0
        assert "-5 is not positive" in result.output

    def test_decorator_with_float_value(self) -> None:
        """Test decorator with positive float values."""

        @command()
        @option("--ratio", "-r", type=float, default=1.0)
        @is_positive()
        def test_cmd(ratio: float) -> None:
            """Test command."""
            print(f"Ratio: {ratio}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--ratio", "2.5"])  # type: ignore

        assert result.exit_code == 0
        assert "Ratio: 2.5" in result.output

    def test_decorator_with_negative_float(self) -> None:
        """Test decorator rejects negative floats."""

        @command()
        @option("--ratio", "-r", type=float, default=1.0)
        @is_positive()
        def test_cmd(ratio: float) -> None:
            """Test command."""
            print(f"Ratio: {ratio}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--ratio", "-1.5"])  # type: ignore

        assert result.exit_code != 0
        assert "-1.5 is not positive" in result.output

    def test_decorator_error_includes_option_name(self) -> None:
        """Test that validation error includes the option name."""

        @command()
        @option("--port", "-p", type=int, default=8080)
        @is_positive()
        def test_cmd(port: int) -> None:
            """Test command."""
            print(f"Port: {port}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--port", "-1"])  # type: ignore

        assert result.exit_code != 0
        assert "--port" in result.output
        assert "-1 is not positive" in result.output

    def test_decorator_with_default_positive_value(self) -> None:
        """Test decorator works with default positive value."""

        @command()
        @option("--timeout", "-t", type=int, default=30)
        @is_positive()
        def test_cmd(timeout: int) -> None:
            """Test command."""
            print(f"Timeout: {timeout}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert "Timeout: 30" in result.output

    def test_decorator_returns_callable(self) -> None:
        """Test that is_positive decorator returns a callable."""
        decorator = is_positive()
        assert callable(decorator)

    def test_decorator_can_be_applied_to_function(self) -> None:
        """Test that decorator can be applied to a function."""

        @is_positive()
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_decorator_with_optional_argument_not_provided(self) -> None:
        """Test that validator handles optional arguments when not provided."""
        from click_extended.core.argument import argument

        @command()
        @argument("value", type=int, default=None)
        @is_positive()
        def test_cmd(value: int | None) -> None:
            """Test command."""
            if value is None:
                print("No value provided")
            else:
                print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, [])  # type: ignore

        assert result.exit_code == 0
        assert "No value provided" in result.output


class TestIsPositiveTypeValidation:
    """Test type validation for IsPositive decorator."""

    def test_supports_int_type(self) -> None:
        """Test that is_positive supports int type."""

        @command()
        @option("--count", "-c", type=int, default=1)
        @is_positive()
        def test_cmd(count: int) -> None:
            """Test command."""
            print(f"Count: {count}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--count", "5"])  # type: ignore

        assert result.exit_code == 0
        assert "Count: 5" in result.output

    def test_supports_float_type(self) -> None:
        """Test that is_positive supports float type."""

        @command()
        @option("--ratio", "-r", type=float, default=1.0)
        @is_positive()
        def test_cmd(ratio: float) -> None:
            """Test command."""
            print(f"Ratio: {ratio}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--ratio", "2.5"])  # type: ignore

        assert result.exit_code == 0
        assert "Ratio: 2.5" in result.output

    def test_rejects_string_type(self) -> None:
        """Test that is_positive rejects string type."""

        @command()
        @option("--name", "-n", type=str, default="test")
        @is_positive()
        def test_cmd(name: str) -> None:
            """Test command."""
            print(f"Name: {name}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--name", "hello"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, TypeMismatchError)
        assert "is_positive" in str(result.exception)
        assert "str" in str(result.exception)

    def test_rejects_bool_type(self) -> None:
        """Test that is_positive rejects explicit bool type."""

        @command()
        @option("--enabled", "-e", type=bool, default=False)
        @is_positive()
        def test_cmd(enabled: bool) -> None:
            """Test command."""
            print(f"Enabled: {enabled}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--enabled", "true"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, TypeMismatchError)
        assert "is_positive" in str(result.exception)
        assert "bool" in str(result.exception)

    def test_allows_no_type_specified(self) -> None:
        """Test that is_positive allows options with no type specified."""

        @command()
        @option("--value", "-v", default=5)
        @is_positive()
        def test_cmd(value: int) -> None:
            """Test command."""
            print(f"Value: {value}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--value", "10"])  # type: ignore

        # Should succeed because no type means validation is skipped
        assert result.exit_code == 0
        assert "Value: 10" in result.output
