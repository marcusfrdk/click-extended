"""Tests for random_integer decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.random.random_integer import random_integer


class TestRandomIntegerBasic:
    """Test basic random_integer functionality."""

    def test_generates_within_default_range(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that default range is 0-100."""

        @command()
        @random_integer("value", seed=1000)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())
        assert 0 <= value <= 100

    def test_generates_within_custom_range(self, cli_runner: CliRunner) -> None:
        """Test custom range parameter."""

        @command()
        @random_integer("age", min_value=18, max_value=65, seed=1001)
        def cmd(age: int) -> None:
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        age = int(result.output.split("Age: ")[1].strip())
        assert 18 <= age <= 65

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that multiple invocations generate different values."""

        values = []
        for i in range(10):

            @command()
            @random_integer("value", min_value=0, max_value=1000, seed=1002 + i)
            def cmd(value: int) -> None:
                click.echo(f"Value: {value}")

            result = cli_runner.invoke(cmd)
            values.append(int(result.output.split("Value: ")[1].strip()))
        # With range 0-1000, we should have at least some variety
        assert len(set(values)) > 1

    def test_single_value_range(self, cli_runner: CliRunner) -> None:
        """Test when min and max are the same."""

        @command()
        @random_integer("value", min_value=42, max_value=42, seed=1012)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())
        assert value == 42


class TestRandomIntegerRanges:
    """Test various range configurations."""

    def test_negative_range(self, cli_runner: CliRunner) -> None:
        """Test negative number range."""

        @command()
        @random_integer("value", min_value=-100, max_value=-10, seed=1013)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())
        assert -100 <= value <= -10

    def test_mixed_range(self, cli_runner: CliRunner) -> None:
        """Test range crossing zero."""

        @command()
        @random_integer("value", min_value=-50, max_value=50, seed=1014)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())
        assert -50 <= value <= 50

    def test_large_range(self, cli_runner: CliRunner) -> None:
        """Test very large range."""

        @command()
        @random_integer("value", min_value=0, max_value=1_000_000, seed=1015)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())
        assert 0 <= value <= 1_000_000


class TestRandomIntegerErrors:
    """Test error conditions."""

    def test_invalid_range_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that min > max raises ValueError."""

        @command()
        @random_integer("value", min_value=100, max_value=10, seed=1016)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "min_value can not be larger than max_value" in result.output


class TestRandomIntegerDistribution:
    """Test distribution properties."""

    def test_includes_boundaries(self, cli_runner: CliRunner) -> None:
        """Test that both min and max values can be generated."""

        # Run multiple times to likely hit boundaries
        values = set()
        for i in range(50):

            @command()
            @random_integer("value", min_value=1, max_value=3, seed=1050 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = int(result.output.strip())
            values.add(value)

        # Should have seen 1, 2, and 3
        assert values == {1, 2, 3}

    def test_reasonable_distribution(self, cli_runner: CliRunner) -> None:
        """Test that distribution is reasonably uniform."""

        # Collect sample
        values = []
        for i in range(100):

            @command()
            @random_integer("value", min_value=0, max_value=9, seed=1100 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = int(result.output.strip())
            values.append(value)

        # Should see most digits (not a strict statistical test)
        unique_values = len(set(values))
        assert unique_values >= 7  # At least 7 out of 10 digits


class TestRandomIntegerIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_integers(self, cli_runner: CliRunner) -> None:
        """Test multiple random_integer decorators."""

        @command()
        @random_integer("age", min_value=18, max_value=65, seed=1200)
        @random_integer("score", min_value=0, max_value=100, seed=1201)
        def cmd(age: int, score: int) -> None:
            click.echo(f"Age: {age}, Score: {score}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        output = result.output.strip()

        age = int(output.split("Age: ")[1].split(",")[0])
        score = int(output.split("Score: ")[1])

        assert 18 <= age <= 65
        assert 0 <= score <= 100
        assert age != score or (age == score and 18 <= age <= 65)
