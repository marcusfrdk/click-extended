"""Tests for the Group class."""

from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

from click_extended.core._aliased import AliasedGroup
from click_extended.core.command import Command, command
from click_extended.core.group import Group, GroupWrapper, group
from click_extended.core.option import option


class TestGroupInitialization:
    """Test Group class initialization."""

    def test_init_with_name_only(self) -> None:
        """Test initializing Group with name only."""
        grp = Group(name="test-group")
        assert grp.name == "test-group"
        assert grp.children == {}
        assert grp.tree is not None

    def test_init_with_kwargs(self) -> None:
        """Test initializing Group with additional kwargs."""
        grp = Group(name="test-group", help="Test help")
        assert grp.name == "test-group"
        assert grp.children == {}

    def test_children_initialized_as_empty_dict(self) -> None:
        """Test that children dict is initialized empty."""
        grp = Group(name="test-group")
        assert grp.children == {}
        assert isinstance(grp.children, dict)

    def test_tree_created_automatically(self) -> None:
        """Test that a Tree is automatically created."""
        grp = Group(name="test-group")
        assert grp.tree is not None
        assert hasattr(grp.tree, "register_root")


class TestGroupClassMethods:
    """Test Group class methods."""

    def test_get_click_decorator_returns_click_group(self) -> None:
        """Test that _get_click_decorator returns click.group."""
        decorator = Group._get_click_decorator()  # type: ignore
        assert decorator == click.group

    def test_get_click_cls_returns_aliased_group(self) -> None:
        """Test that _get_click_cls returns AliasedGroup."""
        cls = Group._get_click_cls()  # type: ignore
        assert cls == AliasedGroup

    def test_get_click_cls_is_group_subclass(self) -> None:
        """Test that AliasedGroup is a click.Group subclass."""
        cls = Group._get_click_cls()  # type: ignore
        assert issubclass(cls, click.Group)


class TestGroupAsDecorator:
    """Test Group.as_decorator functionality."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_explicit_name(
        self, mock_register: MagicMock
    ) -> None:
        """Test as_decorator with explicit name."""
        decorator = Group.as_decorator("test-group")

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
        decorator = Group.as_decorator()

        def my_group() -> str:
            return "test"

        result = decorator(my_group)
        assert callable(result)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_kwargs(self, mock_register: MagicMock) -> None:
        """Test as_decorator with additional kwargs."""
        decorator = Group.as_decorator("test-group", help="Test help")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_registers_group(
        self, mock_register: MagicMock
    ) -> None:
        """Test that as_decorator registers the group with tree."""
        decorator = Group.as_decorator("test-group")

        def test_func() -> str:
            return "test"

        decorator(test_func)
        mock_register.assert_called_once()
        args, _ = mock_register.call_args
        assert isinstance(args[0], Group)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_as_decorator_with_async_function(
        self, mock_register: MagicMock
    ) -> None:
        """Test as_decorator with async function."""
        decorator = Group.as_decorator("test-group")

        async def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)
        mock_register.assert_called_once()


class TestGroupDecoratorFunction:
    """Test the group() decorator function."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_name_only(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator with name only."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_infers_name(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator infers function name."""

        @group()
        def my_group() -> str:
            return "test"

        assert callable(my_group)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_aliases(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator with aliases parameter."""

        @group("test-group", aliases=["tg", "test"])
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_single_alias(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator with single alias string."""

        @group("test-group", aliases="tg")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_help(self, mock_register: MagicMock) -> None:
        """Test group decorator with help parameter."""

        @group("test-group", help="Test help text")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_all_params(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator with all parameters."""

        @group(
            "test-group",
            aliases=["tg", "test"],
            help="Test help text",
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_with_extra_kwargs(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator with extra kwargs."""

        @group("test-group", context_settings={"help_option_names": ["-h"]})
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_decorator_returns_wrapper(
        self, mock_register: MagicMock
    ) -> None:
        """Test group decorator returns GroupWrapper."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        assert hasattr(test_func, "visualize")
        assert hasattr(test_func, "add")


class TestGroupInheritance:
    """Test Group class inheritance."""

    def test_group_is_rootnode_subclass(self) -> None:
        """Test that Group is a RootNode subclass."""
        from click_extended.core._root_node import RootNode

        assert issubclass(Group, RootNode)

    def test_group_instance_is_rootnode_instance(self) -> None:
        """Test that Group instance is a RootNode instance."""
        from click_extended.core._root_node import RootNode

        grp = Group(name="test-group")
        assert isinstance(grp, RootNode)

    def test_group_is_node_subclass(self) -> None:
        """Test that Group is a Node subclass."""
        from click_extended.core._node import Node

        assert issubclass(Group, Node)

    def test_group_instance_is_node_instance(self) -> None:
        """Test that Group instance is a Node instance."""
        from click_extended.core._node import Node

        grp = Group(name="test-group")
        assert isinstance(grp, Node)


class TestGroupWrap:
    """Test Group.wrap functionality."""

    def test_wrap_creates_click_group(self) -> None:
        """Test that wrap creates a click.Group."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert hasattr(result, "_underlying")
        assert isinstance(result._underlying, click.Group)  # type: ignore

    def test_wrap_uses_aliased_group_class(self) -> None:
        """Test that wrap uses AliasedGroup class."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert isinstance(result._underlying, AliasedGroup)  # type: ignore

    def test_wrap_preserves_function_name(self) -> None:
        """Test that wrap preserves function name."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "my-group", grp)
        assert result._underlying.name == "my-group"  # type: ignore

    def test_wrap_returns_group_wrapper(self) -> None:
        """Test that wrap returns GroupWrapper."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert isinstance(result, GroupWrapper)

    def test_wrap_wrapper_has_visualize(self) -> None:
        """Test that wrapped result has visualize method."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert hasattr(result, "visualize")
        assert callable(result.visualize)

    def test_wrap_wrapper_has_add(self) -> None:
        """Test that wrapped result has add method."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert hasattr(result, "add")
        assert callable(result.add)

    def test_wrap_wrapper_is_callable(self) -> None:
        """Test that wrapped result is callable."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp)
        assert callable(result)

    def test_wrap_with_kwargs(self) -> None:
        """Test wrap with additional kwargs."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        result = Group.wrap(test_func, "test-group", grp, help="Test help")
        assert hasattr(result, "_underlying")


class TestGroupWrapper:
    """Test GroupWrapper functionality."""

    def test_wrapper_delegates_to_underlying(self) -> None:
        """Test that wrapper delegates to underlying group."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)
        assert hasattr(wrapper, "_underlying")
        assert isinstance(wrapper._underlying, click.Group)  # type: ignore

    def test_wrapper_has_visualize_method(self) -> None:
        """Test that wrapper has visualize method."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)
        assert hasattr(wrapper, "visualize")
        assert callable(wrapper.visualize)

    def test_wrapper_has_add_method(self) -> None:
        """Test that wrapper has add method."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)
        assert hasattr(wrapper, "add")
        assert callable(wrapper.add)

    def test_wrapper_is_callable(self) -> None:
        """Test that wrapper is callable."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)
        assert callable(wrapper)

    def test_wrapper_add_returns_self(self) -> None:
        """Test that add method returns self for chaining."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)

        cmd = Command(name="sub-command")

        def cmd_func() -> str:
            return "cmd"

        cmd_wrapper = Command.wrap(cmd_func, "sub-command", cmd)

        result = wrapper.add(cmd_wrapper)
        assert result is wrapper

    def test_wrapper_add_accepts_command(self) -> None:
        """Test that add method accepts Command wrapper."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)

        from click_extended.core.command import Command

        cmd = Command(name="sub-command")

        def cmd_func() -> str:
            return "cmd"

        cmd_wrapper = Command.wrap(cmd_func, "sub-command", cmd)

        wrapper.add(cmd_wrapper)
        assert "sub-command" in wrapper._underlying.commands  # type: ignore

    def test_wrapper_add_accepts_group(self) -> None:
        """Test that add method accepts Group wrapper."""
        parent_grp = Group(name="parent-group")

        def parent_func() -> str:
            return "parent"

        parent_wrapper = Group.wrap(parent_func, "parent-group", parent_grp)

        sub_grp = Group(name="sub-group")

        def sub_func() -> str:
            return "sub"

        sub_wrapper = Group.wrap(sub_func, "sub-group", sub_grp)

        parent_wrapper.add(sub_wrapper)  # type: ignore

        assert "sub-group" in parent_wrapper._underlying.commands  # type: ignore

    def test_wrapper_add_chaining(self) -> None:
        """Test that add method supports chaining."""
        grp = Group(name="test-group")

        def test_func() -> str:
            return "test"

        wrapper = Group.wrap(test_func, "test-group", grp)

        cmd1 = Command(name="cmd1")

        def cmd1_func() -> str:
            return "cmd1"

        cmd1_wrapper = Command.wrap(cmd1_func, "cmd1", cmd1)

        cmd2 = Command(name="cmd2")

        def cmd2_func() -> str:
            return "cmd2"

        cmd2_wrapper = Command.wrap(cmd2_func, "cmd2", cmd2)

        result = wrapper.add(cmd1_wrapper).add(cmd2_wrapper)
        assert result is wrapper
        assert "cmd1" in wrapper._underlying.commands  # type: ignore
        assert "cmd2" in wrapper._underlying.commands  # type: ignore


class TestGroupAliases:
    """Test Group aliases functionality."""

    def test_group_with_single_alias_string(self) -> None:
        """Test group decorator with single alias as string."""

        @group("test-group", aliases="tg")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_group_with_multiple_aliases_list(self) -> None:
        """Test group decorator with multiple aliases as list."""

        @group("test-group", aliases=["tg", "test", "t"])
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_group_with_empty_aliases_list(self) -> None:
        """Test group decorator with empty aliases list."""

        @group("test-group", aliases=[])
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_group_without_aliases(self) -> None:
        """Test group decorator without aliases parameter."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)


class TestGroupEdgeCases:
    """Test Group edge cases."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_empty_name_allowed(self, mock_register: MagicMock) -> None:
        """Test that empty name is allowed."""
        grp = Group(name="")
        assert grp.name == ""
        mock_register.assert_not_called()

    @patch("click_extended.core._tree.Tree.register_root")
    def test_name_with_special_characters(
        self, mock_register: MagicMock
    ) -> None:
        """Test group name with special characters."""
        decorator = Group.as_decorator("test-group_123")

        def test_func() -> str:
            return "test"

        result = decorator(test_func)
        assert callable(result)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_function_with_no_parameters(
        self, mock_register: MagicMock
    ) -> None:
        """Test decorating function with no parameters."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_function_with_return_type_annotation(
        self, mock_register: MagicMock
    ) -> None:
        """Test decorating function with return type annotation."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_async_function_converted_to_sync(
        self, mock_register: MagicMock
    ) -> None:
        """Test that async function is converted to sync."""

        @group("test-group")
        async def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_multiple_groups_independent(
        self, mock_register: MagicMock
    ) -> None:
        """Test that multiple groups are independent."""

        @group("group1")
        def func1() -> str:
            return "test1"

        @group("group2")
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

        @group("test-group")
        def test_func() -> str:
            """Test docstring."""
            return "test"

        assert hasattr(test_func, "_underlying")

    def test_group_help_none_by_default(self) -> None:
        """Test that help is None when not provided."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    def test_group_aliases_none_by_default(self) -> None:
        """Test that aliases is None when not provided."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert callable(test_func)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_with_context_settings(
        self, mock_register: MagicMock
    ) -> None:
        """Test group with Click context_settings."""

        @group(
            "test-group",
            context_settings={"help_option_names": ["-h", "--help"]},
        )
        def test_func() -> str:
            return "test"

        assert callable(test_func)
        mock_register.assert_called_once()


class TestGroupIntegration:
    """Test Group integration scenarios."""

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_function_signature(self, mock_register: MagicMock) -> None:
        """Test that group() function has correct signature."""

        @group("test-group")
        def func1() -> str:
            return "test"

        @group()
        def func2() -> str:
            return "test"

        @group(name="test-group", aliases=["tg"])
        def func3() -> str:
            return "test"

        assert callable(func1)
        assert callable(func2)
        assert callable(func3)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_returns_group_wrapper(
        self, mock_register: MagicMock
    ) -> None:
        """Test that group returns GroupWrapper type."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert isinstance(test_func, GroupWrapper)

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_wrapper_has_underlying(
        self, mock_register: MagicMock
    ) -> None:
        """Test that wrapper has _underlying attribute."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert hasattr(test_func, "_underlying")
        assert isinstance(test_func._underlying, click.Group)  # type: ignore

    @patch("click_extended.core._tree.Tree.register_root")
    def test_group_wrapper_has_root_instance(
        self, mock_register: MagicMock
    ) -> None:
        """Test that wrapper has _root_instance attribute."""

        @group("test-group")
        def test_func() -> str:
            return "test"

        assert hasattr(test_func, "_root_instance")
        assert isinstance(test_func._root_instance, Group)  # type: ignore

    def test_group_decorator_is_reusable(self) -> None:
        """Test that group decorator can be reused."""
        decorator = group("test-group")

        def func1() -> str:
            return "test1"

        def func2() -> str:
            return "test2"

        result1 = decorator(func1)
        result2 = decorator(func2)

        assert callable(result1)
        assert callable(result2)
        assert result1 is not result2

    def test_group_with_commands_hierarchy(self) -> None:
        """Test building a group with command hierarchy."""
        from click_extended.core.command import Command

        parent_grp = Group(name="parent")

        def parent_func() -> str:
            return "parent"

        parent_wrapper = Group.wrap(parent_func, "parent", parent_grp)

        cmd = Command(name="child")

        def cmd_func() -> str:
            return "child"

        cmd_wrapper = Command.wrap(cmd_func, "child", cmd)

        parent_wrapper.add(cmd_wrapper)

        assert "child" in parent_wrapper._underlying.commands  # type: ignore

    def test_group_with_nested_groups(self) -> None:
        """Test building nested group hierarchy."""
        parent_grp = Group(name="parent")

        def parent_func() -> str:
            return "parent"

        parent_wrapper = Group.wrap(parent_func, "parent", parent_grp)

        child_grp = Group(name="child")

        def child_func() -> str:
            return "child"

        child_wrapper = Group.wrap(child_func, "child", child_grp)

        grandchild_grp = Group(name="grandchild")

        def grandchild_func() -> str:
            return "grandchild"

        grandchild_wrapper = Group.wrap(
            grandchild_func, "grandchild", grandchild_grp
        )

        child_wrapper.add(grandchild_wrapper)  # type: ignore
        parent_wrapper.add(child_wrapper)  # type: ignore

        assert "child" in parent_wrapper._underlying.commands  # type: ignore
        assert "grandchild" in child_wrapper._underlying.commands  # type: ignore


class TestGroupHelpShortcut:
    """Test -h help shortcut functionality for groups."""

    def test_h_flag_shows_help_on_group(self) -> None:
        """Test that -h shows help on groups."""

        @group()
        @option("--verbose", "-v", is_flag=True)
        def cli(verbose: bool) -> None:
            """CLI tool."""
            if verbose:
                print("Verbose mode")

        @command()
        def subcommand() -> None:
            """A subcommand."""
            print("Subcommand executed")

        cli.add(subcommand)

        runner = CliRunner()
        result = runner.invoke(cli, ["-h"])  # type: ignore

        assert result.exit_code == 0
        assert "Show this message and exit" in result.output
        assert "-h, --help" in result.output
        assert "subcommand" in result.output

    def test_h_flag_overridden_on_group(self) -> None:
        """Test that user's -h option overrides help on groups."""

        @group()
        @option("--host", "-h", default="localhost")
        def cli(host: str) -> None:
            """CLI with host option."""
            print(f"Host: {host}")

        @command()
        def subcommand() -> None:
            """A subcommand."""
            print("Subcommand executed")

        cli.add(subcommand)

        runner = CliRunner()

        result = runner.invoke(cli, ["-h", "example.com", "subcommand"])  # type: ignore
        assert result.exit_code == 0
        assert "Host: example.com" in result.output

        result_help = runner.invoke(cli, ["--help"])  # type: ignore
        assert result_help.exit_code == 0
        assert "Show this message and exit" in result_help.output
        assert "-h, --host" in result_help.output

    def test_h_flag_on_nested_groups(self) -> None:
        """Test -h help works on nested groups."""

        @group()
        def main_cli() -> None:
            """Main CLI."""
            pass

        @group()
        def sub_group() -> None:
            """Sub group."""
            pass

        @command()
        def leaf_command() -> None:
            """Leaf command."""
            print("Executed")

        sub_group.add(leaf_command)
        main_cli.add(sub_group)  # type: ignore

        runner = CliRunner()

        result = runner.invoke(main_cli, ["-h"])  # type: ignore
        assert result.exit_code == 0
        assert "-h, --help" in result.output

        result = runner.invoke(main_cli, ["sub_group", "-h"])  # type: ignore
        assert result.exit_code == 0
        assert "-h, --help" in result.output

    def test_h_flag_different_per_command_in_group(self) -> None:
        """Test that -h behavior is independent per command in a group."""

        @group()
        def main_cli() -> None:
            """Main CLI."""
            pass

        @command()
        @option("--name", "-n", default="World")
        def cmd1(name: str) -> None:
            """Command 1."""
            print(f"Cmd1: {name}")

        @command()
        @option("--host", "-h", default="localhost")
        def cmd2(host: str) -> None:
            """Command 2."""
            print(f"Cmd2: {host}")

        main_cli.add(cmd1)
        main_cli.add(cmd2)

        runner = CliRunner()

        result1 = runner.invoke(main_cli, ["cmd1", "-h"])  # type: ignore
        assert result1.exit_code == 0
        assert "Show this message and exit" in result1.output

        result2 = runner.invoke(main_cli, ["cmd2", "-h", "example.com"])  # type: ignore
        assert result2.exit_code == 0
        assert "Cmd2: example.com" in result2.output
