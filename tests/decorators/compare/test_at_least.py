"""Tests for at_least decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.core.decorators.tag import tag
from click_extended.decorators.compare.at_least import at_least


class TestAtLeastBasic:
    """Test basic at_least functionality."""

    def test_at_least_with_exact_required(self, cli_runner: CliRunner) -> None:
        """Test that providing exactly the required number succeeds."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_least(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_at_least_with_more_than_required(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing more than required succeeds."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_least(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c"]
        )
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_at_least_with_less_than_required_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing less than required fails."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_least(2)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a"])
        assert result.exit_code == 1
        assert "At least 2" in result.output
        assert "only 1" in result.output

    def test_at_least_with_none_provided_fails(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing no parameters fails."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @at_least(1)
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 1
        assert "At least 1" in result.output
        assert "only 0" in result.output


class TestAtLeastOne:
    """Test at_least(1) - at least one required."""

    def test_at_least_one_with_one_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test at_least(1) succeeds with one parameter."""

        @command()
        @option("--username", default=None, tags="auth")
        @option("--email", default=None, tags="auth")
        @option("--phone", default=None, tags="auth")
        @tag("auth")
        @at_least(1)
        def cmd(
            username: str | None, email: str | None, phone: str | None
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--username", "john"])
        assert result.exit_code == 0

    def test_at_least_one_with_none_fails(self, cli_runner: CliRunner) -> None:
        """Test at_least(1) fails with no parameters."""

        @command()
        @option("--username", default=None, tags="auth")
        @option("--email", default=None, tags="auth")
        @option("--phone", default=None, tags="auth")
        @tag("auth")
        @at_least(1)
        def cmd(
            username: str | None, email: str | None, phone: str | None
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 1
        assert "At least 1" in result.output


class TestAtLeastMultiple:
    """Test at_least with various requirements."""

    def test_at_least_all_required(self, cli_runner: CliRunner) -> None:
        """Test requiring all parameters."""

        @command()
        @option("--a", default=None, tags="all")
        @option("--b", default=None, tags="all")
        @option("--c", default=None, tags="all")
        @tag("all")
        @at_least(3)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        # All three - should succeed
        result = cli_runner.invoke(cmd, ["--a", "1", "--b", "2", "--c", "3"])
        assert result.exit_code == 0

        # Only two - should fail
        result = cli_runner.invoke(cmd, ["--a", "1", "--b", "2"])
        assert result.exit_code == 1
        assert "At least 3" in result.output

    def test_at_least_with_five_params(self, cli_runner: CliRunner) -> None:
        """Test at_least with multiple parameters."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @option("--opt4", default=None, tags="group")
        @option("--opt5", default=None, tags="group")
        @tag("group")
        @at_least(3)
        def cmd(
            opt1: str | None,
            opt2: str | None,
            opt3: str | None,
            opt4: str | None,
            opt5: str | None,
        ) -> None:
            click.echo("Success")

        # Exactly 3 - should succeed
        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c"]
        )
        assert result.exit_code == 0

        # Only 2 - should fail
        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 1


class TestAtLeastWithFlags:
    """Test at_least with boolean flags."""

    def test_at_least_with_flags(self, cli_runner: CliRunner) -> None:
        """Test at_least works with boolean flags."""

        @command()
        @option("--flag1", is_flag=True, default=False, tags="flags")
        @option("--flag2", is_flag=True, default=False, tags="flags")
        @option("--flag3", is_flag=True, default=False, tags="flags")
        @tag("flags")
        @at_least(2)
        def cmd(flag1: bool, flag2: bool, flag3: bool) -> None:
            click.echo("Success")

        # Two flags - should succeed
        result = cli_runner.invoke(cmd, ["--flag1", "--flag2"])
        assert result.exit_code == 0

        # One flag - should fail
        result = cli_runner.invoke(cmd, ["--flag1"])
        assert result.exit_code == 1


class TestAtLeastErrorMessages:
    """Test error message formatting."""

    def test_error_message_shows_count(self, cli_runner: CliRunner) -> None:
        """Test error message shows required and provided counts."""

        @command()
        @option("--a", default=None, tags="group")
        @option("--b", default=None, tags="group")
        @option("--c", default=None, tags="group")
        @tag("group")
        @at_least(2)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--a", "1"])
        assert result.exit_code == 1
        assert "At least 2" in result.output
        assert "only 1 was given" in result.output

    def test_error_message_grammar_plural(self, cli_runner: CliRunner) -> None:
        """Test error message uses correct grammar for plural."""

        @command()
        @option("--a", default=None, tags="group")
        @option("--b", default=None, tags="group")
        @option("--c", default=None, tags="group")
        @tag("group")
        @at_least(3)
        def cmd(a: str | None, b: str | None, c: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 1
        assert "0 were given" in result.output

    def test_error_message_shows_param_names(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message shows parameter names."""

        @command()
        @option("--username", default=None, tags="auth")
        @option("--email", default=None, tags="auth")
        @tag("auth")
        @at_least(1)
        def cmd(username: str | None, email: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 1
        assert "username" in result.output
        assert "email" in result.output


class TestAtLeastPractical:
    """Test practical real-world use cases."""

    def test_contact_info_requirement(self, cli_runner: CliRunner) -> None:
        """Test requiring at least one contact method."""

        @command()
        @option("--email", default=None, tags="contact")
        @option("--phone", default=None, tags="contact")
        @option("--address", default=None, tags="contact")
        @tag("contact")
        @at_least(1)
        def register(
            email: str | None, phone: str | None, address: str | None
        ) -> None:
            click.echo("Registration successful")

        # With email - should succeed
        result = cli_runner.invoke(register, ["--email", "test@example.com"])
        assert result.exit_code == 0

        # Without any contact - should fail
        result = cli_runner.invoke(register, [])
        assert result.exit_code == 1

    def test_payment_method_requirement(self, cli_runner: CliRunner) -> None:
        """Test requiring at least one payment method."""

        @command()
        @option("--card", default=None, tags="payment")
        @option("--paypal", default=None, tags="payment")
        @option("--bank", default=None, tags="payment")
        @tag("payment")
        @at_least(1)
        def checkout(
            card: str | None, paypal: str | None, bank: str | None
        ) -> None:
            click.echo("Payment processed")

        result = cli_runner.invoke(checkout, ["--card", "1234"])
        assert result.exit_code == 0

        result = cli_runner.invoke(checkout, [])
        assert result.exit_code == 1
