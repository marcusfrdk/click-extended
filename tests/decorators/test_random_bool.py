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
        @random_bool("flag", seed=3000)
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        flag_str = result.output.split("Flag: ")[1].strip()
        assert flag_str in ["True", "False"]

    def test_default_weight_50_percent(self, cli_runner: CliRunner) -> None:
        """Test default weight gives approximately 50% distribution."""

        # Sample many times
        results = []
        for i in range(100):

            @command()
            @random_bool("coin", seed=3001 + i)
            def cmd(coin: bool) -> None:
                click.echo(f"{coin}")

            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 50%, allowing for randomness (30-70%)
        assert 30 <= true_count <= 70

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that both True and False are generated."""

        # Run enough times to see both values
        values = set()
        for i in range(20):

            @command()
            @random_bool("value", seed=3002 + i)
            def cmd(value: bool) -> None:
                click.echo(f"{value}")

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
        @random_bool("never", weight=0.0, seed=3003)
        def cmd(never: bool) -> None:
            click.echo(f"{never}")

        # Run multiple times
        for _ in range(20):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "False"

    def test_weight_one_always_true(self, cli_runner: CliRunner) -> None:
        """Test weight=1.0 always returns True."""

        @command()
        @random_bool("always", weight=1.0, seed=3004)
        def cmd(always: bool) -> None:
            click.echo(f"{always}")

        # Run multiple times
        for _ in range(20):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "True"

    def test_weight_high_mostly_true(self, cli_runner: CliRunner) -> None:
        """Test weight=0.8 gives mostly True values."""

        results = []
        for i in range(100):

            @command()
            @random_bool("likely", weight=0.8, seed=3005 + i)
            def cmd(likely: bool) -> None:
                click.echo(f"{likely}")

            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 80%, allowing for randomness (65-95%)
        assert 65 <= true_count <= 95

    def test_weight_low_mostly_false(self, cli_runner: CliRunner) -> None:
        """Test weight=0.2 gives mostly False values."""

        results = []
        for i in range(100):

            @command()
            @random_bool("unlikely", weight=0.2, seed=3006 + i)
            def cmd(unlikely: bool) -> None:
                click.echo(f"{unlikely}")

            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 20%, allowing for randomness (5-35%)
        assert 5 <= true_count <= 35

    def test_weight_quarter(self, cli_runner: CliRunner) -> None:
        """Test weight=0.25 gives approximately 25% True."""

        results = []
        for i in range(200):

            @command()
            @random_bool("rare", weight=0.25, seed=3007 + i)
            def cmd(rare: bool) -> None:
                click.echo(f"{rare}")

            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 25%, allowing for randomness (15-35%)
        assert 15 <= true_count * 100 / 200 <= 35

    def test_weight_three_quarters(self, cli_runner: CliRunner) -> None:
        """Test weight=0.75 gives approximately 75% True."""

        results = []
        for i in range(200):

            @command()
            @random_bool("common", weight=0.75, seed=3008 + i)
            def cmd(common: bool) -> None:
                click.echo(f"{common}")

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
        @random_bool("negative", weight=-0.5, seed=3009)
        def cmd(negative: bool) -> None:
            click.echo(f"{negative}")

        # Should behave like weight=0.0 (always False)
        for _ in range(10):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "False"

    def test_weight_clamped_above_one(self, cli_runner: CliRunner) -> None:
        """Test that weights > 1.0 are clamped to 1.0."""

        @command()
        @random_bool("over", weight=2.0, seed=3010)
        def cmd(over: bool) -> None:
            click.echo(f"{over}")

        # Should behave like weight=1.0 (always True)
        for _ in range(10):
            result = cli_runner.invoke(cmd)
            assert result.output.strip() == "True"

    def test_very_small_weight(self, cli_runner: CliRunner) -> None:
        """Test very small but non-zero weight."""

        results = []
        for i in range(500):

            @command()
            @random_bool("tiny", weight=0.01, seed=3011 + i)
            def cmd(tiny: bool) -> None:
                click.echo(f"{tiny}")

            result = cli_runner.invoke(cmd)
            value = result.output.strip() == "True"
            results.append(value)

        true_count = sum(results)
        # Should be roughly 1% (0-10 out of 500, so 0-2%)
        assert 0 <= true_count <= 10

    def test_very_large_weight(self, cli_runner: CliRunner) -> None:
        """Test weight very close to 1.0."""

        results = []
        for i in range(500):

            @command()
            @random_bool("almost", weight=0.99, seed=3012 + i)
            def cmd(almost: bool) -> None:
                click.echo(f"{almost}")

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
        @random_bool("likely", weight=0.9, seed=3013)
        @random_bool("unlikely", weight=0.1, seed=3014)
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

        # Collect samples
        results = []
        for i in range(100):

            @command()
            @random_bool("coin1", weight=0.5, seed=3015 + i * 2)
            @random_bool("coin2", weight=0.5, seed=3016 + i * 2)
            def cmd(coin1: bool, coin2: bool) -> None:
                click.echo(f"{coin1},{coin2}")

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

        results = []
        for i in range(100):

            @command()
            @random_bool(
                "new_feature", weight=0.1, seed=3017 + i
            )  # 10% rollout
            def cmd(new_feature: bool) -> None:
                if new_feature:
                    click.echo("Using new feature")
                else:
                    click.echo("Using old feature")

            result = cli_runner.invoke(cmd)
            new = "new" in result.output
            results.append(new)

        new_count = sum(results)
        # Approximately 10% should get new feature
        assert 0 <= new_count <= 20

    def test_ab_testing_simulation(self, cli_runner: CliRunner) -> None:
        """Test simulating A/B testing with equal split."""

        results = {"A": 0, "B": 0}
        for i in range(100):

            @command()
            @random_bool("variant_b", weight=0.5, seed=3018 + i)
            def cmd(variant_b: bool) -> None:
                variant = "B" if variant_b else "A"
                click.echo(f"Variant: {variant}")

            result = cli_runner.invoke(cmd)
            variant = result.output.split("Variant: ")[1].strip()
            results[variant] += 1

        # Should be roughly 50/50
        assert 30 <= results["A"] <= 70
        assert 30 <= results["B"] <= 70
