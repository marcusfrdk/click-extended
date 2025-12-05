"""Tests for experimental decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.misc.experimental import experimental


class TestExperimentalBasic:
    """Test basic experimental functionality."""

    def test_experimental_no_params(self, cli_runner: CliRunner) -> None:
        """Test experimental with no parameters."""

        @command()
        @option("exp_flag", default=None)
        @experimental()
        def cmd(exp_flag: str | None) -> None:
            click.echo(f"Flag: {exp_flag}")

        result = cli_runner.invoke(cmd, ["--exp-flag", "test"])
        assert result.exit_code == 0
        assert "Flag: test" in result.output
        assert "ExperimentalWarning" in result.output
        assert "The parameter '--exp-flag' is experimental." in result.output

    def test_experimental_since_version(self, cli_runner: CliRunner) -> None:
        """Test experimental with since version."""

        @command()
        @option("new_opt", default=None)
        @experimental(since="v2.0.0")
        def cmd(new_opt: str | None) -> None:
            click.echo(f"Value: {new_opt}")

        result = cli_runner.invoke(cmd, ["--new-opt", "value"])
        assert result.exit_code == 0
        assert "Value: value" in result.output
        assert "ExperimentalWarning" in result.output
        assert (
            "The parameter '--new-opt' is experimental since 'v2.0.0'."
            in result.output
        )

    def test_experimental_stable_version(self, cli_runner: CliRunner) -> None:
        """Test experimental with stable version."""

        @command()
        @option("beta", default=None)
        @experimental(stable="v3.0.0")
        def cmd(beta: str | None) -> None:
            click.echo(f"Beta: {beta}")

        result = cli_runner.invoke(cmd, ["--beta", "test"])
        assert result.exit_code == 0
        assert "ExperimentalWarning" in result.output
        assert (
            "The parameter '--beta' is experimental and will stable in 'v3.0.0'."
            in result.output
        )

    def test_experimental_custom_message(self, cli_runner: CliRunner) -> None:
        """Test experimental with custom message."""

        @command()
        @option("alpha", default=None)
        @experimental(message="This feature is still under development!")
        def cmd(alpha: str | None) -> None:
            click.echo(f"Alpha: {alpha}")

        result = cli_runner.invoke(cmd, ["--alpha", "data"])
        assert result.exit_code == 0
        assert "ExperimentalWarning" in result.output
        assert "This feature is still under development!" in result.output


class TestExperimentalCombinations:
    """Test combinations of experimental parameters."""

    def test_experimental_since_and_stable(self, cli_runner: CliRunner) -> None:
        """Test experimental with both since and stable versions."""

        @command()
        @option("preview", default=None)
        @experimental(since="v1.5.0", stable="v2.0.0")
        def cmd(preview: str | None) -> None:
            click.echo(f"Preview: {preview}")

        result = cli_runner.invoke(cmd, ["--preview", "test"])
        assert result.exit_code == 0
        assert "ExperimentalWarning" in result.output
        assert (
            "The parameter '--preview' is experimental since 'v1.5.0' "
            "and will stable in 'v2.0.0'." in result.output
        )

    def test_experimental_custom_message_ignores_versions(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that custom message takes precedence over version info."""

        @command()
        @option("feature", default=None)
        @experimental(
            message="Custom warning!", since="v1.0.0", stable="v2.0.0"
        )
        def cmd(feature: str | None) -> None:
            click.echo(f"Feature: {feature}")

        result = cli_runner.invoke(cmd, ["--feature", "test"])
        assert result.exit_code == 0
        assert "Custom warning!" in result.output
        assert "v1.0.0" not in result.output
        assert "v2.0.0" not in result.output


class TestExperimentalNoWarning:
    """Test that experimental doesn't warn when not used."""

    def test_experimental_not_provided_default_none(
        self, cli_runner: CliRunner
    ) -> None:
        """Test no warning when experimental option not provided."""

        @command()
        @option("exp_opt", default=None)
        @experimental()
        def cmd(exp_opt: str | None) -> None:
            click.echo(f"Value: {exp_opt}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "ExperimentalWarning" not in result.output

    def test_experimental_not_provided_with_default(
        self, cli_runner: CliRunner
    ) -> None:
        """Test no warning when using default value."""

        @command()
        @option("exp_flag", default="default_value")
        @experimental()
        def cmd(exp_flag: str) -> None:
            click.echo(f"Flag: {exp_flag}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Flag: default_value" in result.output
        assert "ExperimentalWarning" not in result.output


class TestExperimentalValuePassthrough:
    """Test that experimental passes values through correctly."""

    def test_experimental_string_value(self, cli_runner: CliRunner) -> None:
        """Test experimental passes string values correctly."""

        @command()
        @option("text", default=None)
        @experimental()
        def cmd(text: str | None) -> None:
            click.echo(f"Text: {text}")

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0
        assert "Text: hello" in result.output

    def test_experimental_integer_value(self, cli_runner: CliRunner) -> None:
        """Test experimental passes integer values correctly."""

        @command()
        @option("count", default=0, type=int)
        @experimental()
        def cmd(count: int) -> None:
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(cmd, ["--count", "42"])
        assert result.exit_code == 0
        assert "Count: 42" in result.output

    def test_experimental_boolean_value(self, cli_runner: CliRunner) -> None:
        """Test experimental passes boolean values correctly."""

        @command()
        @option("flag", default=False, is_flag=True)
        @experimental()
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd, ["--flag"])
        assert result.exit_code == 0
        assert "Flag: True" in result.output


class TestExperimentalMultipleOptions:
    """Test experimental with multiple options."""

    def test_experimental_multiple_options_all_used(
        self, cli_runner: CliRunner
    ) -> None:
        """Test multiple experimental options when all are used."""

        @command()
        @option("exp1", default=None)
        @experimental()
        @option("exp2", default=None)
        @experimental()
        def cmd(exp1: str | None, exp2: str | None) -> None:
            click.echo(f"Exp1: {exp1}, Exp2: {exp2}")

        result = cli_runner.invoke(cmd, ["--exp1", "a", "--exp2", "b"])
        assert result.exit_code == 0
        assert "Exp1: a, Exp2: b" in result.output
        # Should see two warnings
        assert result.output.count("ExperimentalWarning") == 2

    def test_experimental_multiple_options_one_used(
        self, cli_runner: CliRunner
    ) -> None:
        """Test multiple experimental options when only one is used."""

        @command()
        @option("exp1", default=None)
        @experimental()
        @option("exp2", default=None)
        @experimental()
        def cmd(exp1: str | None, exp2: str | None) -> None:
            click.echo(f"Exp1: {exp1}, Exp2: {exp2}")

        result = cli_runner.invoke(cmd, ["--exp1", "a"])
        assert result.exit_code == 0
        assert "Exp1: a, Exp2: None" in result.output
        # Should see only one warning
        assert result.output.count("ExperimentalWarning") == 1


class TestExperimentalPractical:
    """Test practical use cases of experimental."""

    def test_experimental_api_flag(self, cli_runner: CliRunner) -> None:
        """Test experimental flag for new API features."""

        @command()
        @option("use_new_api", default=False, is_flag=True)
        @experimental(
            since="v2.1.0",
            stable="v3.0.0",
        )
        def cmd(use_new_api: bool) -> None:
            if use_new_api:
                click.echo("Using new API")
            else:
                click.echo("Using old API")

        result = cli_runner.invoke(cmd, ["--use-new-api"])
        assert result.exit_code == 0
        assert "Using new API" in result.output
        assert "ExperimentalWarning" in result.output

    def test_experimental_format_option(self, cli_runner: CliRunner) -> None:
        """Test experimental output format option."""

        @command()
        @option("format", default="json")
        @experimental(message="YAML format is experimental and may change!")
        def cmd(format: str) -> None:
            click.echo(f"Format: {format}")

        result = cli_runner.invoke(cmd, ["--format", "yaml"])
        assert result.exit_code == 0
        assert "Format: yaml" in result.output
        assert "YAML format is experimental" in result.output

    def test_experimental_performance_flag(self, cli_runner: CliRunner) -> None:
        """Test experimental performance optimization flag."""

        @command()
        @option("turbo", default=False, is_flag=True)
        @experimental(stable="v2.5.0")
        def cmd(turbo: bool) -> None:
            mode = "turbo" if turbo else "normal"
            click.echo(f"Mode: {mode}")

        result = cli_runner.invoke(cmd, ["--turbo"])
        assert result.exit_code == 0
        assert "Mode: turbo" in result.output
        assert "will stable in 'v2.5.0'" in result.output


class TestExperimentalEdgeCases:
    """Test edge cases for experimental."""

    def test_experimental_empty_string_value(
        self, cli_runner: CliRunner
    ) -> None:
        """Test experimental with empty string value."""

        @command()
        @option("text", default=None)
        @experimental()
        def cmd(text: str | None) -> None:
            click.echo(f"Text: '{text}'")

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0
        assert "Text: ''" in result.output
        assert "ExperimentalWarning" in result.output

    def test_experimental_special_characters_in_message(
        self, cli_runner: CliRunner
    ) -> None:
        """Test experimental with special characters in message."""

        @command()
        @option("special", default=None)
        @experimental(message="Warning: Use at your own risk! (◉_◉)")
        def cmd(special: str | None) -> None:
            click.echo(f"Special: {special}")

        result = cli_runner.invoke(cmd, ["--special", "test"])
        assert result.exit_code == 0
        assert "Warning: Use at your own risk! (◉_◉)" in result.output
