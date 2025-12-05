"""Tests for deprecated decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.deprecated import deprecated


class TestDeprecatedBasic:
    """Test basic deprecated functionality."""

    def test_deprecated_old_only(self, cli_runner: CliRunner) -> None:
        """Test deprecated with only old parameter name."""

        @command()
        @option("old_flag", default=None)
        @deprecated()
        def cmd(old_flag: str | None) -> None:
            click.echo(f"Flag: {old_flag}")

        result = cli_runner.invoke(cmd, ["--old-flag", "test"])
        assert result.exit_code == 0
        assert "Flag: test" in result.output
        assert "DeprecationWarning" in result.output
        assert (
            "The parameter '--old-flag' has been deprecated." in result.output
        )

    def test_deprecated_with_alternative(self, cli_runner: CliRunner) -> None:
        """Test deprecated with new parameter specified."""

        @command()
        @option("new_opt", default=None)
        @option("old_opt", default=None)
        @deprecated(name="new_opt")
        def cmd(new_opt: str | None, old_opt: str | None) -> None:
            click.echo(f"Value: {old_opt}")

        result = cli_runner.invoke(cmd, ["--old-opt", "value"])
        assert result.exit_code == 0
        assert "Value: value" in result.output
        assert "DeprecationWarning" in result.output
        assert "The parameter '--old-opt' has been deprecated." in result.output
        assert "Use '--new-opt' instead." in result.output

    def test_deprecated_since_version(self, cli_runner: CliRunner) -> None:
        """Test deprecated with since version."""

        @command()
        @option("legacy", default=None)
        @deprecated(since="v1.0.0")
        def cmd(legacy: str | None) -> None:
            click.echo(f"Legacy: {legacy}")

        result = cli_runner.invoke(cmd, ["--legacy", "old"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "deprecated since 'v1.0.0'" in result.output

    def test_deprecated_removed_version(self, cli_runner: CliRunner) -> None:
        """Test deprecated with removal version."""

        @command()
        @option("temp", default=None)
        @deprecated(removed="v3.0.0")
        def cmd(temp: str | None) -> None:
            click.echo(f"Temp: {temp}")

        result = cli_runner.invoke(cmd, ["--temp", "data"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "will be removed in 'v3.0.0'" in result.output


class TestDeprecatedCombinations:
    """Test combinations of deprecated parameters."""

    def test_deprecated_with_since_and_alternative(
        self, cli_runner: CliRunner
    ) -> None:
        """Test deprecated with since and new parameter."""

        @command()
        @option("new", default=None)
        @option("old", default=None)
        @deprecated(name="new", since="v2.0.0")
        def cmd(new: str | None, old: str | None) -> None:
            click.echo(f"Old: {old}")

        result = cli_runner.invoke(cmd, ["--old", "test"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "deprecated since 'v2.0.0'" in result.output
        assert "Use '--new' instead." in result.output

    def test_deprecated_with_removed_and_alternative(
        self, cli_runner: CliRunner
    ) -> None:
        """Test deprecated with removed and new parameter."""

        @command()
        @option("new", default=None)
        @option("old", default=None)
        @deprecated(name="new", removed="v4.0.0")
        def cmd(new: str | None, old: str | None) -> None:
            click.echo(f"Old: {old}")

        result = cli_runner.invoke(cmd, ["--old", "value"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "will be removed in 'v4.0.0'" in result.output
        assert "Use '--new' instead." in result.output

    def test_deprecated_since_and_removed(self, cli_runner: CliRunner) -> None:
        """Test deprecated with since and removed versions."""

        @command()
        @option("phase_out", default=None)
        @deprecated(since="v1.5.0", removed="v2.0.0")
        def cmd(phase_out: str | None) -> None:
            click.echo(f"PhaseOut: {phase_out}")

        result = cli_runner.invoke(cmd, ["--phase-out", "data"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "was deprecated in 'v1.5.0'" in result.output
        assert "will be removed in 'v2.0.0'" in result.output

    def test_deprecated_all_parameters(self, cli_runner: CliRunner) -> None:
        """Test deprecated with all parameters specified."""

        @command()
        @option("replacement", default=None)
        @option("complete", default=None)
        @deprecated(
            name="replacement",
            since="v1.0.0",
            removed="v2.0.0",
        )
        def cmd(replacement: str | None, complete: str | None) -> None:
            click.echo(f"Complete: {complete}")

        result = cli_runner.invoke(cmd, ["--complete", "test"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "was deprecated in 'v1.0.0'" in result.output
        assert "will be removed in 'v2.0.0'" in result.output
        assert "Use '--replacement' instead." in result.output


class TestDeprecatedNoWarning:
    """Test that deprecation warnings only appear when value is provided."""

    def test_no_warning_when_not_provided(self, cli_runner: CliRunner) -> None:
        """Test that no warning appears when parameter not provided."""

        @command()
        @option("opt", default="default_value")
        @deprecated()
        def cmd(opt: str) -> None:
            click.echo(f"Opt: {opt}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Opt: default_value" in result.output
        assert "DeprecationWarning" not in result.output

    def test_warning_when_explicitly_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test warning appears when parameter explicitly provided."""

        @command()
        @option("opt", default="default")
        @deprecated()
        def cmd(opt: str) -> None:
            click.echo(f"Opt: {opt}")

        result = cli_runner.invoke(cmd, ["--opt", "custom"])
        assert result.exit_code == 0
        assert "Opt: custom" in result.output
        assert "DeprecationWarning" in result.output


class TestDeprecatedValuePassthrough:
    """Test that deprecated decorator doesn't modify values."""

    def test_string_value_unchanged(self, cli_runner: CliRunner) -> None:
        """Test string values pass through unchanged."""

        @command()
        @option("text", default=None)
        @deprecated()
        def cmd(text: str | None) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello world"])
        assert result.exit_code == 0
        assert "Text: hello world" in result.output

    def test_integer_value_unchanged(self, cli_runner: CliRunner) -> None:
        """Test integer values pass through unchanged."""

        @command()
        @option("count", type=int, default=0)
        @deprecated()
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "42"])
        assert result.exit_code == 0
        assert "Count: 42" in result.output

    def test_boolean_value_unchanged(self, cli_runner: CliRunner) -> None:
        """Test boolean values pass through unchanged."""

        @command()
        @option("flag", is_flag=True, default=False)
        @deprecated()
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, ["--flag"])
        assert result.exit_code == 0
        assert "Flag: True" in result.output


class TestDeprecatedMultipleOptions:
    """Test deprecated with multiple options."""

    def test_deprecated_on_multiple_options(
        self, cli_runner: CliRunner
    ) -> None:
        """Test multiple deprecated options in same command."""

        @command()
        @option("new2", default=None)
        @option("old2", default=None)
        @deprecated(name="new2")
        @option("new1", default=None)
        @option("old1", default=None)
        @deprecated(name="new1")
        def cmd(
            new2: str | None,
            old2: str | None,
            new1: str | None,
            old1: str | None,
        ) -> None:
            click.echo(f"Old1: {old1}, Old2: {old2}")

        result = cli_runner.invoke(cmd, ["--old1", "a", "--old2", "b"])
        assert result.exit_code == 0
        assert "Old1: a, Old2: b" in result.output
        assert result.output.count("DeprecationWarning") == 2
        assert "--old1" in result.output
        assert "--old2" in result.output

    def test_deprecated_only_one_used(self, cli_runner: CliRunner) -> None:
        """Test only one warning when only one deprecated option used."""

        @command()
        @option("dep1", default=None)
        @deprecated()
        @option("dep2", default=None)
        @deprecated()
        def cmd(dep1: str | None, dep2: str | None) -> None:
            click.echo(f"Dep1: {dep1}, Dep2: {dep2}")

        result = cli_runner.invoke(cmd, ["--dep1", "only"])
        assert result.exit_code == 0
        assert "Dep1: only, Dep2: None" in result.output
        assert result.output.count("DeprecationWarning") == 1


class TestDeprecatedPractical:
    """Test practical real-world use cases."""

    def test_api_key_migration(self, cli_runner: CliRunner) -> None:
        """Test deprecating old API key format."""

        @command()
        @option("token", default=None)
        @option("api_key", default=None)
        @deprecated(
            name="token",
            since="v3.0.0",
            removed="v4.0.0",
        )
        def cmd(token: str | None, api_key: str | None) -> None:
            actual_key = token or api_key
            click.echo(f"Using key: {actual_key}")

        result = cli_runner.invoke(cmd, ["--api-key", "old-key-123"])
        assert result.exit_code == 0
        assert "Using key: old-key-123" in result.output
        assert "DeprecationWarning" in result.output
        assert "--api-key" in result.output
        assert "--token" in result.output

    def test_format_flag_deprecation(self, cli_runner: CliRunner) -> None:
        """Test deprecating format flags."""

        @command()
        @option("json", is_flag=True, default=False)
        @deprecated(
            since="v2.5.0",
            removed="v3.0.0",
        )
        def cmd(json: bool) -> None:
            if json:
                click.echo("Format: JSON")
            else:
                click.echo("Format: default")

        result = cli_runner.invoke(cmd, ["--json"])
        assert result.exit_code == 0
        assert "Format: JSON" in result.output
        assert "DeprecationWarning" in result.output

    def test_short_option_deprecation(self, cli_runner: CliRunner) -> None:
        """Test deprecating short option form."""

        @command()
        @option("verbose", "-v", default=False, is_flag=True)
        @deprecated(removed="v5.0.0")
        def cmd(verbose: bool) -> None:
            click.echo(f"Verbose: {verbose}")

        result = cli_runner.invoke(cmd, ["-v"])
        assert result.exit_code == 0
        assert "Verbose: True" in result.output
        assert "DeprecationWarning" in result.output
        assert "-v" in result.output


class TestDeprecatedEdgeCases:
    """Test edge cases and special scenarios."""

    def test_deprecated_with_none_value(self, cli_runner: CliRunner) -> None:
        """Test deprecated handles None values correctly."""

        @command()
        @option("opt", default=None)
        @deprecated()
        def cmd(opt: str | None) -> None:
            click.echo(f"Opt: {opt}")

        # Providing explicit None-like value
        result = cli_runner.invoke(cmd, ["--opt", ""])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output

    def test_deprecated_custom_parameter_names(
        self, cli_runner: CliRunner
    ) -> None:
        """Test deprecated with custom display names."""

        @command()
        @option("internal_name", default=None)
        @deprecated(
            since="version 2.0",
        )
        def cmd(internal_name: str | None) -> None:
            click.echo(f"Value: {internal_name}")

        result = cli_runner.invoke(cmd, ["--internal-name", "test"])
        assert result.exit_code == 0
        assert "DeprecationWarning" in result.output
        assert "--internal-name" in result.output
        assert "version 2.0" in result.output
