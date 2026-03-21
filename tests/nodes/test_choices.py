"""Tests for the choices parameter on @option and @argument."""

from typing import Any

import pytest
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# @option choices
# ---------------------------------------------------------------------------


class TestOptionChoicesValidation:
    """Validate choices enforcement at decorator-definition time."""

    def test_empty_choices_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one choice"):

            @command()
            @option("color", choices=())
            def cmd(color: str) -> None: ...

    def test_invalid_choice_type_raises(self) -> None:
        with pytest.raises(TypeError, match="str, int, or float"):

            @command()
            @option("color", choices=(["bad"],))  # type: ignore[arg-type]
            def cmd(color: str) -> None: ...


class TestOptionChoicesRuntime:
    """Check that valid choices pass and invalid choices fail at runtime."""

    def _make_cmd(self, **kwargs: Any) -> Any:
        @command()
        @option("env", choices=("staging", "production"), **kwargs)
        def deploy(env: str) -> None:
            print(f"env={env}")

        return deploy

    def test_valid_choice_accepted(self, runner: CliRunner) -> None:
        result = runner.invoke(self._make_cmd(), ["--env", "staging"])
        assert result.exit_code == 0
        assert "env=staging" in result.output

    def test_invalid_choice_rejected(self, runner: CliRunner) -> None:
        result = runner.invoke(self._make_cmd(), ["--env", "dev"])
        assert result.exit_code != 0

    def test_case_sensitive_default_rejects_wrong_case(self, runner: CliRunner) -> None:
        result = runner.invoke(self._make_cmd(), ["--env", "Staging"])
        assert result.exit_code != 0

    def test_case_insensitive_accepts_wrong_case(self, runner: CliRunner) -> None:
        @command()
        @option("color", choices=("red", "green", "blue"), case_sensitive=False)
        def cmd(color: str) -> None:
            print(f"color={color}")

        result = runner.invoke(cmd, ["--color", "RED"])
        assert result.exit_code == 0
        assert "color=RED" in result.output


class TestOptionChoicesIntAndFloat:
    """Choices work for integer and float options."""

    def test_int_choice_valid(self, runner: CliRunner) -> None:
        @command()
        @option("port", type=int, choices=(80, 443, 8080))
        def cmd(port: int) -> None:
            print(f"port={port}")

        result = runner.invoke(cmd, ["--port", "443"])
        assert result.exit_code == 0
        assert "port=443" in result.output

    def test_int_choice_invalid(self, runner: CliRunner) -> None:
        @command()
        @option("port", type=int, choices=(80, 443, 8080))
        def cmd(port: int) -> None:
            print(f"port={port}")

        result = runner.invoke(cmd, ["--port", "9000"])
        assert result.exit_code != 0

    def test_float_choice_valid(self, runner: CliRunner) -> None:
        @command()
        @option("ratio", type=float, choices=(0.5, 1.0, 2.0))
        def cmd(ratio: float) -> None:
            print(f"ratio={ratio}")

        result = runner.invoke(cmd, ["--ratio", "1.0"])
        assert result.exit_code == 0


class TestOptionChoicesMultiple:
    """Choices validate each value in multiple-option tuples."""

    def test_multiple_all_valid(self, runner: CliRunner) -> None:
        @command()
        @option("env", multiple=True, choices=("staging", "production"))
        def cmd(env: tuple[str, ...]) -> None:
            print(",".join(env))

        result = runner.invoke(cmd, ["--env", "staging", "--env", "production"])
        assert result.exit_code == 0

    def test_multiple_one_invalid(self, runner: CliRunner) -> None:
        @command()
        @option("env", multiple=True, choices=("staging", "production"))
        def cmd(env: tuple[str, ...]) -> None:
            print(",".join(env))

        result = runner.invoke(cmd, ["--env", "staging", "--env", "dev"])
        assert result.exit_code != 0


class TestOptionChoicesHelpText:
    """choices display is appended to option help."""

    def test_choices_shown_in_help(self, runner: CliRunner) -> None:
        @command()
        @option("env", help="Target environment.", choices=("staging", "production"))
        def cmd(env: str) -> None: ...

        result = runner.invoke(cmd, ["--help"])
        assert "[staging|production]" in result.output

    def test_choices_shown_in_help_no_existing_help(self, runner: CliRunner) -> None:
        @command()
        @option("env", choices=("staging", "production"))
        def cmd(env: str) -> None: ...

        result = runner.invoke(cmd, ["--help"])
        assert "[staging|production]" in result.output


# ---------------------------------------------------------------------------
# @argument choices
# ---------------------------------------------------------------------------


class TestArgumentChoicesRuntime:
    """choices enforcement for positional @argument."""

    def test_valid_argument_choice(self, runner: CliRunner) -> None:
        @command()
        @argument("env", choices=("staging", "production"))
        def cmd(env: str) -> None:
            print(f"env={env}")

        result = runner.invoke(cmd, ["staging"])
        assert result.exit_code == 0
        assert "env=staging" in result.output

    def test_invalid_argument_choice(self, runner: CliRunner) -> None:
        @command()
        @argument("env", choices=("staging", "production"))
        def cmd(env: str) -> None:
            print(f"env={env}")

        result = runner.invoke(cmd, ["dev"])
        assert result.exit_code != 0

    def test_argument_case_insensitive(self, runner: CliRunner) -> None:
        @command()
        @argument("env", choices=("staging", "production"), case_sensitive=False)
        def cmd(env: str) -> None:
            print(f"env={env}")

        result = runner.invoke(cmd, ["STAGING"])
        assert result.exit_code == 0

    def test_argument_empty_choices_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one choice"):

            @command()
            @argument("env", choices=())
            def cmd(env: str) -> None: ...
