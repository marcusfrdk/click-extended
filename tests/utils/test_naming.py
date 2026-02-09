"""Tests for naming utility functions."""

import pytest

from click_extended.utils.naming import (
    is_long_flag,
    is_short_flag,
    is_valid_name,
    parse_option_args,
    validate_name,
)


class TestIsValidName:
    """Test is_valid_name function."""

    def test_valid_snake_case(self) -> None:
        """Test valid snake_case names."""
        assert is_valid_name("my_option") is True
        assert is_valid_name("config_file") is True
        assert is_valid_name("test") is True
        assert is_valid_name("a") is True
        assert is_valid_name("option_1") is True
        assert is_valid_name("option_123") is True

    def test_invalid_screaming_snake_case(self) -> None:
        """Test that SCREAMING_SNAKE_CASE names are now invalid."""
        assert is_valid_name("MY_OPTION") is False
        assert is_valid_name("CONFIG_FILE") is False
        assert is_valid_name("TEST") is False
        assert is_valid_name("A") is False
        assert is_valid_name("OPTION_1") is False
        assert is_valid_name("OPTION_123") is False

    def test_invalid_kebab_case(self) -> None:
        """Test that kebab-case names are now invalid."""
        assert is_valid_name("my-option") is False
        assert is_valid_name("config-file") is False
        assert is_valid_name("option-1") is False
        assert is_valid_name("option-123") is False

    def test_invalid_names(self) -> None:
        """Test invalid names."""
        assert is_valid_name("") is False
        assert is_valid_name("1invalid") is False
        assert is_valid_name("_invalid") is False
        assert is_valid_name("Invalid") is False
        assert is_valid_name("camelCase") is False
        assert is_valid_name("PascalCase") is False
        assert is_valid_name("my option") is False
        assert is_valid_name("my.option") is False
        assert is_valid_name("my__option") is False
        assert is_valid_name("my-_option") is False


class TestIsLongFlag:
    """Test is_long_flag function."""

    def test_valid_long_flags(self) -> None:
        """Test valid long flags."""
        assert is_long_flag("--option") is True
        assert is_long_flag("--my-option") is True
        assert is_long_flag("--config-file") is True
        assert is_long_flag("--o") is True
        assert is_long_flag("--option-1") is True
        assert is_long_flag("--option-123") is True

    def test_invalid_long_flags(self) -> None:
        """Test invalid long flags."""
        assert is_long_flag("-option") is False
        assert is_long_flag("--Option") is False
        assert is_long_flag("--OPTION") is False
        assert is_long_flag("--my_option") is False
        assert is_long_flag("--1option") is False
        assert is_long_flag("---option") is False
        assert is_long_flag("--") is False
        assert is_long_flag("") is False


class TestIsShortFlag:
    """Test is_short_flag function."""

    def test_valid_short_flags(self) -> None:
        """Test valid short flags."""
        assert is_short_flag("-o") is True
        assert is_short_flag("-m") is True
        assert is_short_flag("-A") is True
        assert is_short_flag("-Z") is True
        assert is_short_flag("-lws") is True
        assert is_short_flag("-option") is True
        assert is_short_flag("-abc123") is True

    def test_invalid_short_flags(self) -> None:
        """Test invalid short flags."""
        assert is_short_flag("--o") is False
        assert is_short_flag("-1") is False
        assert is_short_flag("--") is False
        assert is_short_flag("-") is False
        assert is_short_flag("") is False
        assert is_short_flag("o") is False


class TestValidateName:
    """Test validate_name function."""

    def test_validate_valid_names(self) -> None:
        """Test that valid names don't raise."""
        validate_name("my_option")
        validate_name("config_file")
        validate_name("test")

    def test_validate_invalid_name_raises(self) -> None:
        """Test that invalid names raise SystemExit."""
        with pytest.raises(SystemExit):
            validate_name("Invalid")

    def test_validate_with_custom_context(self) -> None:
        """Test that custom context appears in error message."""
        with pytest.raises(SystemExit):
            validate_name("Invalid", context="option name")


class TestParseOptionArgs:
    """Test parse_option_args function."""

    def test_no_args(self) -> None:
        """Test parsing with no arguments."""
        name, short, long = parse_option_args()
        assert name is None
        assert short is None
        assert long is None

    def test_name_only(self) -> None:
        """Test parsing with name only."""
        name, short, long = parse_option_args("my_option")
        assert name == "my_option"
        assert short is None
        assert long is None

    def test_long_flag_only(self) -> None:
        """Test parsing with long flag only."""
        name, short, long = parse_option_args("--my-option")
        assert name is None
        assert short is None
        assert long == "--my-option"

    def test_short_and_long_flags(self) -> None:
        """Test parsing with short and long flags."""
        name, short, long = parse_option_args("-m", "--my-option")
        assert name is None
        assert short == "-m"
        assert long == "--my-option"

    def test_short_flag_alone_raises(self) -> None:
        """Test that short flag alone raises ValueError."""
        with pytest.raises(
            ValueError, match="Short flag '-m' provided without long flag"
        ):
            parse_option_args("-m")

    def test_wrong_order_raises(self) -> None:
        """Test that wrong argument order raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Invalid argument order.*Short flag must come before",
        ):
            parse_option_args("--my-option", "-m")

    def test_invalid_name_raises(self) -> None:
        """Test that invalid name raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_option_args("Invalid")

    def test_two_names_raises(self) -> None:
        """Test that two names raise ValueError."""
        with pytest.raises(ValueError, match="Invalid arguments"):
            parse_option_args("name1", "name2")

    def test_too_many_args_raises(self) -> None:
        """Test that too many arguments raise ValueError."""
        with pytest.raises(ValueError, match="Too many positional arguments"):
            parse_option_args("-m", "--my-option", "--extra")
