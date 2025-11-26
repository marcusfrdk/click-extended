"""Tests for random_bool decorator."""

import click
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.decorators.random_bool import random_bool


class TestRandomBoolBasic:
    """Test basic random_bool functionality."""

    def test_generates_boolean(self, cli_runner: CliRunner) -> None:
        """Test that it generates a boolean value."""

        @command()
        @random_bool("flag")
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        flag_str = result.output.split("Flag: ")[1].strip()
        assert flag_str in ["True", "False"]

    def test_default_weight_50_percent(self, cli_runner: CliRunner) -> None:
        """Test default weight gives approximately 50% distribution."""

        @command()
        @random_bool("coin")
        def cmd(coin: bool) -> None:
            click.echo(f"{coin}")

        # Sample many times
        results = []
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 50%, allowing for randomness (30-70%)
        assert 30 <= true_count <= 70

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that both True and False are generated."""

        @command()
        @random_bool("value")
        def cmd(value: bool) -> None:
            click.echo(f"{value}")

        # Run enough times to see both values
        values = set()
        for _ in range(20):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            values.add(value)

        # Should have seen both True and False
        assert len(values) == 2


class TestRandomBoolWeights:
    """Test weight parameter."""

    def test_weight_zero_always_false(self, cli_runner: CliRunner) -> None:
        """Test weight=0.0 always returns False."""

        @command()
        @random_bool("never", weight=0.0)
        def cmd(never: bool) -> None:
            click.echo(f"{never}")

        # Run multiple times
        for _ in range(20):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "False"

    def test_weight_one_always_true(self, cli_runner: CliRunner) -> None:
        """Test weight=1.0 always returns True."""

        @command()
        @random_bool("always", weight=1.0)
        def cmd(always: bool) -> None:
            click.echo(f"{always}")

        # Run multiple times
        for _ in range(20):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "True"

    def test_weight_high_mostly_true(self, cli_runner: CliRunner) -> None:
        """Test weight=0.8 gives mostly True values."""

        @command()
        @random_bool("likely", weight=0.8)
        def cmd(likely: bool) -> None:
            click.echo(f"{likely}")

        results = []
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 80%, allowing for randomness (65-95%)
        assert 65 <= true_count <= 95

    def test_weight_low_mostly_false(self, cli_runner: CliRunner) -> None:
        """Test weight=0.2 gives mostly False values."""

        @command()
        @random_bool("unlikely", weight=0.2)
        def cmd(unlikely: bool) -> None:
            click.echo(f"{unlikely}")

        results = []
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 20%, allowing for randomness (5-35%)
        assert 5 <= true_count <= 35

    def test_weight_quarter(self, cli_runner: CliRunner) -> None:
        """Test weight=0.25 gives approximately 25% True."""

        @command()
        @random_bool("rare", weight=0.25)
        def cmd(rare: bool) -> None:
            click.echo(f"{rare}")

        results = []
        for _ in range(200):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 25%, allowing for randomness (15-35%)
        assert 15 <= true_count * 100 / 200 <= 35

    def test_weight_three_quarters(self, cli_runner: CliRunner) -> None:
        """Test weight=0.75 gives approximately 75% True."""

        @command()
        @random_bool("common", weight=0.75)
        def cmd(common: bool) -> None:
            click.echo(f"{common}")

        results = []
        for _ in range(200):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 75%, allowing for randomness (65-85%)
        assert 65 <= true_count * 100 / 200 <= 85


class TestRandomBoolEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_weight_clamped_below_zero(self, cli_runner: CliRunner) -> None:
        """Test that negative weights are clamped to 0."""

        @command()
        @random_bool("negative", weight=-0.5)
        def cmd(negative: bool) -> None:
            click.echo(f"{negative}")

        # Should behave like weight=0.0 (always False)
        for _ in range(10):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "False"

    def test_weight_clamped_above_one(self, cli_runner: CliRunner) -> None:
        """Test that weights > 1.0 are clamped to 1.0."""

        @command()
        @random_bool("over", weight=2.0)
        def cmd(over: bool) -> None:
            click.echo(f"{over}")

        # Should behave like weight=1.0 (always True)
        for _ in range(10):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "True"

    def test_very_small_weight(self, cli_runner: CliRunner) -> None:
        """Test very small but non-zero weight."""

        @command()
        @random_bool("tiny", weight=0.01)
        def cmd(tiny: bool) -> None:
            click.echo(f"{tiny}")

        results = []
        for _ in range(500):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 1% (0-10 out of 500, so 0-2%)
        assert 0 <= true_count <= 10

    def test_very_large_weight(self, cli_runner: CliRunner) -> None:
        """Test weight very close to 1.0."""

        @command()
        @random_bool("almost", weight=0.99)
        def cmd(almost: bool) -> None:
            click.echo(f"{almost}")

        results = []
        for _ in range(500):
            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 99% (490-500, so 98-100%)
        assert 490 <= true_count <= 500


class TestRandomBoolIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_bools(self, cli_runner: CliRunner) -> None:
        """Test multiple random_bool decorators with different weights."""

        @command()
        @random_bool("likely", weight=0.9)
        @random_bool("unlikely", weight=0.1)
        def cmd(likely: bool, unlikely: bool) -> None:
            click.echo(f"Likely: {likely}, Unlikely: {unlikely}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Likely:" in result.output
        assert "Unlikely:" in result.output

    def test_multiple_invocations_independent(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that multiple bools are independent."""

        @command()
        @random_bool("coin1", weight=0.5)
        @random_bool("coin2", weight=0.5)
        def cmd(coin1: bool, coin2: bool) -> None:
            click.echo(f"{coin1},{coin2}")

        # Collect samples
        results = []
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            parts = result.output.strip().split(",")
            pair = (parts[0] == "True", parts[1] == "True")
            results.append(pair)

        # Should see all four combinations
        combinations = set(results)
        # With 100 samples at 50%, we should see at least 3 combinations
        assert len(combinations) >= 3


class TestRandomBoolPractical:
    """Test practical use cases."""

    def test_feature_flag_simulation(self, cli_runner: CliRunner) -> None:
        """Test simulating a feature flag rollout."""

        @command()
        @random_bool("new_feature", weight=0.1)  # 10% rollout
        def cmd(new_feature: bool) -> None:
            if new_feature:
                click.echo("Using new feature")
            else:
                click.echo("Using old feature")

        results = []
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            new = "new" in result.output
            results.append(new)

        new_count = sum(results)
        # Approximately 10% should get new feature
        assert 0 <= new_count <= 20

    def test_ab_testing_simulation(self, cli_runner: CliRunner) -> None:
        """Test simulating A/B testing with equal split."""

        @command()
        @random_bool("variant_b", weight=0.5)
        def cmd(variant_b: bool) -> None:
            variant = "B" if variant_b else "A"
            click.echo(f"Variant: {variant}")

        results = {"A": 0, "B": 0}
        for _ in range(100):
            result = cli_runner.invoke(cmd)
            variant = result.output.split("Variant: ")[1].strip()
            results[variant] += 1

        # Should be roughly 50/50
        assert 30 <= results["A"] <= 70
        assert 30 <= results["B"] <= 70
