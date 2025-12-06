"""Comprehensive tests for ChildValidationNode functionality."""

from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.decorators.tag import tag
from click_extended.core.nodes.child_validation_node import ChildValidationNode
from click_extended.core.other.context import Context


class TestChildValidationNodeChildMode:
    """Test ChildValidationNode when attached to parents (acts as ChildNode)."""

    def test_child_validation_with_option_processes_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid attached to option processes values via handle_all."""

        class Doubler(ChildValidationNode):
            def handle_int(self, value: int, context: Context) -> int:
                return value * 2

            def on_finalize(self, context: Context) -> None:
                raise RuntimeError("Should not be called in child mode")

        @command()
        @option("--num", type=int, default=5)
        @Doubler.as_decorator()
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "10"])
        assert result.exit_code == 0
        assert "Result: 20" in result.output

    def test_child_validation_with_argument_processes_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid attached to argument processes values."""

        class Uppercaser(ChildValidationNode):
            def handle_str(self, value: str, context: Context) -> str:
                return value.upper()

            def on_finalize(self, context: Context) -> None:
                raise RuntimeError("Should not be called in child mode")

        @command()
        @argument("name")
        @Uppercaser.as_decorator()
        def cmd(name: str) -> None:
            click.echo(f"Name: {name}")

        result = cli_runner.invoke(cmd, ["alice"])
        assert result.exit_code == 0
        assert "Name: ALICE" in result.output

    def test_child_validation_handle_all_fallback(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid uses handle_all when specific handler not implemented."""

        class GenericHandler(ChildValidationNode):
            def handle_all(
                self, value: Any, context: Context, *args: Any, **kwargs: Any
            ) -> Any:
                return f"processed-{value}"

            def on_finalize(self, context: Context) -> None:
                raise RuntimeError("Should not be called")

        @command()
        @option("--text", type=str, default="hello")
        @GenericHandler.as_decorator()
        def cmd(text: str) -> None:
            click.echo(text)

        result = cli_runner.invoke(cmd, ["--text", "world"])
        assert result.exit_code == 0
        assert "processed-world" in result.output

    def test_child_validation_with_decorator_args(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid receives decorator args in child mode."""

        class Multiplier(ChildValidationNode):
            def handle_int(
                self, value: int, context: Context, *args: Any, **kwargs: Any
            ) -> int:
                factor = args[0] if args else 1
                return value * factor

            def on_finalize(self, context: Context) -> None:
                pass

        @command()
        @option("--num", type=int, default=5)
        @Multiplier.as_decorator(3)
        def cmd(num: int) -> None:
            click.echo(f"Result: {num}")

        result = cli_runner.invoke(cmd, ["--num", "7"])
        assert result.exit_code == 0
        assert "Result: 21" in result.output


class TestChildValidationNodeValidationMode:
    """Test ChildValidationNode when standalone (acts as ValidationNode)."""

    def test_child_validation_standalone_runs_on_finalize(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid without parent runs on_finalize."""

        class GlobalValidator(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                raise RuntimeError("Should not be called in validation mode")

            def on_finalize(self, context: Context) -> None:
                click.echo("Global validation executed")

        @command()
        @GlobalValidator.as_decorator()
        def cmd() -> None:
            click.echo("Command executed")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Global validation executed" in result.output
        assert "Command executed" in result.output

    def test_child_validation_validation_accesses_context(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid in validation mode runs on_finalize."""

        class ContextChecker(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                raise RuntimeError(
                    "Should not call handle_all in validation mode"
                )

            def on_finalize(self, context: Context) -> None:
                click.echo("Validation mode confirmed")

        @command()
        @ContextChecker.as_decorator()
        @option("username", type=str, default="admin")
        def cmd(username: str) -> None:
            click.echo("Command done")

        result = cli_runner.invoke(cmd, ["--username", "alice"])
        assert result.exit_code == 0
        assert "Validation mode confirmed" in result.output

    def test_child_validation_validation_with_decorator_args(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid receives decorator args in validation mode."""

        class ConfigurableValidator(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return value

            def on_finalize(
                self, context: Context, *args: Any, **kwargs: Any
            ) -> None:
                required_role = args[0] if args else "user"
                click.echo(f"Required role: {required_role}")

        @command()
        @ConfigurableValidator.as_decorator("admin")
        def cmd() -> None:
            pass

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Required role: admin" in result.output

    def test_child_validation_validation_can_raise_errors(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid validation can abort command execution."""

        class StrictValidator(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return value

            def on_finalize(self, context: Context) -> None:
                raise ValueError("Validation failed")

        @command()
        @StrictValidator.as_decorator()
        def cmd() -> None:
            click.echo("Should not reach here")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "validation failed" in result.output.lower()


class TestChildValidationNodeWithTags:
    """Test ChildValidationNode with tag nodes."""

    def test_child_validation_with_tag_uses_handle_tag(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid attached to tag uses handle_tag method."""

        class RangeValidator(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return value

            def handle_tag(
                self, value: dict[str, Any], context: Context
            ) -> None:
                min_val = value.get("min_val")
                max_val = value.get("max_val")
                if min_val is not None and max_val is not None:
                    if min_val >= max_val:
                        raise ValueError("Min must be less than max")

            def on_finalize(self, context: Context) -> None:
                pass

        @command()
        @option("min_val", type=int, tags="range", default=0)
        @option("max_val", type=int, tags="range", default=100)
        @tag("range")
        @RangeValidator.as_decorator()
        def cmd(min_val: int, max_val: int) -> None:
            click.echo(f"Range: {min_val}-{max_val}")

        # Valid range
        result = cli_runner.invoke(cmd, ["--min-val", "10", "--max-val", "20"])
        assert result.exit_code == 0
        assert "Range: 10-20" in result.output

        # Invalid range
        result = cli_runner.invoke(cmd, ["--min-val", "50", "--max-val", "30"])
        assert result.exit_code == 1
        assert "min must be less than max" in result.output.lower()


class TestChildValidationNodeEdgeCases:
    """Test edge cases and error conditions."""

    def test_child_validation_with_multiple_parents(
        self, cli_runner: CliRunner
    ) -> None:
        """Hybrid can be attached to multiple parents."""

        class Logger(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                click.echo(f"Processing: {value}")
                return value

            def on_finalize(self, context: Context) -> None:
                pass

        @command()
        @option("--first", type=str, default="a")
        @Logger.as_decorator()
        @option("--second", type=str, default="b")
        @Logger.as_decorator()
        def cmd(first: str, second: str) -> None:
            click.echo(f"Values: {first}, {second}")

        result = cli_runner.invoke(cmd, ["--first", "x", "--second", "y"])
        assert result.exit_code == 0
        assert "Processing: x" in result.output
        assert "Processing: y" in result.output

    def test_child_validation_decorator_order_matters(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that decorator order determines child_validation behavior."""

        class ModeDetector(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return f"CHILD:{value}"

            def on_finalize(self, context: Context) -> None:
                click.echo("VALIDATION")

        # Child mode: child_validation AFTER option
        @command()
        @option("--val", type=str, default="test")
        @ModeDetector.as_decorator()
        def cmd1(val: str) -> None:
            click.echo(val)

        result = cli_runner.invoke(cmd1)
        assert "CHILD:test" in result.output
        assert "VALIDATION" not in result.output

        # Validation mode: child_validation BEFORE option
        @command()
        @ModeDetector.as_decorator()
        @option("--val", type=str, default="test")
        def cmd2(val: str) -> None:
            click.echo(val)

        result = cli_runner.invoke(cmd2)
        assert "VALIDATION" in result.output
        assert "CHILD:" not in result.output


class TestChildValidationNodeInheritance:
    """Test that ChildValidationNode properly inherits from both parents."""

    def test_child_validation_has_child_methods(self) -> None:
        """ChildValidationNode has ChildNode methods."""

        class TestHybrid(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return value

            def on_finalize(self, context: Context) -> None:
                pass

        instance = TestHybrid(name="test")
        assert hasattr(instance, "handle_str")
        assert hasattr(instance, "handle_int")
        assert hasattr(instance, "handle_all")

    def test_child_validation_has_validation_methods(self) -> None:
        """ChildValidationNode has ValidationNode methods."""

        class TestHybrid(ChildValidationNode):
            def handle_all(self, value: Any, context: Context) -> Any:
                return value

            def on_finalize(self, context: Context) -> None:
                pass

        instance = TestHybrid(name="test")
        assert hasattr(instance, "on_init")
        assert hasattr(instance, "on_finalize")

    def test_child_validation_mro_is_correct(self) -> None:
        """ChildValidationNode MRO includes both parents."""
        from click_extended.core.nodes.child_node import ChildNode
        from click_extended.core.nodes.validation_node import ValidationNode

        assert issubclass(ChildValidationNode, ChildNode)
        assert issubclass(ChildValidationNode, ValidationNode)


class TestChildValidationNodePracticalExamples:
    """Real-world usage examples."""

    def test_requires_decorator_pattern(self, cli_runner: CliRunner) -> None:
        """Example: @requires decorator that works in both modes."""

        class Requires(ChildValidationNode):
            def handle_all(
                self, value: Any, context: Context, *args: Any, **kwargs: Any
            ) -> Any:
                # Child mode: just pass through, validation elsewhere
                return value

            def on_finalize(
                self, context: Context, *args: Any, **kwargs: Any
            ) -> None:
                # Validation mode: just verify it runs
                click.echo("Validation executed")

        # Child mode: field-level
        @command()
        @option("is_admin", is_flag=True)
        @option("secret", type=str, default="data")
        @Requires.as_decorator()
        def cmd1(is_admin: bool, secret: str) -> None:
            click.echo(f"Secret: {secret}")

        result = cli_runner.invoke(cmd1)
        assert result.exit_code == 0
        assert "Secret: data" in result.output

        # Validation mode: command-level
        @command()
        @Requires.as_decorator()
        @option("is_admin", is_flag=True)
        def cmd2(is_admin: bool) -> None:
            click.echo("Admin panel")

        result = cli_runner.invoke(cmd2)
        assert result.exit_code == 0
        assert "Validation executed" in result.output
