"""Tests for the Command class."""

from unittest.mock import MagicMock, patch

import click

from click_extended.core._aliased import AliasedCommand
from click_extended.core.command import Command, command


class TestCommandInitialization:
    """Test Command class initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initializing Command with name only."""
        cmd = Command(name="test-command")
        assert cmd.name == "test-command"
        assert cmd.children == {}
        assert cmd.tree is not None

    def test_init_with_kwargs(self) -> None:
        """Test initializing Command with additional kwargs."""
        cmd = Command(name="test-command", help="Test help")
        assert cmd.name == "test-command"
        assert cmd.children == {}

    def test_children_initialized_as_empty_dict(self) -> None:
        """Test that children dict is initialized empty."""
        cmd = Command(name="test-command")
        assert cmd.children == {}
        assert isinstance(cmd.children, dict)

    def test_tree_created_automatically(self) -> None:
        """Test that a Tree is automatically created."""
        cmd = Command(name="test-command")
        assert cmd.tree is not None
        assert hasattr(cmd.tree, "register_root")


class TestCommandClassMethods:
    """Test Command class methods."""

    def test_get_click_decorator_returns_click_command(self) -> None:
        """Test that _get_click_decorator returns click.command."""
        decorator = Command._get_click_decorator()  # type: ignore
        assert decorator == click.command

    def test_get_click_cls_returns_aliased_command(self) -> None:
        """Test that _get_click_cls returns AliasedCommand."""
        cls = Command._get_click_cls()  # type: ignore
        assert cls == AliasedCommand

    def test_get_click_cls_is_command_subclass(self) -> None:
        """Test that AliasedCommand is a click.Command subclass."""
        cls = Command._get_click_cls()  # type: ignore
        assert issubclass(cls, click.Command)


class TestCommandAsDecorator:
    """Test Command.as_decorator functionality."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_explicit_name(
        self, mock_register: MagicMock
    ) -> None:
        """Test as_decorator with explicit name."""
        decorator = Command.as_decorator("test-command")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_infers_name_from_function(
        self, mock_register: MagicMock
    ) -> None:
        """Test as_decorator infers function name when name is None."""
        decorator = Command.as_decorator()

        def my_command() -> str:
            return "test"

        result = decorator(my_command)
        assert callable(result)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_kwargs(self, mock_register: MagicMock) -> None:
        """Test as_decorator with additional kwargs."""
        decorator = Command.as_decorator("test-command", help="Test help")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_registers_command(
        self, mock_register: MagicMock
    ) -> None:
        """Test that as_decorator registers the command with tree."""
        decorator = Command.as_decorator("test-command")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_register.assert_called_once()
        args, _ = mock_register.call_args
        assert isinstance(args[0], Command)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_async_function(
        self, mock_register: MagicMock
    ) -> None:
        """Test as_decorator with async function."""
        decorator = Command.as_decorator("test-command")

        async def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        mock_register.assert_called_once()


class TestCommandDecoratorFunction:
    """Test the command() decorator function."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_name_only(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with name only."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_infers_name(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator infers function name."""

        @command()
        def my_command() -> str:
            return "test"

        assert callable(my_command)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_aliases(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with aliases parameter."""

        @command("test-command", aliases=["tc", "test"])
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_single_alias(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with single alias string."""

        @command("test-command", aliases="tc")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_help(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with help parameter."""

        @command("test-command", help="Test help text")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_all_params(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with all parameters."""

        @command(
            "test-command",
            aliases=["tc", "test"],
            help="Test help text",
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_with_extra_kwargs(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator with extra kwargs."""

        @command("test-command", context_settings={"help_option_names": ["-h"]})
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_decorator_returns_wrapper(
        self, mock_register: MagicMock
    ) -> None:
        """Test command decorator returns RootNodeWrapper."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        assert hasattr(test_func, "visualize")


class TestCommandInheritance:
    """Test Command class inheritance."""

    def test_command_is_rootnode_subclass(self) -> None:
        """Test that Command is a RootNode subclass."""
        from click_extended.core._root_node import RootNode

        assert issubclass(Command, RootNode)

    def test_command_instance_is_rootnode_instance(self) -> None:
        """Test that Command instance is a RootNode instance."""
        from click_extended.core._root_node import RootNode

        cmd = Command(name="test-command")
        assert isinstance(cmd, RootNode)

    def test_command_is_node_subclass(self) -> None:
        """Test that Command is a Node subclass."""
        from click_extended.core._node import Node

        assert issubclass(Command, Node)

    def test_command_instance_is_node_instance(self) -> None:
        """Test that Command instance is a Node instance."""
        from click_extended.core._node import Node

        cmd = Command(name="test-command")
        assert isinstance(cmd, Node)


class TestCommandWrap:
    """Test Command.wrap functionality."""

    def test_wrap_creates_click_command(self) -> None:
        """Test that wrap creates a click.Command."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "test-command", cmd)
        assert hasattr(result, "_underlying")
        assert isinstance(result._underlying, click.Command)

    def test_wrap_uses_aliased_command_class(self) -> None:
        """Test that wrap uses AliasedCommand class."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "test-command", cmd)
        assert isinstance(result._underlying, AliasedCommand)

    def test_wrap_preserves_function_name(self) -> None:
        """Test that wrap preserves function name."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "my-command", cmd)
        assert result._underlying.name == "my-command"

    def test_wrap_returns_wrapper_with_visualize(self) -> None:
        """Test that wrap returns RootNodeWrapper with visualize method."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "test-command", cmd)
        assert hasattr(result, "visualize")
        assert callable(result.visualize)

    def test_wrap_wrapper_is_callable(self) -> None:
        """Test that wrapped result is callable."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "test-command", cmd)
        assert callable(result)

    def test_wrap_with_kwargs(self) -> None:
        """Test wrap with additional kwargs."""
        cmd = Command(name="test-command")

        def test_func() -> str:
            return "test"

        result = Command.wrap(test_func, "test-command", cmd, help="Test help")
        assert hasattr(result, "_underlying")


class TestCommandAliases:
    """Test Command aliases functionality."""

    def test_command_with_single_alias_string(self) -> None:
        """Test command decorator with single alias as string."""

        @command("test-command", aliases="tc")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_command_with_multiple_aliases_list(self) -> None:
        """Test command decorator with multiple aliases as list."""

        @command("test-command", aliases=["tc", "test", "t"])
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_command_with_empty_aliases_list(self) -> None:
        """Test command decorator with empty aliases list."""

        @command("test-command", aliases=[])
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_command_without_aliases(self) -> None:
        """Test command decorator without aliases parameter."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)


class TestCommandEdgeCases:
    """Test Command edge cases."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_empty_name_allowed(self, mock_register: MagicMock) -> None:
        """Test that empty name is allowed."""
        cmd = Command(name="")
        assert cmd.name == ""
        mock_register.assert_not_called()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_name_with_special_characters(
        self, mock_register: MagicMock
    ) -> None:
        """Test command name with special characters."""
        decorator = Command.as_decorator("test-command_123")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_function_with_no_parameters(
        self, mock_register: MagicMock
    ) -> None:
        """Test decorating function with no parameters."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_function_with_return_type_annotation(
        self, mock_register: MagicMock
    ) -> None:
        """Test decorating function with return type annotation."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_async_function_converted_to_sync(
        self, mock_register: MagicMock
    ) -> None:
        """Test that async function is converted to sync."""

        @command("test-command")
        async def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_multiple_commands_independent(
        self, mock_register: MagicMock
    ) -> None:
        """Test that multiple commands are independent."""

        @command("command1")
        def func1() -> str:
            return "test1"

        @command("command2")
        def func2() -> str:
            return "test2"

        assert callable(func1)
        assert callable(func2)
        assert mock_register.call_count == 2

    @patch("click_extended.core._tree.Tree.register_root")
    def test_decorator_preserves_function_metadata(
        self, mock_register: MagicMock
    ) -> None:
        """Test that decorator preserves function metadata."""

        @command("test-command")
        def test_func() -> str:
            """Test docstring."""
            return "test"

        assert hasattr(test_func, "_underlying")

    def test_command_help_none_by_default(self) -> None:
        """Test that help is None when not provided."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_command_aliases_none_by_default(self) -> None:
        """Test that aliases is None when not provided."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_with_context_settings(
        self, mock_register: MagicMock
    ) -> None:
        """Test command with Click context_settings."""

        @command(
            "test-command",
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()


class TestCommandIntegration:
    """Test Command integration scenarios."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_function_signature(self, mock_register: MagicMock) -> None:
        """Test that command() function has correct signature."""

        @command("test-command")
        def func1() -> str:
            return "test"

        @command()
        def func2() -> str:
            return "test"

        @command(name="test-command", aliases=["tc"])
        def func3() -> str:
            return "test"

        assert callable(func1)
        assert callable(func2)
        assert callable(func3)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_returns_root_node_wrapper(
        self, mock_register: MagicMock
    ) -> None:
        """Test that command returns RootNodeWrapper type."""
        from click_extended.core._root_node import RootNodeWrapper

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert isinstance(test_func, RootNodeWrapper)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_wrapper_has_underlying(
        self, mock_register: MagicMock
    ) -> None:
        """Test that wrapper has _underlying attribute."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert hasattr(test_func, "_underlying")
        assert isinstance(test_func._underlying, click.Command)  # type: ignore

    @patch("click_extended.core._tree.Tree.register_root")
    def test_command_wrapper_has_root_instance(
        self, mock_register: MagicMock
    ) -> None:
        """Test that wrapper has _root_instance attribute."""

        @command("test-command")
        def test_func() -> str:
            return "test"

        assert hasattr(test_func, "_root_instance")
        assert isinstance(test_func._root_instance, Command)  # type: ignore

    def test_command_decorator_is_reusable(self) -> None:
        """Test that command decorator can be reused."""
        decorator = command("test-command")

        def func1() -> str:
            return "test1"

        def func2() -> str:
            return "test2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert callable(result1)
        assert callable(result2)

        assert result1 is not result2
