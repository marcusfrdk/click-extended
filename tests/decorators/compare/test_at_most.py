"""Tests for at_most decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.decorators.tag import tag
from click_extended.decorators.compare.at_most import at_most


class TestAtMostBasic:
    """Test basic at_most functionality."""

    def test_at_most_with_exact_maximum(self, cli_runner: CliRunner) -> None:
        """Test that providing exactly the maximum succeeds."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_most(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_at_most_with_less_than_maximum(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing less than maximum succeeds."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_most(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a"])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_at_most_with_more_than_maximum_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing more than maximum fails."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_most(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c"]
        )
        assert result.exit_code == 1
        assert "At most 2" in result.output
        assert "3 were given" in result.output

    def test_at_most_with_none_provided(self, cli_runner: CliRunner) -> None:
        """Test that providing no parameters succeeds."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_most(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Success" in result.output


class TestAtMostOne:
    """Test at_most(1) - at most one allowed."""

    def test_at_most_one_with_one_provided(self, cli_runner: CliRunner) -> None:
        """Test at_most(1) succeeds with one parameter."""

        @command()
        @option("--method1", default=None, tags="method")
        @option("--method2", default=None, tags="method")
        @option("--method3", default=None, tags="method")
        @tag("method")
        @at_most(1)
        def cmd(
            method1: str | None, method2: str | None, method3: str | None
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--method1", "a"])
        assert result.exit_code == 0

    def test_at_most_one_with_two_fails(self, cli_runner: CliRunner) -> None:
        """Test at_most(1) fails with two parameters."""

        @command()
        @option("--method1", default=None, tags="method")
        @option("--method2", default=None, tags="method")
        @option("--method3", default=None, tags="method")
        @tag("method")
        @at_most(1)
        def cmd(
            method1: str | None, method2: str | None, method3: str | None
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--method1", "a", "--method2", "b"])
        assert result.exit_code == 1
        assert "At most 1" in result.output

    def test_at_most_one_with_none_succeeds(
        self, cli_runner: CliRunner
    ) -> None:
        """Test at_most(1) succeeds with no parameters."""

        @command()
        @option("--method1", default=None, tags="method")
        @option("--method2", default=None, tags="method")
        @tag("method")
        @at_most(1)
        def cmd(method1: str | None, method2: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0


class TestAtMostMultiple:
    """Test at_most with various limits."""

    def test_at_most_zero_allows_none(self, cli_runner: CliRunner) -> None:
        """Test at_most(0) allows no parameters."""

        @command()
        @option("--opt1", default=None, tags="none")
        @option("--opt2", default=None, tags="none")
        @tag("none")
        @at_most(0)
        def cmd(opt1: str | None, opt2: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--opt1", "a"])
        assert result.exit_code == 1

    def test_at_most_with_five_params(self, cli_runner: CliRunner) -> None:
        """Test at_most with multiple parameters."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @option("--opt4", default=None, tags="group")
        @option("--opt5", default=None, tags="group")
        @tag("group")
        @at_most(3)
        def cmd(
            opt1: str | None,
            opt2: str | None,
            opt3: str | None,
            opt4: str | None,
            opt5: str | None,
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c", "--opt4", "d"]
        )
        assert result.exit_code == 1


class TestAtMostWithFlags:
    """Test at_most with boolean flags."""

    def test_at_most_with_flags(self, cli_runner: CliRunner) -> None:
        """Test at_most works with boolean flags."""

        @command()
        @option("--flag1", is_flag=True, default=False, tags="flags")
        @option("--flag2", is_flag=True, default=False, tags="flags")
        @option("--flag3", is_flag=True, default=False, tags="flags")
        @tag("flags")
        @at_most(2)
        def cmd(flag1: bool, flag2: bool, flag3: bool) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--flag1", "--flag2"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--flag1", "--flag2", "--flag3"])
        assert result.exit_code == 1


class TestAtMostErrorMessages:
    """Test error message formatting."""

    def test_error_message_shows_count(self, cli_runner: CliRunner) -> None:
        """Test error message shows maximum and provided counts."""

        @command()
        @option("--a", default=None, tags="group")
        @option("--b", default=None, tags="group")
        @option("--c", default=None, tags="group")
        @tag("group")
        @at_most(1)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--a", "1", "--b", "2"])
        assert result.exit_code == 1
        assert "At most 1" in result.output
        assert "2 were given" in result.output

    def test_error_message_grammar_singular(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message uses correct grammar for singular."""

        @command()
        @option("--a", default=None, tags="group")
        @option("--b", default=None, tags="group")
        @tag("group")
        @at_most(0)
        def cmd(a: str | None, b: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--a", "1"])
        assert result.exit_code == 1
        assert "1 was given" in result.output

    def test_error_message_shows_param_names(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message shows parameter names."""

        @command()
        @option("--format", default=None, tags="output")
        @option("--style", default=None, tags="output")
        @tag("output")
        @at_most(1)
        def cmd(format: str | None, style: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--format", "json", "--style", "pretty"]
        )
        assert result.exit_code == 1
        assert "format" in result.output
        assert "style" in result.output


class TestAtMostPractical:
    """Test practical real-world use cases."""

    def test_single_override_option(self, cli_runner: CliRunner) -> None:
        """Test allowing at most one override option."""

        @command()
        @option(
            "override_config",
            "--override-config",
            default=None,
            tags="override",
        )
        @option("override_env", "--override-env", default=None, tags="override")
        @option("override_cli", "--override-cli", default=None, tags="override")
        @tag("override")
        @at_most(1)
        def run(
            override_config: str | None,
            override_env: str | None,
            override_cli: str | None,
        ) -> None:
            click.echo("Running")

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0

        result = cli_runner.invoke(run, ["--override-config", "custom.yaml"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            run, ["--override-config", "c.yaml", "--override-env", "prod"]
        )
        assert result.exit_code == 1

    def test_optional_metadata(self, cli_runner: CliRunner) -> None:
        """Test allowing limited optional metadata."""

        @command()
        @option("--tag", default=None, tags="meta")
        @option("--label", default=None, tags="meta")
        @option("--category", default=None, tags="meta")
        @option("--priority", default=None, tags="meta")
        @tag("meta")
        @at_most(2)
        def create(
            tag: str | None,
            label: str | None,
            category: str | None,
            priority: str | None,
        ) -> None:
            click.echo("Created")

        result = cli_runner.invoke(create, ["--tag", "v1", "--label", "test"])
        assert result.exit_code == 0

        result = cli_runner.invoke(
            create, ["--tag", "v1", "--label", "test", "--category", "bug"]
        )
        assert result.exit_code == 1
