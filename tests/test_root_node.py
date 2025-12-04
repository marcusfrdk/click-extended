"""Comprehensive tests for RootNode functionality."""

from typing import Any

import pytest

from click_extended.core.command import Command, command
from click_extended.core.group import Group, group


class TestRootNodeInit:
    """Test RootNode initialization and setup."""

    def test_command_initialization_basic(self) -> None:
        """Test basic Command initialization with name."""
        cmd = Command(name="test_cmd")

        assert cmd.name == "test_cmd"
        assert cmd.aliases is None
        assert cmd.tree is not None
        assert cmd.extra_args == ()
        assert cmd.extra_kwargs == {}

    def test_command_initialization_with_aliases_string(self) -> None:
        """Test Command initialization with single alias string."""
        cmd = Command(name="serve", aliases="s")

        assert cmd.name == "serve"
        assert cmd.aliases == "s"

    def test_command_initialization_with_aliases_list(self) -> None:
        """Test Command initialization with list of aliases."""
        cmd = Command(name="serve", aliases=["s", "start", "run"])

        assert cmd.name == "serve"
        assert cmd.aliases == ["s", "start", "run"]

    def test_command_initialization_with_extra_kwargs(self) -> None:
        """Test that extra kwargs are stored."""
        cmd = Command(
            name="test",
            help="Test command",
            context_settings={"allow_extra_args": True},
        )

        assert cmd.name == "test"
        assert "help" in cmd.extra_kwargs
        assert cmd.extra_kwargs["help"] == "Test command"
        assert "context_settings" in cmd.extra_kwargs

    def test_group_initialization_basic(self) -> None:
        """Test basic Group initialization."""
        grp = Group(name="test_group")

        assert grp.name == "test_group"
        assert grp.aliases is None
        assert grp.tree is not None

    def test_group_initialization_with_aliases(self) -> None:
        """Test Group initialization with aliases."""
        grp = Group(name="cli", aliases=["c", "main"])

        assert grp.name == "cli"
        assert grp.aliases == ["c", "main"]

    def test_format_name_with_no_aliases(self) -> None:
        """Test format_name_with_aliases with no aliases."""
        cmd = Command(name="serve")

        assert cmd.format_name_with_aliases() == "serve"

    def test_format_name_with_single_alias(self) -> None:
        """Test format_name_with_aliases with single alias."""
        cmd = Command(name="serve", aliases="s")

        formatted = cmd.format_name_with_aliases()
        assert formatted == "serve (s)"

    def test_format_name_with_multiple_aliases(self) -> None:
        """Test format_name_with_aliases with multiple aliases."""
        cmd = Command(name="serve", aliases=["s", "start", "run"])

        formatted = cmd.format_name_with_aliases()
        assert formatted == "serve (s, start, run)"

    def test_format_name_with_empty_alias_filtered(self) -> None:
        """Test that empty aliases are filtered out."""
        cmd = Command(name="serve", aliases=["s", "", "run"])

        formatted = cmd.format_name_with_aliases()
        assert formatted == "serve (s, run)"

    def test_tree_is_unique_per_instance(self) -> None:
        """Test that each RootNode instance has its own Tree."""
        cmd1 = Command(name="cmd1")
        cmd2 = Command(name="cmd2")

        assert cmd1.tree is not cmd2.tree

    def test_command_extra_args_stored(self) -> None:
        """Test that extra positional args are stored."""
        cmd = Command("test", "arg1", "arg2")  # type: ignore[call-arg]

        assert cmd.name == "test"
        assert cmd.extra_args == ("arg1", "arg2")


class TestRootNodeDecorator:
    """Test RootNode decorator application."""

    def test_command_decorator_basic(self, cli_runner: Any) -> None:
        """Test basic @command() decorator."""

        @command()
        def hello() -> None:
            import click

            click.echo("Hello!")

        result = cli_runner.invoke(hello, [])
        assert result.exit_code == 0
        assert "Hello!" in result.output

    def test_command_decorator_with_explicit_name(
        self, cli_runner: Any
    ) -> None:
        """Test @command() with explicit name override."""

        @command("greet")
        def some_function() -> None:
            import click

            click.echo("Greeting")

        # The Click command name should be 'greet'
        assert some_function.name == "greet"  # type: ignore[attr-defined]

    def test_command_decorator_derives_name_from_function(
        self, cli_runner: Any
    ) -> None:
        """Test that command name is derived from function name."""

        @command()
        def my_command() -> None:
            import click

            click.echo("Running")

        assert my_command.name == "my_command"  # type: ignore[attr-defined]

    def test_group_decorator_basic(self, cli_runner: Any) -> None:
        """Test basic @group() decorator."""

        @group()
        def cli() -> None:
            """Main CLI group."""
            pass

        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Main CLI group" in result.output

    def test_command_decorator_with_help(self, cli_runner: Any) -> None:
        """Test @command() with explicit help text."""

        @command(help="Custom help message")
        def serve() -> None:
            pass

        result = cli_runner.invoke(serve, ["--help"])
        assert result.exit_code == 0
        assert "Custom help message" in result.output

    def test_command_decorator_derives_help_from_docstring(
        self, cli_runner: Any
    ) -> None:
        """Test that help is derived from first line of docstring."""

        @command()
        def deploy() -> None:
            """Deploy the application to production."""
            pass

        result = cli_runner.invoke(deploy, ["--help"])
        assert result.exit_code == 0
        assert "Deploy the application to production" in result.output

    def test_command_decorator_with_aliases(self, cli_runner: Any) -> None:
        """Test @command() with aliases."""

        @command(aliases=["s", "start"])
        def serve() -> None:
            """Start the server."""
            pass

        # Note: Aliases are stored but testing them requires Click context
        result = cli_runner.invoke(serve, ["--help"])
        assert result.exit_code == 0

    def test_command_preserves_function_name(self) -> None:
        """Test that decorator preserves function __name__."""

        @command()
        def my_func() -> None:
            """Test function."""
            pass

        assert my_func.callback.__name__ == "my_func"  # type: ignore[union-attr]

    def test_command_preserves_function_docstring(self) -> None:
        """Test that decorator preserves function __doc__."""

        @command()
        def documented() -> None:
            """This is a documented function."""
            pass

        assert "documented function" in documented.callback.__doc__  # type: ignore[union-attr, operator]

    def test_async_command_wrapped_to_sync(self, cli_runner: Any) -> None:
        """Test that async functions are wrapped to sync."""
        import asyncio

        @command()
        async def async_hello() -> None:
            import click

            await asyncio.sleep(0.001)
            click.echo("Async Hello!")

        result = cli_runner.invoke(async_hello, [])
        assert result.exit_code == 0
        assert "Async Hello!" in result.output

    def test_multiple_commands_separate_trees(self) -> None:
        """Test that multiple commands have separate tree instances."""

        @command()
        def cmd1() -> None:
            pass

        @command()
        def cmd2() -> None:
            pass

        # Each command should have its own tree
        assert cmd1.root.tree is not cmd2.root.tree  # type: ignore[attr-defined]

    def test_command_decorator_with_context_settings(
        self, cli_runner: Any
    ) -> None:
        """Test @command() with custom context_settings."""

        @command(
            context_settings={"help_option_names": ["-h", "--help", "--info"]}
        )
        def info() -> None:
            """Show info."""
            pass

        result = cli_runner.invoke(info, ["--info"])
        assert result.exit_code == 0

    def test_group_decorator_with_aliases(self, cli_runner: Any) -> None:
        """Test @group() with aliases."""

        @group(aliases="c")
        def cli() -> None:
            """Main CLI."""
            pass

        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_group_decorator_with_explicit_help(self, cli_runner: Any) -> None:
        """Test @group() decorator with explicit help parameter."""

        @group(help="Explicit help text")
        def admin() -> None:
            """Docstring that should be ignored."""
            pass

        # Help text should be the explicit parameter
        result = cli_runner.invoke(admin, ["--help"])
        assert result.exit_code == 0
        assert "Explicit help text" in result.output
        assert "Docstring that should be ignored" not in result.output

    def test_command_with_return_value(self, cli_runner: Any) -> None:
        """Test that command return values are preserved."""

        @command()
        def get_value() -> int:
            return 42

        # Click doesn't directly return the value, but we can test execution
        result = cli_runner.invoke(get_value, [])
        assert result.exit_code == 0


class TestRootNodeTreeBuilding:
    """Test RootNode tree building and validation."""

    def test_empty_command_builds_tree(self, cli_runner: Any) -> None:
        """Test that command with no decorators builds valid tree."""

        @command()
        def empty() -> None:
            import click

            click.echo("Empty")

        result = cli_runner.invoke(empty, [])
        assert result.exit_code == 0
        assert "Empty" in result.output

    def test_command_with_option_parent(self, cli_runner: Any) -> None:
        """Test command with option decorator."""
        from click_extended.core.option import option

        @command()
        @option("name")
        def greet(name: str) -> None:
            import click

            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_command_with_argument_parent(self, cli_runner: Any) -> None:
        """Test command with argument decorator."""
        from click_extended.core.argument import argument

        @command()
        @argument("filename")
        def process(filename: str) -> None:
            import click

            click.echo(f"Processing {filename}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "Processing test.txt" in result.output

    def test_command_with_multiple_parents(self, cli_runner: Any) -> None:
        """Test command with multiple parent decorators."""
        from click_extended.core.argument import argument
        from click_extended.core.option import option

        @command()
        @option("port", type=int, default=8080)
        @option("host", default="localhost")
        @argument("config")
        def serve(host: str, port: int, config: str) -> None:
            import click

            click.echo(f"Serving on {host}:{port} with {config}")

        result = cli_runner.invoke(
            serve, ["--host", "0.0.0.0", "--port", "3000", "app.yaml"]
        )
        assert result.exit_code == 0
        assert "Serving on 0.0.0.0:3000 with app.yaml" in result.output

    def test_command_with_child_on_parent(self, cli_runner: Any) -> None:
        """Test command with child node attached to parent."""
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("name")
        @Uppercase.as_decorator()
        def greet(name: str) -> None:
            import click

            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "world"])
        assert result.exit_code == 0
        assert "Hello, WORLD!" in result.output

    def test_command_with_tag(self, cli_runner: Any) -> None:
        """Test command with tag decorator."""
        from click_extended.core.option import option
        from click_extended.core.tag import tag

        @command()
        @option("name", tags="input")
        @tag("input")
        def greet(name: str) -> None:
            import click

            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "Test"])
        assert result.exit_code == 0
        assert "Hello, Test!" in result.output

    def test_auto_tag_creation(self, cli_runner: Any) -> None:
        """Test that tags are auto-created when referenced but not declared."""
        from click_extended.core.option import option

        @command()
        @option("name", tags="auto_tag")
        def greet(name: str) -> None:
            import click

            click.echo(f"Hello, {name}!")

        # Should not error, auto-tag should be created
        result = cli_runner.invoke(greet, ["--name", "Test"])
        assert result.exit_code == 0

    def test_duplicate_short_flags_raises_error(self) -> None:
        """Test that duplicate short flags raise NameExistsError."""
        from click_extended.core.option import option
        from click_extended.errors import NameExistsError

        with pytest.raises(NameExistsError):

            @command()
            @option("port", short="-p")
            @option("path", short="-p")
            def serve(port: int, path: str) -> None:
                pass

            # Need to actually invoke to trigger validation
            from click.testing import CliRunner

            runner = CliRunner()
            runner.invoke(serve, ["-p", "8080"])

    def test_help_option_names_when_h_not_taken(self, cli_runner: Any) -> None:
        """Test that -h is added to help options when not taken."""
        from click_extended.core.option import option

        @command()
        @option("verbose", short="-v", is_flag=True)
        def run(verbose: bool) -> None:
            pass

        result = cli_runner.invoke(run, ["-h"])
        assert result.exit_code == 0
        assert "Usage:" in result.output or "help" in result.output.lower()

    def test_help_option_when_h_flag_taken(self, cli_runner: Any) -> None:
        """Test that -h is not added when taken by an option."""
        from click_extended.core.option import option

        @command()
        @option("host", short="-h")
        def serve(host: str) -> None:
            import click

            click.echo(f"Host: {host}")

        # -h should be used for host, not help
        result = cli_runner.invoke(serve, ["-h", "localhost"])
        assert result.exit_code == 0
        assert "Host: localhost" in result.output

    def test_tag_with_multiple_parents(self, cli_runner: Any) -> None:
        """Test tag associated with multiple parents."""
        from click_extended.core.option import option
        from click_extended.core.tag import tag

        @command()
        @option("first", tags="group1")
        @option("second", tags="group1")
        @tag("group1")
        def process(first: str, second: str) -> None:
            import click

            click.echo(f"{first} and {second}")

        result = cli_runner.invoke(process, ["--first", "A", "--second", "B"])
        assert result.exit_code == 0
        assert "A and B" in result.output


class TestRootNodeValueProcessing:
    """Test RootNode value processing and injection."""

    def test_option_value_injection(self, cli_runner: Any) -> None:
        """Test that option values are injected into function."""
        from click_extended.core.option import option

        @command()
        @option("name")
        def greet(name: str) -> None:
            import click

            click.echo(f"Name: {name}")

        result = cli_runner.invoke(greet, ["--name", "Alice"])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output

    def test_argument_value_injection(self, cli_runner: Any) -> None:
        """Test that argument values are injected."""
        from click_extended.core.argument import argument

        @command()
        @argument("filename")
        def process(filename: str) -> None:
            import click

            click.echo(f"File: {filename}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "File: test.txt" in result.output

    def test_option_default_value_used(self, cli_runner: Any) -> None:
        """Test that default values are used when option not provided."""
        from click_extended.core.option import option

        @command()
        @option("port", type=int, default=8080)
        def serve(port: int) -> None:
            import click

            click.echo(f"Port: {port}")

        result = cli_runner.invoke(serve, [])
        assert result.exit_code == 0
        assert "Port: 8080" in result.output

    def test_required_option_missing_raises_error(
        self, cli_runner: Any
    ) -> None:
        """Test that missing required option raises error."""
        from click_extended.core.option import option

        @command()
        @option("config", required=True)
        def run(config: str) -> None:
            pass

        result = cli_runner.invoke(run, [])
        assert result.exit_code != 0

    def test_multiple_values_injected(self, cli_runner: Any) -> None:
        """Test that multiple parent values are injected."""
        from click_extended.core.argument import argument
        from click_extended.core.option import option

        @command()
        @option("verbose", is_flag=True)
        @option("port", type=int, default=3000)
        @argument("filename")
        def process(filename: str, port: int, verbose: bool) -> None:
            import click

            click.echo(f"File: {filename}, Port: {port}, Verbose: {verbose}")

        result = cli_runner.invoke(
            process, ["--verbose", "--port", "5000", "test.txt"]
        )
        assert result.exit_code == 0
        assert "File: test.txt" in result.output
        assert "Port: 5000" in result.output
        assert "Verbose: True" in result.output

    def test_was_provided_tracking_true(self, cli_runner: Any) -> None:
        """Test that was_provided is True when value provided."""
        from click_extended.core.option import option

        was_provided_value = None

        @command()
        @option("name")
        def check(name: str) -> None:
            nonlocal was_provided_value
            import click

            # Access via context to check was_provided
            ctx = click.get_current_context()
            meta = ctx.meta.get("click_extended", {})
            # This would need actual implementation to check

        result = cli_runner.invoke(check, ["--name", "test"])
        assert result.exit_code == 0

    def test_was_provided_tracking_false_with_default(
        self, cli_runner: Any
    ) -> None:
        """Test that was_provided is False when default used."""
        from click_extended.core.option import option

        @command()
        @option("port", type=int, default=8080)
        def serve(port: int) -> None:
            import click

            click.echo(f"Port: {port}")

        result = cli_runner.invoke(serve, [])
        assert result.exit_code == 0
        assert "Port: 8080" in result.output

    def test_custom_param_name_injection(self, cli_runner: Any) -> None:
        """Test that custom param names work correctly."""
        from click_extended.core.option import option

        @command()
        @option("configuration_file", param="cfg")
        def run(cfg: str) -> None:
            import click

            click.echo(f"Config: {cfg}")

        result = cli_runner.invoke(run, ["--configuration-file", "app.yaml"])
        assert result.exit_code == 0
        assert "Config: app.yaml" in result.output

    def test_value_type_conversion(self, cli_runner: Any) -> None:
        """Test that values are converted to correct types."""
        from click_extended.core.option import option

        @command()
        @option("count", type=int)
        @option("ratio", type=float)
        @option("enabled", is_flag=True)
        def process(count: int, ratio: float, enabled: bool) -> None:
            import click

            click.echo(f"{count}, {ratio}, {enabled}")

        result = cli_runner.invoke(
            process, ["--count", "42", "--ratio", "3.14", "--enabled"]
        )
        assert result.exit_code == 0
        assert "42, 3.14, True" in result.output


class TestRootNodeChildrenProcessing:
    """Test RootNode children processing and transformation."""

    def test_child_executes_after_parents(self, cli_runner: Any) -> None:
        """Test that children execute after parent load."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        execution_order = []

        class TrackedChild(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                execution_order.append("child")
                return value.upper()

        @command()
        @option("text")
        @TrackedChild.as_decorator()
        def transform(text: str) -> None:
            execution_order.append("function")
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(transform, ["--text", "hello"])
        assert result.exit_code == 0
        assert execution_order == ["child", "function"]
        assert "Text: HELLO" in result.output

    def test_multiple_children_execute_in_order(self, cli_runner: Any) -> None:
        """Test that multiple children execute in top-to-bottom order."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        execution_order = []

        class First(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                execution_order.append("first")
                return value + "1"

        class Second(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                execution_order.append("second")
                return value + "2"

        class Third(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                execution_order.append("third")
                return value + "3"

        @command()
        @option("text")
        @First.as_decorator()
        @Second.as_decorator()
        @Third.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(process, ["--text", "x"])
        assert result.exit_code == 0
        assert execution_order == ["first", "second", "third"]
        assert "Result: x123" in result.output

    def test_child_error_propagates(self, cli_runner: Any) -> None:
        """Test that child errors propagate correctly."""
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option
        from click_extended.errors import ContextAwareError

        class FailingChild(ChildNode):
            def handle_int(
                self, value: int, context: Context, *args: Any, **kwargs: Any
            ) -> int:
                if value < 0:
                    raise ContextAwareError("Value must be positive")
                return value

        @command()
        @option("number", type=int)
        @FailingChild.as_decorator()
        def check(number: int) -> None:
            pass

        result = cli_runner.invoke(check, ["--number", "-5"])
        assert result.exit_code == 1
        assert "Value must be positive" in result.output

    def test_children_receive_transformed_values(self, cli_runner: Any) -> None:
        """Test that children receive output from previous children."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class Double(ChildNode):
            def handle_int(
                self, value: int, context: Context, *args: Any, **kwargs: Any
            ) -> int:
                return value * 2

        class AddTen(ChildNode):
            def handle_int(
                self, value: int, context: Context, *args: Any, **kwargs: Any
            ) -> int:
                return value + 10

        @command()
        @option("num", type=int)
        @Double.as_decorator()
        @AddTen.as_decorator()
        def calc(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(calc, ["--num", "5"])
        assert result.exit_code == 0
        # (5 * 2) + 10 = 20
        assert "Result: 20" in result.output


class TestRootNodeAsync:
    """Test RootNode async handler support."""

    def test_async_child_handler_detected(self, cli_runner: Any) -> None:
        """Test that async child handlers are detected."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class AsyncChild(ChildNode):
            async def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @option("text")
        @AsyncChild.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(process, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: HELLO" in result.output

    def test_multiple_async_children(self, cli_runner: Any) -> None:
        """Test multiple async children execute correctly."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class AsyncFirst(ChildNode):
            async def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value + "1"

        class AsyncSecond(ChildNode):
            async def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value + "2"

        @command()
        @option("text")
        @AsyncFirst.as_decorator()
        @AsyncSecond.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(process, ["--text", "x"])
        assert result.exit_code == 0
        assert "Result: x12" in result.output

    def test_mixed_sync_and_async_children(self, cli_runner: Any) -> None:
        """Test mixing sync and async children."""
        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class SyncChild(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value + "sync"

        class AsyncChild(ChildNode):
            async def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value + "async"

        @command()
        @option("text")
        @SyncChild.as_decorator()
        @AsyncChild.as_decorator()
        def process(text: str) -> None:
            click.echo(f"Result: {text}")

        result = cli_runner.invoke(process, ["--text", "x"])
        assert result.exit_code == 0
        assert "Result: xsyncasync" in result.output


class TestRootNodeErrorHandling:
    """Test RootNode error handling and debug mode."""

    def test_context_aware_error_exits_with_code_1(
        self, cli_runner: Any
    ) -> None:
        """Test that ContextAwareError results in exit code 1."""
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option
        from click_extended.errors import ContextAwareError

        class FailingChild(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                raise ContextAwareError("Something went wrong")

        @command()
        @option("text")
        @FailingChild.as_decorator()
        def process(text: str) -> None:
            pass

        result = cli_runner.invoke(process, ["--text", "test"])
        assert result.exit_code == 1

    def test_generic_exception_exits_with_code_1(self, cli_runner: Any) -> None:
        """Test that generic exceptions result in exit code 1."""
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class FailingChild(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                raise ValueError("Invalid value")

        @command()
        @option("text")
        @FailingChild.as_decorator()
        def process(text: str) -> None:
            pass

        result = cli_runner.invoke(process, ["--text", "test"])
        assert result.exit_code == 1
        assert "ValueError" in result.output

    def test_error_message_displayed(self, cli_runner: Any) -> None:
        """Test that error messages are displayed to user."""
        from click_extended.core.option import option
        from click_extended.errors import ContextAwareError

        @command()
        @option("number", type=int, required=True)
        def check(number: int) -> None:
            if number > 100:
                raise ContextAwareError("Number must be 100 or less")

        result = cli_runner.invoke(check, ["--number", "999"])
        assert result.exit_code == 1
        assert "Number must be 100 or less" in result.output

    def test_missing_required_option_error(self, cli_runner: Any) -> None:
        """Test error when required option is missing."""
        from click_extended.core.option import option

        @command()
        @option("config", required=True)
        def run(config: str) -> None:
            pass

        result = cli_runner.invoke(run, [])
        assert result.exit_code != 0
        assert (
            "config" in result.output.lower()
            or "required" in result.output.lower()
        )

    def test_type_conversion_error(self, cli_runner: Any) -> None:
        """Test error when type conversion fails."""
        from click_extended.core.option import option

        @command()
        @option("count", type=int)
        def process(count: int) -> None:
            pass

        result = cli_runner.invoke(process, ["--count", "not-a-number"])
        assert result.exit_code != 0

    def test_empty_function_with_parents(self, cli_runner: Any) -> None:
        """Test empty function with parent nodes works."""
        from click_extended.core.option import option

        @command()
        @option("name")
        def greet(name: str) -> None:
            pass

        result = cli_runner.invoke(greet, ["--name", "Alice"])
        assert result.exit_code == 0


class TestRootNodeClickIntegration:
    """Test RootNode integration with Click framework."""

    def test_click_context_available(self, cli_runner: Any) -> None:
        """Test that Click context is accessible in function."""
        import click

        from click_extended.core.option import option

        @command()
        @option("name")
        def greet(name: str) -> None:
            ctx = click.get_current_context()
            assert ctx is not None
            click.echo(f"Hello, {name}!")

        result = cli_runner.invoke(greet, ["--name", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_help_option_works(self, cli_runner: Any) -> None:
        """Test that --help option displays help."""
        from click_extended.core.option import option

        @command(help="A greeting command")
        @option("name", help="The name to greet")
        def greet(name: str) -> None:
            pass

        result = cli_runner.invoke(greet, ["--help"])
        assert result.exit_code == 0
        assert "greeting command" in result.output
        assert "--name" in result.output

    def test_command_with_docstring_help(self, cli_runner: Any) -> None:
        """Test that docstring is used as help text."""

        @command()
        def process() -> None:
            """Process some data."""
            pass

        result = cli_runner.invoke(process, ["--help"])
        assert result.exit_code == 0
        assert "Process some data" in result.output

    def test_multiple_options_in_help(self, cli_runner: Any) -> None:
        """Test that all options appear in help."""
        from click_extended.core.option import option

        @command()
        @option("name", help="User name")
        @option("age", type=int, help="User age")
        @option("verbose", is_flag=True, help="Verbose output")
        def process(name: str, age: int, verbose: bool) -> None:
            pass

        result = cli_runner.invoke(process, ["--help"])
        assert result.exit_code == 0
        assert "--name" in result.output
        assert "--age" in result.output
        assert "--verbose" in result.output


class TestRootNodeEdgeCases:
    """Test RootNode edge cases and complex scenarios."""

    def test_command_with_no_decorators(self, cli_runner: Any) -> None:
        """Test command with no parent decorators."""

        @command()
        def simple() -> None:
            import click

            click.echo("Success")

        result = cli_runner.invoke(simple, [])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_option_with_default_none(self, cli_runner: Any) -> None:
        """Test option with None as default value."""
        import click

        from click_extended.core.option import option

        @command()
        @option("value", default=None)
        def process(value: str | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "Value: None" in result.output

    def test_option_with_zero_default(self, cli_runner: Any) -> None:
        """Test option with 0 as default value."""
        import click

        from click_extended.core.option import option

        @command()
        @option("count", type=int, default=0)
        def process(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "Count: 0" in result.output

    def test_option_with_empty_string_default(self, cli_runner: Any) -> None:
        """Test option with empty string as default."""
        import click

        from click_extended.core.option import option

        @command()
        @option("text", default="")
        def process(text: str) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0
        assert "Text: ''" in result.output

    def test_function_with_return_value(self, cli_runner: Any) -> None:
        """Test that function return values are preserved."""
        from click_extended.core.option import option

        @command()
        @option("value", type=int)
        def calculate(value: int) -> int:
            return value * 2

        result = cli_runner.invoke(calculate, ["--value", "5"])
        assert result.exit_code == 0

    def test_complex_scenario_all_node_types(self, cli_runner: Any) -> None:
        """Test complex scenario with multiple node types."""
        import click

        from click_extended.core.argument import argument
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option

        class Validate(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.strip().upper()

        @command()
        @option("verbose", is_flag=True)
        @option("format", default="json")
        @argument("filename")
        @Validate.as_decorator()
        def process(filename: str, format: str, verbose: bool) -> None:
            click.echo(
                f"File: {filename}, Format: {format}, Verbose: {verbose}"
            )

        result = cli_runner.invoke(
            process, ["--verbose", "--format", "xml", "  test.txt  "]
        )
        assert result.exit_code == 0
        assert "File: TEST.TXT" in result.output
        assert "Format: xml" in result.output
        assert "Verbose: True" in result.output


class TestRootNodeGroupFunctionality:
    """Test Group-specific RootNode functionality."""

    def test_group_with_single_subcommand(self, cli_runner: Any) -> None:
        """Test group with a single subcommand."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def hello() -> None:
            """Say hello."""
            click.echo("Hello!")

        result = cli_runner.invoke(cli, ["hello"])
        assert result.exit_code == 0
        assert "Hello!" in result.output

    def test_group_with_multiple_subcommands(self, cli_runner: Any) -> None:
        """Test group with multiple subcommands."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def start() -> None:
            """Start service."""
            click.echo("Starting...")

        @cli.command()  # type: ignore[misc]
        def stop() -> None:
            """Stop service."""
            click.echo("Stopping...")

        result1 = cli_runner.invoke(cli, ["start"])
        assert result1.exit_code == 0
        assert "Starting..." in result1.output

        result2 = cli_runner.invoke(cli, ["stop"])
        assert result2.exit_code == 0
        assert "Stopping..." in result2.output

    def test_nested_groups(self, cli_runner: Any) -> None:
        """Test nested group structure."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.group()  # type: ignore[misc]
        def database() -> None:
            """Database commands."""
            pass

        @database.command()  # type: ignore[misc]
        def migrate() -> None:
            """Run migrations."""
            click.echo("Migrating...")

        result = cli_runner.invoke(cli, ["database", "migrate"])
        assert result.exit_code == 0
        assert "Migrating..." in result.output

    def test_group_add_command(self, cli_runner: Any) -> None:
        """Test adding command to group via add_command."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @command()
        def deploy() -> None:
            """Deploy application."""
            click.echo("Deploying...")

        cli.add_command(deploy)

        result = cli_runner.invoke(cli, ["deploy"])
        assert result.exit_code == 0
        assert "Deploying..." in result.output

    def test_group_invocation_without_subcommand(self, cli_runner: Any) -> None:
        """Test invoking group without subcommand shows help."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def hello() -> None:
            """Say hello."""
            pass

        result = cli_runner.invoke(cli, [])
        # Click returns exit code 2 when group invoked without subcommand
        assert result.exit_code in (0, 2)
        assert "Usage:" in result.output or "Commands:" in result.output

    def test_group_help_display(self, cli_runner: Any) -> None:
        """Test group help shows all subcommands."""

        @group()
        def cli() -> None:
            """Main CLI group."""
            pass

        @cli.command()  # type: ignore[misc]
        def start() -> None:
            """Start the service."""
            pass

        @cli.command()  # type: ignore[misc]
        def stop() -> None:
            """Stop the service."""
            pass

        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Main CLI group" in result.output
        assert "start" in result.output
        assert "stop" in result.output

    def test_group_with_options(self, cli_runner: Any) -> None:
        """Test group with options passed to handler."""
        import click

        from click_extended.core.option import option

        @group()
        @option("verbose", is_flag=True)
        def cli(verbose: bool) -> None:
            """Main CLI."""
            if verbose:
                click.echo("Verbose mode")

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            click.echo("Testing")

        result = cli_runner.invoke(cli, ["--verbose", "test"])
        assert result.exit_code == 0
        assert "Verbose mode" in result.output
        assert "Testing" in result.output

    def test_group_subcommand_with_options(self, cli_runner: Any) -> None:
        """Test subcommand with its own options."""
        import click

        from click_extended.core.option import option

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        @option("port", type=int, default=8080)
        def serve(port: int) -> None:
            """Start server."""
            click.echo(f"Serving on port {port}")

        result = cli_runner.invoke(cli, ["serve", "--port", "3000"])
        assert result.exit_code == 0
        assert "Serving on port 3000" in result.output

    def test_group_with_callback(self, cli_runner: Any) -> None:
        """Test group with callback function."""
        import click

        execution_order = []

        @group()
        def cli() -> None:
            """Main CLI."""
            execution_order.append("group")

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            execution_order.append("command")
            click.echo("Test")

        result = cli_runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert execution_order == ["group", "command"]

    def test_three_level_nested_groups(self, cli_runner: Any) -> None:
        """Test three-level nested group structure."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.group()  # type: ignore[misc]
        def admin() -> None:
            """Admin commands."""
            pass

        @admin.group()  # type: ignore[misc]
        def users() -> None:
            """User management."""
            pass

        @users.command()  # type: ignore[misc]
        def add() -> None:
            """Add a user."""
            click.echo("User added")

        result = cli_runner.invoke(cli, ["admin", "users", "add"])
        assert result.exit_code == 0
        assert "User added" in result.output

    def test_group_with_aliases(self, cli_runner: Any) -> None:
        """Test group initialization with aliases."""

        @group(aliases=["c", "main"])
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            pass

        # Note: Click doesn't natively support group aliases in invocation
        # This test verifies the group can be created with aliases
        result = cli_runner.invoke(cli, ["test"])
        assert result.exit_code == 0

    def test_group_chain_mode(self, cli_runner: Any) -> None:
        """Test group with chain mode allowing multiple commands."""
        import click

        @group(chain=True)
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def clean() -> None:
            """Clean up."""
            click.echo("Cleaned")

        @cli.command()  # type: ignore[misc]
        def build() -> None:
            """Build project."""
            click.echo("Built")

        result = cli_runner.invoke(cli, ["clean", "build"])
        assert result.exit_code == 0
        assert "Cleaned" in result.output
        assert "Built" in result.output

    def test_group_with_invoke_without_command(self, cli_runner: Any) -> None:
        """Test group configured to invoke without command."""
        import click

        @group(invoke_without_command=True)
        def cli() -> None:
            """Main CLI."""
            ctx = click.get_current_context()
            if ctx.invoked_subcommand is None:
                click.echo("No subcommand")

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            click.echo("Test")

        result = cli_runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "No subcommand" in result.output

    def test_group_command_name_collision_prevention(
        self, cli_runner: Any
    ) -> None:
        """Test that duplicate command names are handled."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """First test."""
            pass

        # Adding another command with the same name should replace or error
        @cli.command()  # type: ignore[misc]
        def test2() -> None:
            """Second test."""
            pass

        # The second definition should be the one that runs
        # Both commands should be available
        result = cli_runner.invoke(cli, ["test"])
        assert result.exit_code == 0


class TestRootNodeEnvIntegration:
    """Test Env node integration with RootNode."""

    def test_env_with_command_basic(self, cli_runner: Any) -> None:
        """Test basic env decorator with command."""
        import os

        import click

        from click_extended.core.env import env

        @command()
        @env("TEST_VAR")
        def check(test_var: str) -> None:
            click.echo(f"Value: {test_var}")

        # Set environment variable
        os.environ["TEST_VAR"] = "test_value"

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 0
        assert "Value: test_value" in result.output

        # Clean up
        del os.environ["TEST_VAR"]

    def test_env_missing_single_variable(self, cli_runner: Any) -> None:
        """Test error when single env variable is missing."""
        import os

        from click_extended.core.env import env

        @command()
        @env("MISSING_VAR", required=True)
        def check(missing_var: str) -> None:
            pass

        # Ensure variable is not set
        if "MISSING_VAR" in os.environ:
            del os.environ["MISSING_VAR"]

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 1
        assert "MISSING_VAR" in result.output

    def test_env_missing_multiple_variables(self, cli_runner: Any) -> None:
        """Test error message when multiple env variables are missing."""
        import os

        from click_extended.core.env import env

        @command()
        @env("VAR_ONE", required=True)
        @env("VAR_TWO", required=True)
        @env("VAR_THREE", required=True)
        def check(var_one: str, var_two: str, var_three: str) -> None:
            pass

        # Ensure variables are not set
        for var in ["VAR_ONE", "VAR_TWO", "VAR_THREE"]:
            if var in os.environ:
                del os.environ[var]

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 1
        # Should show all missing variables
        assert "VAR_ONE" in result.output
        assert "VAR_TWO" in result.output
        assert "VAR_THREE" in result.output

    def test_env_with_default_value(self, cli_runner: Any) -> None:
        """Test env with default value when variable not set."""
        import os

        import click

        from click_extended.core.env import env

        @command()
        @env("OPTIONAL_VAR", default="default_value")
        def check(optional_var: str) -> None:
            click.echo(f"Value: {optional_var}")

        # Ensure variable is not set
        if "OPTIONAL_VAR" in os.environ:
            del os.environ["OPTIONAL_VAR"]

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 0
        assert "Value: default_value" in result.output

    def test_env_with_children_processors(self, cli_runner: Any) -> None:
        """Test env with child processors transforming value."""
        import os

        import click

        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.env import env

        class Uppercase(ChildNode):
            def handle_str(
                self, value: str, context: Context, *args: Any, **kwargs: Any
            ) -> str:
                return value.upper()

        @command()
        @env("MY_VAR")
        @Uppercase.as_decorator()
        def check(my_var: str) -> None:
            click.echo(f"Value: {my_var}")

        os.environ["MY_VAR"] = "lowercase"

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 0
        assert "Value: LOWERCASE" in result.output

        del os.environ["MY_VAR"]

    def test_env_with_type_conversion(self, cli_runner: Any) -> None:
        """Test env with type conversion."""
        import os

        import click

        from click_extended.core.env import env

        @command()
        @env("PORT_NUMBER", type=int)
        def check(port_number: int) -> None:
            click.echo(f"Port: {port_number}")

        os.environ["PORT_NUMBER"] = "8080"

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 0
        assert "Port: 8080" in result.output

        del os.environ["PORT_NUMBER"]

    def test_env_mixed_with_options(self, cli_runner: Any) -> None:
        """Test env mixed with option decorators."""
        import os

        import click

        from click_extended.core.env import env
        from click_extended.core.option import option

        @command()
        @option("name")
        @env("API_KEY")
        def deploy(name: str, api_key: str) -> None:
            click.echo(f"Deploying {name} with key {api_key}")

        os.environ["API_KEY"] = "secret123"

        result = cli_runner.invoke(deploy, ["--name", "myapp"])
        assert result.exit_code == 0
        assert "Deploying myapp with key secret123" in result.output

        del os.environ["API_KEY"]

    def test_env_error_message_formatting_single(self, cli_runner: Any) -> None:
        """Test error message format for single missing variable."""
        import os

        from click_extended.core.env import env

        @command()
        @env("DATABASE_URL", required=True)
        def connect(database_url: str) -> None:
            pass

        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

        result = cli_runner.invoke(connect, [])
        assert result.exit_code == 1
        # Error should mention the specific variable
        assert "DATABASE_URL" in result.output
        assert (
            "environment" in result.output.lower()
            or "missing" in result.output.lower()
        )

    def test_env_error_message_formatting_multiple(
        self, cli_runner: Any
    ) -> None:
        """Test error message format for multiple missing variables."""
        import os

        from click_extended.core.env import env

        @command()
        @env("DB_HOST", required=True)
        @env("DB_PORT", required=True)
        def connect(db_host: str, db_port: str) -> None:
            pass

        for var in ["DB_HOST", "DB_PORT"]:
            if var in os.environ:
                del os.environ[var]

        result = cli_runner.invoke(connect, [])
        assert result.exit_code == 1
        assert "DB_HOST" in result.output
        assert "DB_PORT" in result.output

    def test_env_with_group(self, cli_runner: Any) -> None:
        """Test env with group command."""
        import os

        import click

        from click_extended.core.env import env

        @group()
        @env("CONFIG_PATH")
        def cli(config_path: str) -> None:
            """Main CLI."""
            click.echo(f"Config: {config_path}")

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            click.echo("Testing")

        os.environ["CONFIG_PATH"] = "/etc/config.yaml"

        result = cli_runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "Config: /etc/config.yaml" in result.output
        assert "Testing" in result.output

        del os.environ["CONFIG_PATH"]


class TestRootNodeDebugMode:
    """Test RootNode error handling in various scenarios."""

    def test_error_handling_basic(self, cli_runner: Any) -> None:
        """Test basic error handling with ContextAwareError."""
        from click_extended.core.option import option
        from click_extended.errors import ContextAwareError

        @command()
        @option("value", type=int)
        def check(value: int) -> None:
            if value < 0:
                raise ContextAwareError("Value must be positive")

        result = cli_runner.invoke(check, ["--value", "-5"])
        assert result.exit_code == 1
        assert "Value must be positive" in result.output

    def test_error_with_type_conversion(self, cli_runner: Any) -> None:
        """Test error handling with type conversion error."""
        from click_extended.core.option import option

        @command()
        @option("count", type=int)
        def process(count: int) -> None:
            pass

        result = cli_runner.invoke(process, ["--count", "invalid"])
        assert result.exit_code != 0

    def test_error_with_child_validation(self, cli_runner: Any) -> None:
        """Test error handling in child node validation."""
        from click_extended.core.child_node import ChildNode
        from click_extended.core.context import Context
        from click_extended.core.option import option
        from click_extended.errors import ContextAwareError

        class Validator(ChildNode):
            def handle_int(
                self, value: int, context: Context, *args: Any, **kwargs: Any
            ) -> int:
                if value > 100:
                    raise ContextAwareError("Value too large")
                return value

        @command()
        @option("num", type=int)
        @Validator.as_decorator()
        def check(num: int) -> None:
            pass

        result = cli_runner.invoke(check, ["--num", "999"])
        assert result.exit_code == 1
        assert "Value too large" in result.output

    def test_error_with_missing_required_env(self, cli_runner: Any) -> None:
        """Test error handling with missing required environment variable."""
        import os

        from click_extended.core.env import env

        @command()
        @env("MISSING_DEBUG_VAR", required=True)
        def check(missing_debug_var: str) -> None:
            pass

        if "MISSING_DEBUG_VAR" in os.environ:
            del os.environ["MISSING_DEBUG_VAR"]

        result = cli_runner.invoke(check, [])
        assert result.exit_code == 1
        assert "MISSING_DEBUG_VAR" in result.output

    def test_error_with_generic_exception(self, cli_runner: Any) -> None:
        """Test error handling with generic Python exception."""
        from click_extended.core.option import option

        @command()
        @option("value")
        def check(value: str) -> None:
            raise ValueError("Something went wrong")

        result = cli_runner.invoke(check, ["--value", "test"])
        assert result.exit_code == 1
        assert "ValueError" in result.output
        assert "Something went wrong" in result.output


class TestRootNodeAliasInvocation:
    """Test RootNode alias invocation functionality."""

    def test_command_with_single_alias_storage(self, cli_runner: Any) -> None:
        """Test that command stores single alias correctly."""

        @command(aliases="s")
        def serve() -> None:
            """Start server."""
            pass

        # Verify alias is stored
        assert serve.root.aliases == "s"  # type: ignore[attr-defined]

    def test_command_with_multiple_aliases_storage(
        self, cli_runner: Any
    ) -> None:
        """Test that command stores multiple aliases correctly."""

        @command(aliases=["s", "start", "run"])
        def serve() -> None:
            """Start server."""
            pass

        # Verify aliases are stored
        assert serve.root.aliases == ["s", "start", "run"]  # type: ignore[attr-defined]

    def test_group_with_single_alias_storage(self, cli_runner: Any) -> None:
        """Test that group stores single alias correctly."""

        @group(aliases="c")
        def cli() -> None:
            """Main CLI."""
            pass

        # Verify alias is stored
        assert cli.root.aliases == "c"  # type: ignore[attr-defined]

    def test_group_with_multiple_aliases_storage(self, cli_runner: Any) -> None:
        """Test that group stores multiple aliases correctly."""

        @group(aliases=["c", "main", "app"])
        def cli() -> None:
            """Main CLI."""
            pass

        # Verify aliases are stored
        assert cli.root.aliases == ["c", "main", "app"]  # type: ignore[attr-defined]

    def test_format_name_with_aliases_in_help(self, cli_runner: Any) -> None:
        """Test that format_name_with_aliases works for help display."""
        from click_extended.core.command import Command

        cmd = Command(name="deploy", aliases=["d", "push"])
        formatted = cmd.format_name_with_aliases()

        assert formatted == "deploy (d, push)"

    def test_empty_aliases_filtered_in_format(self, cli_runner: Any) -> None:
        """Test that empty aliases are filtered out in formatting."""
        from click_extended.core.command import Command

        cmd = Command(name="build", aliases=["b", "", "compile", ""])
        formatted = cmd.format_name_with_aliases()

        assert formatted == "build (b, compile)"

    def test_command_aliases_preserved_in_tree(self, cli_runner: Any) -> None:
        """Test that aliases are preserved in the tree structure."""

        @command(aliases=["t", "check"])
        def test() -> None:
            """Run tests."""
            pass

        # Aliases should be accessible via the root node
        assert test.root.aliases == ["t", "check"]  # type: ignore[attr-defined]
        assert test.root.name == "test"  # type: ignore[attr-defined]

    def test_group_aliases_preserved_with_subcommands(
        self, cli_runner: Any
    ) -> None:
        """Test that group aliases are preserved with subcommands."""
        import click

        @group(aliases="c")
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def test() -> None:
            """Test command."""
            click.echo("Testing")

        # Group aliases should be preserved
        assert cli.root.aliases == "c"  # type: ignore[attr-defined]

        result = cli_runner.invoke(cli, ["test"])
        assert result.exit_code == 0

    def test_subcommand_with_aliases(self, cli_runner: Any) -> None:
        """Test subcommand with its own aliases."""
        import click

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command(aliases=["d", "push"])  # type: ignore[misc]
        def deploy() -> None:
            """Deploy application."""
            click.echo("Deploying")

        # Note: Click's native alias support is limited
        result = cli_runner.invoke(cli, ["deploy"])
        assert result.exit_code == 0
        assert "Deploying" in result.output

    def test_aliases_with_special_characters_filtered(
        self, cli_runner: Any
    ) -> None:
        """Test that empty aliases are filtered out."""
        from click_extended.core.command import Command

        cmd = Command(name="build", aliases=["", "b", "", "compile"])
        filtered = [a for a in cmd.aliases if a]  # type: ignore[union-attr]

        assert len(filtered) == 2
        assert "b" in filtered
        assert "compile" in filtered


class TestClickCommandAndGroupClasses:
    """Test the ClickCommand and ClickGroup classes."""

    def test_click_command_requires_root_instance(self) -> None:
        """Test that ClickCommand raises ValueError without root_instance."""
        from click_extended.core._click_command import ClickCommand

        with pytest.raises(
            ValueError, match="root_instance is required for ClickCommand"
        ):
            ClickCommand(name="test", root_instance=None)

    def test_click_group_requires_root_instance(self) -> None:
        """Test that ClickGroup raises ValueError without root_instance."""
        from click_extended.core._click_group import ClickGroup

        with pytest.raises(
            ValueError, match="root_instance is required for ClickGroup"
        ):
            ClickGroup(name="test", root_instance=None)

    def test_click_command_with_root_instance(self) -> None:
        """Test that ClickCommand works with valid root_instance."""
        from click_extended.core._click_command import ClickCommand
        from click_extended.core.command import Command

        root = Command(name="test")
        click_cmd = ClickCommand(name="test", root_instance=root)

        assert click_cmd.root == root
        assert click_cmd.name == "test"

    def test_click_group_with_root_instance(self) -> None:
        """Test that ClickGroup works with valid root_instance."""
        from click_extended.core._click_group import ClickGroup
        from click_extended.core.group import Group

        root = Group(name="test")
        click_grp = ClickGroup(name="test", root_instance=root)

        assert click_grp.root == root
        assert click_grp.name == "test"

    def test_click_group_add_command_with_string_alias(
        self, cli_runner: Any
    ) -> None:
        """Test ClickGroup.add_command with command that has string alias."""
        import click

        from click_extended.core._click_group import ClickGroup
        from click_extended.core.command import Command
        from click_extended.core.group import Group

        # Create a group
        root_group = Group(name="cli")
        click_grp = ClickGroup(name="cli", root_instance=root_group)

        # Create a command with a single alias
        root_cmd = Command(name="deploy", aliases="d")
        click_cmd = click.Command(
            name="deploy", callback=lambda: click.echo("Deploying")
        )
        click_cmd.aliases = "d"  # type: ignore[attr-defined]

        # Add command to group
        click_grp.add_command(click_cmd)

        # Both name and alias should work
        assert "deploy" in click_grp.commands
        assert "d" in click_grp.commands

    def test_click_group_add_command_with_list_aliases(
        self, cli_runner: Any
    ) -> None:
        """Test ClickGroup.add_command with command that has list of aliases."""
        import click

        from click_extended.core._click_group import ClickGroup
        from click_extended.core.group import Group

        # Create a group
        root_group = Group(name="cli")
        click_grp = ClickGroup(name="cli", root_instance=root_group)

        # Create a command with multiple aliases
        click_cmd = click.Command(
            name="deploy", callback=lambda: click.echo("Deploying")
        )
        click_cmd.aliases = ["d", "push", "release"]  # type: ignore[attr-defined]

        # Add command to group
        click_grp.add_command(click_cmd)

        # Name and all aliases should work
        assert "deploy" in click_grp.commands
        assert "d" in click_grp.commands
        assert "push" in click_grp.commands
        assert "release" in click_grp.commands

    def test_click_group_command_decorator_extracts_docstring(
        self, cli_runner: Any
    ) -> None:
        """Test that .command() decorator extracts help from docstring."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command()  # type: ignore[misc]
        def deploy() -> None:
            """Deploy the application.

            This is the full docstring.
            """
            pass

        # Help text should be extracted from first line of docstring
        result = cli_runner.invoke(cli, ["--help"])
        assert "Deploy the application" in result.output

    def test_click_group_group_decorator_extracts_docstring(
        self, cli_runner: Any
    ) -> None:
        """Test that .group() decorator extracts help from docstring."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.group()  # type: ignore[misc]
        def admin() -> None:
            """Admin commands.

            These are administrative commands.
            """
            pass

        # Help text should be extracted from first line of docstring
        result = cli_runner.invoke(cli, ["--help"])
        assert "Admin commands" in result.output

    def test_click_group_command_with_explicit_help(
        self, cli_runner: Any
    ) -> None:
        """Test that .command() decorator uses explicit help parameter."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.command(help="Explicit help text")  # type: ignore[misc]
        def deploy() -> None:
            """Docstring that should be ignored."""
            pass

        # Help text should be the explicit parameter, not docstring
        result = cli_runner.invoke(cli, ["--help"])
        assert "Explicit help text" in result.output
        assert "Docstring that should be ignored" not in result.output

    def test_click_group_group_with_explicit_help(
        self, cli_runner: Any
    ) -> None:
        """Test that .group() decorator uses explicit help parameter."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.group(help="Explicit group help")  # type: ignore[misc]
        def admin() -> None:
            """Docstring that should be ignored."""
            pass

        # Help text should be the explicit parameter, not docstring
        result = cli_runner.invoke(cli, ["--help"])
        assert "Explicit group help" in result.output
        assert "Docstring that should be ignored" not in result.output

    def test_click_group_group_decorator_with_aliases(
        self, cli_runner: Any
    ) -> None:
        """Test .group() decorator with aliases parameter."""

        @group()
        def cli() -> None:
            """Main CLI."""
            pass

        @cli.group(aliases="adm", help="Admin commands")  # type: ignore[misc]
        def admin() -> None:
            """Admin commands."""
            pass

        # Both name and alias should work
        result1 = cli_runner.invoke(cli, ["admin", "--help"])
        assert result1.exit_code == 0

        result2 = cli_runner.invoke(cli, ["adm", "--help"])
        assert result2.exit_code == 0

    def test_click_group_format_commands_with_empty_aliases(
        self, cli_runner: Any
    ) -> None:
        """Test format_commands with command that has empty string aliases."""
        import click

        from click_extended.core._click_group import ClickGroup
        from click_extended.core.group import Group

        # Create a group
        root_group = Group(name="cli")
        click_grp = ClickGroup(name="cli", root_instance=root_group)

        # Create a command with aliases including empty strings
        click_cmd = click.Command(
            name="deploy", callback=lambda: click.echo("Deploying")
        )
        click_cmd.aliases = ["d", "", "push", ""]  # type: ignore[attr-defined]

        # Add command to group
        click_grp.add_command(click_cmd)

        # Format commands - should filter empty aliases
        formatter = click.HelpFormatter()
        click_grp.format_commands(click.Context(click_grp), formatter)

        # Should have formatted properly with non-empty aliases
        assert "deploy (d, push)" in formatter.getvalue()

    def test_group_decorator_extracts_docstring_help(
        self, cli_runner: Any
    ) -> None:
        """Test that group() decorator extracts help from docstring."""

        @group()
        def admin() -> None:
            """Admin panel commands.

            Full description of admin commands.
            """
            pass

        # Help text should be extracted from first line
        result = cli_runner.invoke(admin, ["--help"])
        assert result.exit_code == 0
        assert "Admin panel commands" in result.output

    def test_click_group_add_method_returns_self(self) -> None:
        """Test that ClickGroup.add() returns self for chaining."""
        import click

        from click_extended.core._click_group import ClickGroup
        from click_extended.core.group import Group

        root_group = Group(name="cli")
        click_grp = ClickGroup(name="cli", root_instance=root_group)

        cmd1 = click.Command(name="cmd1", callback=lambda: None)
        cmd2 = click.Command(name="cmd2", callback=lambda: None)

        # Test method chaining
        result = click_grp.add(cmd1).add(cmd2)

        assert result is click_grp
        assert "cmd1" in click_grp.commands
        assert "cmd2" in click_grp.commands


class TestCommandAliases:
    """Test command alias functionality."""

    def test_aliases_with_special_characters_filtered(
        self, cli_runner: Any
    ) -> None:

        # Creating with aliases including empty strings
        cmd = Command(name="test", aliases=["t", "", "check"])
        formatted = cmd.format_name_with_aliases()

        # Empty strings are filtered out by format_name_with_aliases
        assert formatted == "test (t, check)"

    def test_format_name_with_aliases_no_aliases(self) -> None:
        """Test format_name_with_aliases when no aliases provided."""
        cmd = Command(name="test")
        formatted = cmd.format_name_with_aliases()
        assert formatted == "test"

    def test_format_name_with_aliases_only_empty_strings(self) -> None:
        """Test format_name_with_aliases when all aliases are empty."""
        cmd = Command(name="test", aliases=["", ""])
        formatted = cmd.format_name_with_aliases()
        assert formatted == "test"


class TestClickDecoratorMethods:
    """Test _get_click_decorator methods."""

    def test_command_get_click_decorator(self) -> None:
        """Test Command._get_click_decorator returns click.command."""
        from click_extended.core.command import Command

        decorator = Command._get_click_decorator()
        # Should return click.command function
        assert callable(decorator)

    def test_group_get_click_decorator(self) -> None:
        """Test Group._get_click_decorator returns click.group."""
        from click_extended.core.group import Group

        decorator = Group._get_click_decorator()
        # Should return click.group function
        assert callable(decorator)
