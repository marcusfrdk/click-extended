"""Tests for random_choice decorator."""

import click
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.decorators.random_choice import random_choice


class TestRandomChoiceBasic:
    """Test basic random_choice functionality."""

    def test_chooses_from_strings(self, cli_runner: CliRunner) -> None:
        """Test that it chooses a value from string list."""

        @command()
        @random_choice("status", ["active", "pending", "inactive"], seed=4000)
        def cmd(status: str) -> None:
            click.echo(f"Status: {status}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        output = result.output.strip()
        assert "Status:" in output
        # Extract status value
        status = output.split("Status: ")[1]
        assert status in ["active", "pending", "inactive"]

    def test_chooses_from_integers(self, cli_runner: CliRunner) -> None:
        """Test that it chooses a value from integer list."""

        @command()
        @random_choice("port", [8080, 8081, 8082, 8083], seed=4001)
        def cmd(port: int) -> None:
            click.echo(f"Port: {port}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        port_value = int(result.output.split("Port: ")[1].strip())
        assert port_value in [8080, 8081, 8082, 8083]

    def test_chooses_from_floats(self, cli_runner: CliRunner) -> None:
        """Test that it chooses a value from float list."""

        @command()
        @random_choice("rate", [0.1, 0.5, 1.0, 2.0], seed=4002)
        def cmd(rate: float) -> None:
            click.echo(f"Rate: {rate}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        rate = float(result.output.split("Rate: ")[1].strip())
        assert rate in [0.1, 0.5, 1.0, 2.0]

    def test_chooses_from_booleans(self, cli_runner: CliRunner) -> None:
        """Test that it chooses a value from boolean list."""

        @command()
        @random_choice("flag", [True, False], seed=4003)
        def cmd(flag: bool) -> None:
            click.echo(f"Flag: {flag}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        flag_str = result.output.split("Flag: ")[1].strip()
        assert flag_str in ["True", "False"]

    def test_single_item_list(self, cli_runner: CliRunner) -> None:
        """Test choosing from a single-item list."""

        @command()
        @random_choice("only", ["single"], seed=4004)
        def cmd(only: str) -> None:
            click.echo(f"Value: {only}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value: single" in result.output

    def test_different_seeds_different_results(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different seeds can produce different results."""

        choices = ["a", "b", "c", "d", "e"]
        results = []

        for i in range(10):

            @command()
            @random_choice("value", choices, seed=4100 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        # Should have some variety (not all the same)
        assert len(set(results)) > 1


class TestRandomChoiceWeights:
    """Test weighted random choice."""

    def test_equal_weights(self, cli_runner: CliRunner) -> None:
        """Test equal weights behaves like no weights."""

        choices = ["a", "b", "c"]
        results = []

        for i in range(30):

            @command()
            @random_choice("value", choices, weights=[1, 1, 1], seed=4200 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        # Should see all choices
        assert set(results) == {"a", "b", "c"}

    def test_high_weight_appears_more(self, cli_runner: CliRunner) -> None:
        """Test that higher weighted items appear more frequently."""

        choices = ["rare", "common"]
        results = []

        for i in range(100):

            @command()
            @random_choice(
                "value", choices, weights=[1, 9], seed=4300 + i
            )  # 10% vs 90%
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        rare_count = results.count("rare")
        common_count = results.count("common")

        # "common" should appear much more than "rare"
        # With 90% weight, expect roughly 90 out of 100
        assert 70 <= common_count <= 100
        assert 0 <= rare_count <= 30

    def test_zero_weight_never_chosen(self, cli_runner: CliRunner) -> None:
        """Test that zero-weighted items are never chosen."""

        choices = ["never", "always"]
        results = []

        for i in range(50):

            @command()
            @random_choice("value", choices, weights=[0, 1], seed=4400 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        # Should never see "never"
        assert "never" not in results
        assert all(r == "always" for r in results)

    def test_weights_as_integers(self, cli_runner: CliRunner) -> None:
        """Test that integer weights work correctly."""

        @command()
        @random_choice("value", ["a", "b", "c"], weights=[7, 2, 1], seed=4500)
        def cmd(value: str) -> None:
            click.echo(f"{value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert result.output.strip() in ["a", "b", "c"]

    def test_weights_normalization(self, cli_runner: CliRunner) -> None:
        """Test that weights are normalized (don't need to sum to 1)."""

        choices = ["low", "high"]

        # Test with weights summing to 10
        results_10 = []
        for i in range(50):

            @command()
            @random_choice("value", choices, weights=[1, 9], seed=4600 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results_10.append(result.output.strip())

        # Test with weights summing to 100 (same ratio)
        results_100 = []
        for i in range(50):

            @command()
            @random_choice("value", choices, weights=[10, 90], seed=4600 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results_100.append(result.output.strip())

        # Should produce same distribution (same seed, same ratio)
        assert results_10 == results_100


class TestRandomChoiceErrors:
    """Test error conditions."""

    def test_weights_length_mismatch_raises_error(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that mismatched weights and iterable lengths raise error."""

        @command()
        @random_choice("value", ["a", "b", "c"], weights=[0.5, 0.5], seed=4700)
        def cmd(value: str) -> None:
            click.echo(f"{value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "length of weights" in result.output.lower()
        assert "must match" in result.output.lower()

    def test_too_many_weights_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that too many weights raise error."""

        @command()
        @random_choice("value", ["a", "b"], weights=[1, 2, 3, 4], seed=4701)
        def cmd(value: str) -> None:
            click.echo(f"{value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "length of weights (4)" in result.output
        assert "iterable length (2)" in result.output


class TestRandomChoiceDistribution:
    """Test distribution properties."""

    def test_all_items_can_be_chosen(self, cli_runner: CliRunner) -> None:
        """Test that all items in the list can be chosen."""

        choices = ["a", "b", "c", "d", "e"]
        results = set()

        for i in range(100):

            @command()
            @random_choice("value", choices, seed=4800 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.add(result.output.strip())

        # Should see all choices over 100 iterations
        assert results == set(choices)

    def test_roughly_uniform_without_weights(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that choices are roughly uniform without weights."""

        choices = ["a", "b", "c"]
        results = []

        for i in range(150):

            @command()
            @random_choice("value", choices, seed=4900 + i)
            def cmd(value: str) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        # Each should appear roughly 50 times (33%)
        # Allow 20-70 (roughly 13-47%)
        for choice in choices:
            count = results.count(choice)
            assert 20 <= count <= 70, f"{choice} appeared {count} times"


class TestRandomChoiceIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_choices(self, cli_runner: CliRunner) -> None:
        """Test multiple random_choice decorators."""

        @command()
        @random_choice("env", ["dev", "staging", "prod"], seed=5000)
        @random_choice("region", ["us", "eu", "asia"], seed=5001)
        def cmd(env: str, region: str) -> None:
            click.echo(f"Env: {env}, Region: {region}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Env:" in result.output
        assert "Region:" in result.output

    def test_mixed_types(self, cli_runner: CliRunner) -> None:
        """Test choosing from mixed type iterable."""

        @command()
        @random_choice("value", ["text", 42, 3.14, True], seed=5002)
        def cmd(value: str | int | float | bool) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Value:" in result.output


class TestRandomChoicePractical:
    """Test practical use cases."""

    def test_status_simulation(self, cli_runner: CliRunner) -> None:
        """Test simulating API status codes."""

        statuses = [200, 400, 404, 500]
        weights = [8, 1, 0.5, 0.5]  # Mostly successful
        results = []

        for i in range(100):

            @command()
            @random_choice("status", statuses, weights=weights, seed=5100 + i)
            def cmd(status: int) -> None:
                click.echo(f"{status}")

            result = cli_runner.invoke(cmd)
            results.append(int(result.output.strip()))

        # Should be mostly 200s
        success_count = results.count(200)
        assert success_count > 60  # At least 60% success

    def test_environment_selection(self, cli_runner: CliRunner) -> None:
        """Test weighted environment selection."""

        envs = ["local", "dev", "staging", "prod"]
        # Higher weight for non-prod environments in testing
        weights = [5, 3, 2, 0]

        @command()
        @random_choice("env", envs, weights=weights, seed=5200)
        def cmd(env: str) -> None:
            click.echo(f"Deploying to: {env}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        env = result.output.split("Deploying to: ")[1].strip()
        # Should never be prod (weight=0)
        assert env != "prod"
        assert env in ["local", "dev", "staging"]

    def test_a_b_c_testing(self, cli_runner: CliRunner) -> None:
        """Test A/B/C testing scenario."""

        variants = ["control", "variant_a", "variant_b"]
        # 50% control, 25% each variant
        weights = [2, 1, 1]
        results = []

        for i in range(100):

            @command()
            @random_choice("variant", variants, weights=weights, seed=5300 + i)
            def cmd(variant: str) -> None:
                click.echo(f"{variant}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        control_count = results.count("control")
        # Control should be roughly 50%
        assert 30 <= control_count <= 70
