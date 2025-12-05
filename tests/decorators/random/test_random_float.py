"""Tests for random_float decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.random.random_float import random_float


class TestRandomFloatBasic:
    """Test basic random_float functionality."""

    def test_generates_within_default_range(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that default range is 0.0-1.0."""

        @command()
        @random_float("value", seed=2000)
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = float(result.output.split("Value: ")[1].strip())
        assert 0.0 <= value <= 1.0

    def test_generates_within_custom_range(self, cli_runner: CliRunner) -> None:
        """Test custom range parameter."""

        @command()
        @random_float("price", min_value=10.0, max_value=100.0, seed=2001)
        def cmd(price: float) -> None:
            click.echo(f"Price: {price}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        price = float(result.output.split("Price: ")[1].strip())
        assert 10.0 <= price <= 100.0

    def test_default_decimals(self, cli_runner: CliRunner) -> None:
        """Test default decimals is 3."""

        @command()
        @random_float("value", seed=2002)
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value_str = result.output.split("Value: ")[1].strip()

        # Check decimal places (may be fewer if trailing zeros)
        if "." in value_str:
            decimal_places = len(value_str.split(".")[1])
            assert decimal_places <= 3

    def test_custom_decimals(self, cli_runner: CliRunner) -> None:
        """Test custom decimal places."""

        @command()
        @random_float(
            "ratio", min_value=0.0, max_value=1.0, decimals=5, seed=2003
        )
        def cmd(ratio: float) -> None:
            click.echo(f"Ratio: {ratio}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        ratio_str = result.output.split("Ratio: ")[1].strip()

        if "." in ratio_str:
            decimal_places = len(ratio_str.split(".")[1])
            assert decimal_places <= 5

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that multiple invocations generate different values."""

        results = []
        for i in range(10):

            @command()
            @random_float(
                "value", min_value=0.0, max_value=100.0, seed=2004 + i
            )
            def cmd(value: float) -> None:
                click.echo(f"Value: {value}")

            results.append(cli_runner.invoke(cmd).output)
        values = [float(r.split("Value: ")[1].strip()) for r in results]
        # Should have variety
        assert len(set(values)) > 1


class TestRandomFloatRanges:
    """Test various range configurations."""

    def test_negative_range(self, cli_runner: CliRunner) -> None:
        """Test negative number range."""

        @command()
        @random_float("temp", min_value=-50.0, max_value=-10.0, seed=2014)
        def cmd(temp: float) -> None:
            click.echo(f"Temp: {temp}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        temp = float(result.output.split("Temp: ")[1].strip())
        assert -50.0 <= temp <= -10.0

    def test_mixed_range(self, cli_runner: CliRunner) -> None:
        """Test range crossing zero."""

        @command()
        @random_float("value", min_value=-25.5, max_value=25.5, seed=2015)
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = float(result.output.split("Value: ")[1].strip())
        assert -25.5 <= value <= 25.5

    def test_large_range(self, cli_runner: CliRunner) -> None:
        """Test very large range."""

        @command()
        @random_float("value", min_value=0.0, max_value=1_000_000.0, seed=2016)
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = float(result.output.split("Value: ")[1].strip())
        assert 0.0 <= value <= 1_000_000.0

    def test_small_range(self, cli_runner: CliRunner) -> None:
        """Test very small range with high precision."""

        @command()
        @random_float(
            "epsilon", min_value=0.0001, max_value=0.0002, decimals=6, seed=2017
        )
        def cmd(epsilon: float) -> None:
            click.echo(f"Epsilon: {epsilon}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        epsilon = float(result.output.split("Epsilon: ")[1].strip())
        assert 0.0001 <= epsilon <= 0.0002


class TestRandomFloatDecimals:
    """Test decimal place handling."""

    def test_zero_decimals(self, cli_runner: CliRunner) -> None:
        """Test with 0 decimal places (whole numbers)."""

        @command()
        @random_float(
            "value", min_value=10.0, max_value=20.0, decimals=0, seed=2018
        )
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = float(result.output.split("Value: ")[1].strip())
        assert value == int(value)  # Should be whole number

    def test_one_decimal(self, cli_runner: CliRunner) -> None:
        """Test with 1 decimal place."""

        @command()
        @random_float(
            "score", min_value=0.0, max_value=10.0, decimals=1, seed=2019
        )
        def cmd(score: float) -> None:
            click.echo(f"Score: {score}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        score_str = result.output.split("Score: ")[1].strip()

        # Verify rounding
        if "." in score_str:
            decimal_places = len(score_str.split(".")[1])
            assert decimal_places <= 1

    def test_many_decimals(self, cli_runner: CliRunner) -> None:
        """Test with many decimal places."""

        @command()
        @random_float(
            "precise", min_value=0.0, max_value=1.0, decimals=10, seed=2020
        )
        def cmd(precise: float) -> None:
            click.echo(f"Precise: {precise}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        precise_str = result.output.split("Precise: ")[1].strip()

        if "." in precise_str:
            decimal_places = len(precise_str.split(".")[1])
            assert decimal_places <= 10


class TestRandomFloatErrors:
    """Test error conditions."""

    def test_invalid_range_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that min > max raises ValueError."""

        @command()
        @random_float("value", min_value=100.0, max_value=10.0, seed=2021)
        def cmd(value: float) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "min_value can not be larger than max_value" in result.output


class TestRandomFloatDistribution:
    """Test distribution properties."""

    def test_includes_approximate_boundaries(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that values near boundaries can be generated."""

        # Collect samples
        values = []
        for i in range(100):

            @command()
            @random_float(
                "value", min_value=0.0, max_value=1.0, decimals=1, seed=2022 + i
            )
            def cmd(value: float) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = float(result.output.strip())
            values.append(value)

        # Should see values near both ends
        assert any(v < 0.2 for v in values)  # Near min
        assert any(v > 0.8 for v in values)  # Near max

    def test_coverage_across_range(self, cli_runner: CliRunner) -> None:
        """Test that values cover the range."""

        values = []
        for i in range(50):

            @command()
            @random_float(
                "value",
                min_value=0.0,
                max_value=10.0,
                decimals=0,
                seed=2122 + i,
            )
            def cmd(value: float) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = float(result.output.strip())
            values.append(value)

        # Should see variety across the range
        unique_values = len(set(values))
        assert unique_values >= 5  # At least half the range


class TestRandomFloatIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_floats(self, cli_runner: CliRunner) -> None:
        """Test multiple random_float decorators."""

        @command()
        @random_float(
            "price", min_value=10.0, max_value=100.0, decimals=2, seed=2172
        )
        @random_float(
            "discount", min_value=0.0, max_value=1.0, decimals=2, seed=2173
        )
        def cmd(price: float, discount: float) -> None:
            click.echo(f"Price: {price}, Discount: {discount}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        output = result.output.strip()

        price = float(output.split("Price: ")[1].split(",")[0])
        discount = float(output.split("Discount: ")[1])

        assert 10.0 <= price <= 100.0
        assert 0.0 <= discount <= 1.0

    def test_same_range_different_decimals(self, cli_runner: CliRunner) -> None:
        """Test same range with different decimal precision."""

        @command()
        @random_float(
            "rough", min_value=0.0, max_value=10.0, decimals=1, seed=2174
        )
        @random_float(
            "precise", min_value=0.0, max_value=10.0, decimals=5, seed=2175
        )
        def cmd(rough: float, precise: float) -> None:
            click.echo(f"Rough: {rough}, Precise: {precise}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Rough:" in result.output
        assert "Precise:" in result.output
