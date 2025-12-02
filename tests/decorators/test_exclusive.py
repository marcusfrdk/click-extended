"""Tests for exclusive decorator."""

import click
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.exclusive import exclusive


class TestExclusiveGroupMode:
    """Test exclusive decorator in group mode (multiple param names)."""

    def test_exclusive_with_none_provided(self, cli_runner: CliRunner) -> None:
        """Test that providing no parameters succeeds."""

        @command()
        @exclusive("format", "json", "xml")
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @option("--xml", is_flag=True, default=False)
        def cmd(format: str | None, json: bool, xml: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}, XML: {xml}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Format: None, JSON: False, XML: False" in result.output

    def test_exclusive_with_one_provided(self, cli_runner: CliRunner) -> None:
        """Test that providing one parameter succeeds."""

        @command()
        @exclusive("format", "json", "xml")
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @option("--xml", is_flag=True, default=False)
        def cmd(format: str | None, json: bool, xml: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}, XML: {xml}")

        # Test with --format
        result = cli_runner.invoke(cmd, ["--format", "yaml"])
        assert result.exit_code == 0
        assert "Format: yaml" in result.output

        # Test with --json
        result = cli_runner.invoke(cmd, ["--json"])
        assert result.exit_code == 0
        assert "JSON: True" in result.output

        # Test with --xml
        result = cli_runner.invoke(cmd, ["--xml"])
        assert result.exit_code == 0
        assert "XML: True" in result.output

    def test_exclusive_with_two_provided_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing two parameters fails."""

        @command()
        @exclusive("format", "json", "xml")
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @option("--xml", is_flag=True, default=False)
        def cmd(format: str | None, json: bool, xml: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}, XML: {xml}")

        result = cli_runner.invoke(cmd, ["--format", "yaml", "--json"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output
        assert "format" in result.output
        assert "json" in result.output

    def test_exclusive_with_all_provided_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing all parameters fails."""

        @command()
        @exclusive("a", "b", "c")
        @option("--a", default=None)
        @option("--b", default=None)
        @option("--c", default=None)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--a", "1", "--b", "2", "--c", "3"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output


class TestExclusiveTwoParams:
    """Test exclusive with two parameters."""

    def test_two_params_both_provided_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing both parameters fails."""

        @command()
        @exclusive("p", "q")
        @option("p", short="-p", default=None)
        @option("q", short="-q", default=None)
        def cmd(p: str | None, q: str | None) -> None:
            click.echo(f"P: {p}, Q: {q}")

        result = cli_runner.invoke(cmd, ["-p", "5", "-q", "10"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output
        assert "'p'" in result.output or "p" in result.output
        assert "'q'" in result.output or "q" in result.output

    def test_two_params_one_provided_succeeds(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing one parameter succeeds."""

        @command()
        @exclusive("p", "q")
        @option("p", short="-p", default=None)
        @option("q", short="-q", default=None)
        def cmd(p: str | None, q: str | None) -> None:
            click.echo(f"P: {p}, Q: {q}")

        # Test with p
        result = cli_runner.invoke(cmd, ["-p", "5"])
        assert result.exit_code == 0
        assert "P: 5, Q: None" in result.output

        # Test with q
        result = cli_runner.invoke(cmd, ["-q", "10"])
        assert result.exit_code == 0
        assert "P: None, Q: 10" in result.output


class TestExclusiveManyParams:
    """Test exclusive with many parameters."""

    def test_many_params_only_one_allowed(self, cli_runner: CliRunner) -> None:
        """Test that only one of many parameters can be provided."""

        @command()
        @exclusive("opt1", "opt2", "opt3", "opt4", "opt5")
        @option("--opt1", default=None)
        @option("--opt2", default=None)
        @option("--opt3", default=None)
        @option("--opt4", default=None)
        @option("--opt5", default=None)
        def cmd(
            opt1: str | None,
            opt2: str | None,
            opt3: str | None,
            opt4: str | None,
            opt5: str | None,
        ) -> None:
            click.echo("Success")

        # Each one alone should work
        for i in range(1, 6):
            result = cli_runner.invoke(cmd, [f"--opt{i}", "value"])
            assert result.exit_code == 0

        # Two together should fail
        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt3", "b"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output


class TestExclusiveWithFlags:
    """Test exclusive with flag options."""

    def test_exclusive_flags(self, cli_runner: CliRunner) -> None:
        """Test exclusive with boolean flags."""

        @command()
        @exclusive("verbose", "quiet", "debug")
        @option("--verbose", is_flag=True, default=False)
        @option("--quiet", is_flag=True, default=False)
        @option("--debug", is_flag=True, default=False)
        def cmd(verbose: bool, quiet: bool, debug: bool) -> None:
            if verbose:
                click.echo("Mode: Verbose")
            elif quiet:
                click.echo("Mode: Quiet")
            elif debug:
                click.echo("Mode: Debug")
            else:
                click.echo("Mode: Normal")

        # No flags - should work
        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Mode: Normal" in result.output

        # One flag - should work
        result = cli_runner.invoke(cmd, ["--verbose"])
        assert result.exit_code == 0
        assert "Mode: Verbose" in result.output

        # Two flags - should fail
        result = cli_runner.invoke(cmd, ["--verbose", "--quiet"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output


class TestExclusiveWithDefaults:
    """Test exclusive with default values."""

    def test_defaults_not_considered_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that default values don't trigger exclusivity."""

        @command()
        @exclusive("format", "output")
        @option("--format", default="json")
        @option("--output", default="stdout")
        def cmd(format: str, output: str) -> None:
            click.echo(f"Format: {format}, Output: {output}")

        # Neither explicitly provided - should work
        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Format: json, Output: stdout" in result.output

        # One explicitly provided - should work
        result = cli_runner.invoke(cmd, ["--format", "xml"])
        assert result.exit_code == 0
        assert "Format: xml" in result.output

        # Both explicitly provided - should fail
        result = cli_runner.invoke(cmd, ["--format", "xml", "--output", "file"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output


class TestExclusiveErrorMessages:
    """Test error message formatting."""

    def test_error_message_shows_all_conflicts(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that error message shows all conflicting parameters."""

        @command()
        @exclusive("a", "b", "c")
        @option("--a", default=None)
        @option("--b", default=None)
        @option("--c", default=None)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--a", "1", "--b", "2"])
        assert result.exit_code == 1
        assert "2 were given" in result.output or "2" in result.output

    def test_error_message_with_three_conflicts(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message when three parameters conflict."""

        @command()
        @exclusive("x", "y", "z")
        @option("--x", default=None)
        @option("--y", default=None)
        @option("--z", default=None)
        def cmd(x: str | None, y: str | None, z: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--x", "1", "--y", "2", "--z", "3"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output
        assert "3 were given" in result.output or "3" in result.output


class TestExclusiveEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_group(self, cli_runner: CliRunner) -> None:
        """Test exclusive with no parameters specified."""

        @command()
        @exclusive()
        @option("--opt", default=None)
        def cmd(opt: str | None) -> None:
            click.echo(f"Opt: {opt}")

        result = cli_runner.invoke(cmd, ["--opt", "value"])
        assert result.exit_code == 0

    def test_single_param_group(self, cli_runner: CliRunner) -> None:
        """Test exclusive with only one parameter."""

        @command()
        @exclusive("only")
        @option("--only", default=None)
        def cmd(only: str | None) -> None:
            click.echo(f"Only: {only}")

        result = cli_runner.invoke(cmd, ["--only", "value"])
        assert result.exit_code == 0

    def test_nonexistent_param_ignored(self, cli_runner: CliRunner) -> None:
        """Test that nonexistent parameters in group are ignored."""

        @command()
        @exclusive("real", "fake", "another_fake")
        @option("--real", default=None)
        def cmd(real: str | None) -> None:
            click.echo(f"Real: {real}")

        # Should work since only 'real' exists
        result = cli_runner.invoke(cmd, ["--real", "value"])
        assert result.exit_code == 0


class TestExclusivePractical:
    """Test practical real-world use cases."""

    def test_output_format_selection(self, cli_runner: CliRunner) -> None:
        """Test exclusive output format selection."""

        @command()
        @exclusive("json", "xml", "yaml", "csv")
        @option("--json", is_flag=True, default=False)
        @option("--xml", is_flag=True, default=False)
        @option("--yaml", is_flag=True, default=False)
        @option("--csv", is_flag=True, default=False)
        def export(json: bool, xml: bool, yaml: bool, csv: bool) -> None:
            if json:
                click.echo("Exporting as JSON")
            elif xml:
                click.echo("Exporting as XML")
            elif yaml:
                click.echo("Exporting as YAML")
            elif csv:
                click.echo("Exporting as CSV")
            else:
                click.echo("Exporting as default format")

        # Each format alone should work
        for fmt in ["json", "xml", "yaml", "csv"]:
            result = cli_runner.invoke(export, [f"--{fmt}"])
            assert result.exit_code == 0

        # Multiple formats should fail
        result = cli_runner.invoke(export, ["--json", "--xml"])
        assert result.exit_code == 1

    def test_authentication_method_selection(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive authentication method selection."""

        @command()
        @exclusive("token", "password", "oauth")
        @option("--token", default=None)
        @option("--password", default=None)
        @option("--oauth", default=None)
        def login(
            token: str | None, password: str | None, oauth: str | None
        ) -> None:
            if token:
                click.echo(f"Logging in with token: {token}")
            elif password:
                click.echo(f"Logging in with password: {password}")
            elif oauth:
                click.echo(f"Logging in with OAuth: {oauth}")

        # Each method alone should work
        result = cli_runner.invoke(login, ["--token", "abc123"])
        assert result.exit_code == 0

        # Multiple methods should fail
        result = cli_runner.invoke(
            login, ["--token", "abc", "--password", "xyz"]
        )
        assert result.exit_code == 1

    def test_verbosity_level_selection(self, cli_runner: CliRunner) -> None:
        """Test exclusive verbosity level selection."""

        @command()
        @exclusive("quiet", "normal", "verbose", "debug")
        @option("--quiet", is_flag=True, default=False)
        @option("--normal", is_flag=True, default=False)
        @option("--verbose", is_flag=True, default=False)
        @option("--debug", is_flag=True, default=False)
        def run(quiet: bool, normal: bool, verbose: bool, debug: bool) -> None:
            if debug:
                click.echo("Level: Debug")
            elif verbose:
                click.echo("Level: Verbose")
            elif normal:
                click.echo("Level: Normal")
            elif quiet:
                click.echo("Level: Quiet")
            else:
                click.echo("Level: Default")

        # Each level alone should work
        result = cli_runner.invoke(run, ["--verbose"])
        assert result.exit_code == 0

        # Multiple levels should fail
        result = cli_runner.invoke(run, ["--quiet", "--verbose"])
        assert result.exit_code == 1
