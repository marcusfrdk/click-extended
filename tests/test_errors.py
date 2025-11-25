"""Tests for error classes."""

import sys
from io import StringIO
from typing import Any
from unittest.mock import Mock, patch

import click
import pytest

from click_extended.errors import (
    ClickExtendedError,
    ContextAwareError,
    InternalError,
    InvalidHandlerError,
    MissingValueError,
    NameExistsError,
    NoParentError,
    NoRootError,
    ParentExistsError,
    ProcessError,
    RootExistsError,
    TypeMismatchError,
    UnhandledTypeError,
)


class TestClickExtendedError:
    """Test base ClickExtendedError class."""

    def test_init_with_message(self) -> None:
        """Test creating error with message only."""
        error = ClickExtendedError("Test error")
        assert error.message == "Test error"
        assert error.tip is None
        assert str(error) == "Test error"

    def test_init_with_tip(self) -> None:
        """Test creating error with message and tip."""
        error = ClickExtendedError("Test error", tip="Try this fix")
        assert error.message == "Test error"
        assert error.tip == "Try this fix"

    def test_show_without_tip(self) -> None:
        """Test show() method without tip."""
        error = ClickExtendedError("Test error")
        output = StringIO()
        error.show(file=output)

        result = output.getvalue()
        assert "Error: Test error" in result
        assert "Tip:" not in result

    def test_show_with_tip(self) -> None:
        """Test show() method with tip."""
        error = ClickExtendedError("Test error", tip="Try this fix")
        output = StringIO()
        error.show(file=output)

        result = output.getvalue()
        assert "Error: Test error" in result
        assert "Tip: Try this fix" in result

    def test_show_defaults_to_stderr(self) -> None:
        """Test show() uses sys.stderr when no file provided."""
        error = ClickExtendedError("Test error")

        with patch("click_extended.errors.echo") as mock_echo:
            error.show()
            assert mock_echo.call_count >= 1
            # Check that first call used sys.stderr
            call_kwargs = mock_echo.call_args_list[0][1]
            assert call_kwargs["file"] == sys.stderr


class TestContextAwareError:
    """Test ContextAwareError class."""

    def test_init_without_context(self) -> None:
        """Test creating error outside Click context."""
        error = ContextAwareError("Test error")
        assert error.message == "Test error"
        assert error.context is None
        assert error._node_name == "unknown"

    def test_init_with_context(self) -> None:
        """Test creating error inside Click context."""

        @click.command()
        def dummy() -> None:
            error = ContextAwareError("Test error")
            assert error.context is not None
            assert error._node_name == "unknown"  # No click_extended meta

        runner = click.testing.CliRunner()
        result = runner.invoke(dummy, [])

    def test_resolve_node_name_with_child(self) -> None:
        """Test _resolve_node_name() with child node in context."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_child = Mock()
            mock_child.name = "test_child"
            ctx.meta["click_extended"] = {"child_node": mock_child}

            error = ContextAwareError("Test error")
            assert error._node_name == "test_child"

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_resolve_node_name_with_parent(self) -> None:
        """Test _resolve_node_name() with parent node in context."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.name = "test_parent"
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = ContextAwareError("Test error")
            assert error._node_name == "test_parent"

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_resolve_node_name_with_root(self) -> None:
        """Test _resolve_node_name() with root node in context."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_root = Mock()
            mock_root.name = "test_root"
            ctx.meta["click_extended"] = {"root_node": mock_root}

            error = ContextAwareError("Test error")
            assert error._node_name == "test_root"

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_show_without_context(self) -> None:
        """Test show() falls back to base implementation without context."""
        error = ContextAwareError("Test error", tip="Try this")
        output = StringIO()
        error.show(file=output)

        result = output.getvalue()
        assert "Error: Test error" in result
        assert "Tip: Try this" in result

    def test_show_with_context(self) -> None:
        """Test show() uses Click formatting with context."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            error = ContextAwareError("Test error", tip="Try this")
            output = StringIO()
            error.show(file=output)

            result = output.getvalue()
            assert "Usage:" in result
            assert "ContextAwareError (unknown): Test error" in result
            assert "Tip: Try this" in result

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_show_with_help_option(self) -> None:
        """Test show() includes help hint when help option exists."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            error = ContextAwareError("Test error")
            output = StringIO()
            error.show(file=output)

            result = output.getvalue()
            assert "Try" in result
            assert "--help" in result

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])


class TestMissingValueError:
    """Test MissingValueError class."""

    def test_init_without_context(self) -> None:
        """Test creating MissingValueError without context."""
        error = MissingValueError()
        assert error.message == "Value not provided."
        assert error.tip is not None and "Provide a value" in error.tip

    def test_tip_for_option_parent(self) -> None:
        """Test _tip_for_parent() with Option parent."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.__class__.__name__ = "Option"
            mock_parent.name = "test_option"
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = MissingValueError()
            assert error.tip is not None and "--test-option" in error.tip

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_tip_for_argument_parent(self) -> None:
        """Test _tip_for_parent() with Argument parent."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.__class__.__name__ = "Argument"
            mock_parent.name = "test_arg"
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = MissingValueError()
            assert error.tip is not None and "test_arg argument" in error.tip

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_tip_for_env_parent(self) -> None:
        """Test _tip_for_parent() with Env parent."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.__class__.__name__ = "Env"
            mock_parent.name = "test_env"
            mock_parent.env_name = "TEST_ENV"
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = MissingValueError()
            assert error.tip is not None and "TEST_ENV" in error.tip

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_tip_for_env_parent_without_env_name(self) -> None:
        """Test _tip_for_parent() with Env parent without env_name."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.__class__.__name__ = "Env"
            mock_parent.name = "test_env"
            del mock_parent.env_name
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = MissingValueError()
            assert (
                error.tip is not None and "TEST_ENV" in error.tip
            )  # Uses name.upper()

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])

    def test_tip_for_unknown_parent(self) -> None:
        """Test _tip_for_parent() with unknown parent type."""

        @click.command()
        @click.pass_context
        def dummy(ctx: click.Context) -> None:
            mock_parent = Mock()
            mock_parent.__class__.__name__ = "UnknownType"
            mock_parent.name = "unknown"
            ctx.meta["click_extended"] = {"parent_node": mock_parent}

            error = MissingValueError()
            assert error.tip is not None and "Provide a value" in error.tip

        runner = click.testing.CliRunner()
        runner.invoke(dummy, [])


class TestNoRootError:
    """Test NoRootError class."""

    def test_init_default_tip(self) -> None:
        """Test NoRootError with default tip."""
        error = NoRootError()
        assert "No root node" in error.message
        assert error.tip is not None and "@click_extended.root()" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test NoRootError with custom tip."""
        error = NoRootError(tip="Custom tip")
        assert error.tip == "Custom tip"


class TestNoParentError:
    """Test NoParentError class."""

    def test_init_default_tip(self) -> None:
        """Test NoParentError with default tip."""
        error = NoParentError("child1")
        assert "child1" in error.message
        assert error.tip is not None and "parent node" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test NoParentError with custom tip."""
        error = NoParentError("child1", tip="Custom tip")
        assert error.tip == "Custom tip"


class TestRootExistsError:
    """Test RootExistsError class."""

    def test_init_default_tip(self) -> None:
        """Test RootExistsError with default tip."""
        error = RootExistsError()
        assert "already been defined" in error.message
        assert error.tip is not None and "Only one @root()" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test RootExistsError with custom tip."""
        error = RootExistsError(tip="Custom tip")
        assert error.tip == "Custom tip"


class TestParentExistsError:
    """Test ParentExistsError class."""

    def test_init_default_tip(self) -> None:
        """Test ParentExistsError with default tip."""
        error = ParentExistsError("duplicate")
        assert "duplicate" in error.message
        assert error.tip is not None and "must be unique" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test ParentExistsError with custom tip."""
        error = ParentExistsError("duplicate", tip="Custom tip")
        assert error.tip == "Custom tip"


class TestTypeMismatchError:
    """Test TypeMismatchError class."""

    def test_init_with_default_tip(self) -> None:
        """Test TypeMismatchError with generated tip."""
        error = TypeMismatchError(
            child_name="child1",
            parent_name="parent1",
            parent_type="list",
            supported_types=["str", "int"],
        )
        assert "child1" in error.message
        assert "parent1" in error.message
        assert "list" in error.message
        assert error.tip is not None
        assert "<str>" in error.tip
        assert "<int>" in error.tip

    def test_init_with_custom_tip(self) -> None:
        """Test TypeMismatchError with custom tip."""
        error = TypeMismatchError(
            child_name="child1",
            parent_name="parent1",
            parent_type="list",
            supported_types=["str"],
            tip="Custom tip",
        )
        assert error.tip == "Custom tip"


class TestNameExistsError:
    """Test NameExistsError class."""

    def test_init_default_tip(self) -> None:
        """Test NameExistsError with default tip."""
        error = NameExistsError("duplicate_name")
        assert "duplicate_name" in error.message
        assert error.tip is not None and "must be unique" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test NameExistsError with custom tip."""
        error = NameExistsError("duplicate_name", tip="Custom tip")
        assert error.tip == "Custom tip"


class TestUnhandledTypeError:
    """Test UnhandledTypeError class."""

    def test_init_with_implemented_handlers(self) -> None:
        """Test UnhandledTypeError with implemented handlers."""
        error = UnhandledTypeError(
            child_name="child1",
            value_type="list",
            implemented_handlers=["str", "int"],
        )
        assert "child1" in error.message
        assert "list" in error.message
        assert error.tip is not None
        assert "'str'" in error.tip
        assert "'int'" in error.tip

    def test_init_with_empty_handlers(self) -> None:
        """Test UnhandledTypeError with no implemented handlers."""
        error = UnhandledTypeError(
            child_name="child1",
            value_type="list",
            implemented_handlers=[],
        )
        assert error.tip is not None
        assert "No handlers are implemented" in error.tip
        assert "handle_all()" in error.tip

    def test_init_with_custom_tip(self) -> None:
        """Test UnhandledTypeError with custom tip."""
        error = UnhandledTypeError(
            child_name="child1",
            value_type="list",
            implemented_handlers=["str"],
            tip="Custom tip",
        )
        assert error.tip == "Custom tip"


class TestProcessError:
    """Test ProcessError class."""

    def test_init_without_tip(self) -> None:
        """Test ProcessError without tip."""
        error = ProcessError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.tip is None

    def test_init_with_tip(self) -> None:
        """Test ProcessError with tip."""
        error = ProcessError("Something went wrong", tip="Try this")
        assert error.tip == "Try this"


class TestInvalidHandlerError:
    """Test InvalidHandlerError class."""

    def test_init_without_tip(self) -> None:
        """Test InvalidHandlerError without tip."""
        error = InvalidHandlerError("Handler returned None")
        assert error.message == "Handler returned None"
        assert error.tip is None

    def test_init_with_tip(self) -> None:
        """Test InvalidHandlerError with tip."""
        error = InvalidHandlerError(
            "Handler returned None", tip="Return a value"
        )
        assert error.tip == "Return a value"


class TestInternalError:
    """Test InternalError class."""

    def test_init_default_tip(self) -> None:
        """Test InternalError with default tip."""
        error = InternalError("Unexpected state")
        assert error.message == "Unexpected state"
        assert error.tip is not None and "bug in click-extended" in error.tip

    def test_init_custom_tip(self) -> None:
        """Test InternalError with custom tip."""
        error = InternalError("Unexpected state", tip="Custom tip")
        assert error.tip == "Custom tip"
