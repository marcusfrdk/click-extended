"""Tests for random_string decorator."""

from string import ascii_lowercase, ascii_uppercase, digits, punctuation

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.random.random_string import random_string


class TestRandomStringBasic:
    """Test basic random_string functionality."""

    def test_generates_default_length(self, cli_runner: CliRunner) -> None:
        """Test that default length is 8 characters."""

        @command()
        @random_string("token", seed=42)
        def cmd(token: str) -> None:
            click.echo(f"Token: {token}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        # Extract the token from output
        token = result.output.split("Token: ")[1].strip()
        assert len(token) == 8

    def test_generates_custom_length(self, cli_runner: CliRunner) -> None:
        """Test custom length parameter."""

        @command()
        @random_string("code", length=16, seed=100)
        def cmd(code: str) -> None:
            click.echo(f"Code: {code}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        code = result.output.split("Code: ")[1].strip()
        assert len(code) == 16

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that multiple invocations with different seeds generate different values."""

        results = []
        for i in range(5):

            @command()
            @random_string("value", length=16, seed=200 + i)
            def cmd(value: str) -> None:
                click.echo(f"Value: {value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All results should be different (different seeds)
        assert len(set(results)) == 5


class TestRandomStringCharacterSets:
    """Test character set filtering options."""

    def test_lowercase_only(self, cli_runner: CliRunner) -> None:
        """Test lowercase only option."""

        @command()
        @random_string(
            "value",
            length=20,
            lowercase=True,
            uppercase=False,
            numbers=False,
            symbols=False,
            seed=300,
        )
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()
        assert all(c in ascii_lowercase for c in value)
        assert len(value) == 20

    def test_uppercase_only(self, cli_runner: CliRunner) -> None:
        """Test uppercase only option."""

        @command()
        @random_string(
            "value",
            length=20,
            lowercase=False,
            uppercase=True,
            numbers=False,
            symbols=False,
            seed=301,
        )
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()
        assert all(c in ascii_uppercase for c in value)

    def test_numbers_only(self, cli_runner: CliRunner) -> None:
        """Test numbers only option."""

        @command()
        @random_string(
            "value",
            length=20,
            lowercase=False,
            uppercase=False,
            numbers=True,
            symbols=False,
            seed=302,
        )
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()
        assert all(c in digits for c in value)

    def test_symbols_only(self, cli_runner: CliRunner) -> None:
        """Test symbols only option."""

        @command()
        @random_string(
            "value",
            length=20,
            lowercase=False,
            uppercase=False,
            numbers=False,
            symbols=True,
            seed=303,
        )
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()
        assert all(c in punctuation for c in value)

    def test_alphanumeric_no_symbols(self, cli_runner: CliRunner) -> None:
        """Test alphanumeric without symbols."""

        @command()
        @random_string("token", length=100, symbols=False, seed=304)
        def cmd(token: str) -> None:
            click.echo(f"Token: {token}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        token = result.output.split("Token: ")[1].strip()
        allowed = ascii_lowercase + ascii_uppercase + digits
        assert all(c in allowed for c in token)
        # With 100 chars, should statistically contain mix of character types
        assert any(c in ascii_lowercase for c in token)
        assert any(c in ascii_uppercase for c in token)
        assert any(c in digits for c in token)

    def test_all_character_types(self, cli_runner: CliRunner) -> None:
        """Test with all character types enabled (default)."""

        @command()
        @random_string("password", length=50, seed=305)
        def cmd(password: str) -> None:
            click.echo(f"Password: {password}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        password = result.output.split("Password: ")[1].strip()

        # With 50 characters and all types, we should see all character types
        # (statistically extremely likely)
        assert any(c in ascii_lowercase for c in password)
        assert any(c in ascii_uppercase for c in password)
        assert any(c in digits for c in password)
        assert any(c in punctuation for c in password)


class TestRandomStringEdgeCases:
    """Test edge cases and error conditions."""

    def test_length_one(self, cli_runner: CliRunner) -> None:
        """Test minimum length of 1."""

        @command()
        @random_string("value", length=1, seed=400)
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()
        assert len(value) == 1

    def test_long_string(self, cli_runner: CliRunner) -> None:
        """Test generating a very long string."""

        @command()
        @random_string("value", length=1000, seed=401)
        def cmd(value: str) -> None:
            click.echo(f"Length: {len(value)}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Length: 1000" in result.output

    def test_lowercase_and_numbers_only(self, cli_runner: CliRunner) -> None:
        """Test combination of lowercase and numbers."""

        @command()
        @random_string(
            "code",
            length=20,
            lowercase=True,
            uppercase=False,
            numbers=True,
            symbols=False,
            seed=402,
        )
        def cmd(code: str) -> None:
            click.echo(f"Code: {code}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        code = result.output.split("Code: ")[1].strip()
        allowed = ascii_lowercase + digits
        assert all(c in allowed for c in code)


class TestRandomStringIntegration:
    """Test random_string integration with other decorators."""

    def test_multiple_random_strings(self, cli_runner: CliRunner) -> None:
        """Test multiple random_string decorators on same command."""

        @command()
        @random_string("token", length=16, symbols=False, seed=500)
        @random_string("password", length=20, seed=501)
        def cmd(token: str, password: str) -> None:
            click.echo(f"Token: {token}")
            click.echo(f"Password: {password}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        output = result.output

        token = output.split("Token: ")[1].split("\n")[0].strip()
        password = output.split("Password: ")[1].strip()

        assert len(token) == 16
        assert len(password) == 20
        assert token != password

    def test_respects_default_none(self, cli_runner: CliRunner) -> None:
        """Test that decorator generates value when default is None."""

        @command()
        @random_string("token", length=16, seed=502)
        def cmd(token: str) -> None:
            click.echo(f"Token: {token}")
            click.echo(f"Length: {len(token)}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Length: 16" in result.output
        # Verify it's actually a string, not None
        assert "Token: None" not in result.output

    def test_randomness_quality(self, cli_runner: CliRunner) -> None:
        """Test that generated strings have good randomness."""

        @command()
        @random_string("value", length=100, seed=503)
        def cmd(value: str) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = result.output.split("Value: ")[1].strip()

        # Check that we don't have obvious patterns like repeated characters
        # Count consecutive duplicates
        max_consecutive = max(
            len(list(group))
            for _, group in __import__("itertools").groupby(value)
        )
        # With 100 random characters, we shouldn't see more than 4-5 consecutive
        assert max_consecutive < 6, "String appears to have suspicious patterns"
