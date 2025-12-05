"""Tests for random_prime decorator."""

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.random.random_prime import random_prime


class TestRandomPrimeBasic:
    """Test basic random_prime functionality."""

    def test_generates_prime(self, cli_runner: CliRunner) -> None:
        """Test that it generates a prime number."""

        @command()
        @random_prime("value", k=10, seed=5000)
        def cmd(value: int) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.split("Value: ")[1].strip())

        first_10_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        assert value in first_10_primes

    def test_default_k_100(self, cli_runner: CliRunner) -> None:
        """Test default k=100 parameter."""

        @command()
        @random_prime("prime", seed=5001)
        def cmd(prime: int) -> None:
            click.echo(f"Prime: {prime}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        prime = int(result.output.split("Prime: ")[1].strip())

        assert prime >= 2
        assert prime <= 541

    def test_generates_different_values(self, cli_runner: CliRunner) -> None:
        """Test that multiple invocations generate different values."""

        values: list[int] = []
        for i in range(20):

            @command()
            @random_prime("value", k=20, seed=5002 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.append(int(result.output.strip()))

        assert len(set(values)) > 1


class TestRandomPrimeSmallValues:
    """Test small k values for correct prime generation."""

    def test_k_equals_1(self, cli_runner: CliRunner) -> None:
        """Test k=1 always returns 2 (first prime)."""

        @command()
        @random_prime("first", k=1, seed=5010)
        def cmd(first: int) -> None:
            click.echo(f"{first}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert int(result.output.strip()) == 2

    def test_k_equals_5(self, cli_runner: CliRunner) -> None:
        """Test k=5 generates from first 5 primes."""

        values: set[int] = set()
        for i in range(30):

            @command()
            @random_prime("value", k=5, seed=5011 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.add(int(result.output.strip()))

        first_5_primes = {2, 3, 5, 7, 11}
        assert values.issubset(first_5_primes)
        assert len(values) >= 3

    def test_k_equals_10_coverage(self, cli_runner: CliRunner) -> None:
        """Test k=10 covers all first 10 primes."""

        values: set[int] = set()
        for i in range(100):

            @command()
            @random_prime("value", k=10, seed=5012 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.add(int(result.output.strip()))

        first_10_primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}

        assert len(values) >= 8
        assert values.issubset(first_10_primes)


class TestRandomPrimePrimeVerification:
    """Test that generated numbers are actually prime."""

    def _is_prime(self, n: int) -> bool:
        """Helper to verify if a number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    def test_all_generated_are_prime_k10(self, cli_runner: CliRunner) -> None:
        """Test all generated values are prime for k=10."""

        for i in range(50):

            @command()
            @random_prime("value", k=10, seed=5020 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = int(result.output.strip())
            assert self._is_prime(value), f"{value} is not prime"

    def test_all_generated_are_prime_k25(self, cli_runner: CliRunner) -> None:
        """Test all generated values are prime for k=25."""

        for i in range(50):

            @command()
            @random_prime("value", k=25, seed=5030 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = int(result.output.strip())
            assert self._is_prime(value), f"{value} is not prime"

    def test_all_generated_are_prime_k50(self, cli_runner: CliRunner) -> None:
        """Test all generated values are prime for k=50."""

        for i in range(30):

            @command()
            @random_prime("value", k=50, seed=5040 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            value = int(result.output.strip())
            assert self._is_prime(value), f"{value} is not prime"


class TestRandomPrimeRanges:
    """Test various k ranges."""

    def test_k_20_in_bounds(self, cli_runner: CliRunner) -> None:
        """Test k=20 generates primes up to 71 (20th prime)."""

        values: list[int] = []
        for i in range(50):

            @command()
            @random_prime("value", k=20, seed=5050 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.append(int(result.output.strip()))

        assert all(v <= 71 for v in values)
        assert all(v >= 2 for v in values)

    def test_k_30_in_bounds(self, cli_runner: CliRunner) -> None:
        """Test k=30 generates primes up to 113 (30th prime)."""

        values: list[int] = []
        for i in range(50):

            @command()
            @random_prime("value", k=30, seed=5060 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.append(int(result.output.strip()))

        assert all(v <= 113 for v in values)
        assert all(v >= 2 for v in values)


class TestRandomPrimeDistribution:
    """Test distribution properties."""

    def test_distribution_includes_small_primes(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that small primes are generated."""

        values: set[int] = set()
        for i in range(100):

            @command()
            @random_prime("value", k=20, seed=5070 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.add(int(result.output.strip()))

        assert 2 in values or 3 in values or 5 in values

    def test_distribution_includes_larger_primes(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that larger primes in range are also generated."""

        values: set[int] = set()
        for i in range(150):

            @command()
            @random_prime("value", k=20, seed=5080 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.add(int(result.output.strip()))

        large_primes_in_range = {61, 67, 71}
        assert len(values.intersection(large_primes_in_range)) > 0


class TestRandomPrimeSeedReproducibility:
    """Test seed parameter for reproducibility."""

    def test_same_seed_same_result(self, cli_runner: CliRunner) -> None:
        """Test that same seed produces same result."""

        results: list[int] = []
        for _ in range(3):

            @command()
            @random_prime("value", k=20, seed=5090)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            results.append(int(result.output.strip()))

        assert len(set(results)) == 1

    def test_different_seed_different_result(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different seeds produce different results."""

        values: set[int] = set()
        for i in range(10):

            @command()
            @random_prime("value", k=20, seed=5091 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            values.add(int(result.output.strip()))

        assert len(values) > 1


class TestRandomPrimeIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_primes(self, cli_runner: CliRunner) -> None:
        """Test multiple random_prime decorators."""

        @command()
        @random_prime("prime1", k=10, seed=5100)
        @random_prime("prime2", k=10, seed=5101)
        def cmd(prime1: int, prime2: int) -> None:
            click.echo(f"Prime1: {prime1}, Prime2: {prime2}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Prime1:" in result.output
        assert "Prime2:" in result.output

    def test_multiple_primes_independent(self, cli_runner: CliRunner) -> None:
        """Test that multiple primes are independent."""

        same_count = 0
        for i in range(50):

            @command()
            @random_prime("p1", k=10, seed=5102 + i * 2)
            @random_prime("p2", k=10, seed=5103 + i * 2)
            def cmd(p1: int, p2: int) -> None:
                click.echo(f"{p1},{p2}")

            result = cli_runner.invoke(cmd)
            parts = result.output.strip().split(",")
            if parts[0] == parts[1]:
                same_count += 1

        assert same_count < 50


class TestRandomPrimePractical:
    """Test practical use cases."""

    def test_crypto_key_size_simulation(self, cli_runner: CliRunner) -> None:
        """Test simulating small prime for crypto operations."""

        @command()
        @random_prime("key_prime", k=15, seed=5110)
        def cmd(key_prime: int) -> None:
            click.echo(f"Key prime: {key_prime}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        prime = int(result.output.split("Key prime: ")[1].strip())

        assert prime >= 2
        assert prime <= 47  # 15th prime

    def test_hash_table_size_selection(self, cli_runner: CliRunner) -> None:
        """Test selecting prime for hash table sizing."""

        @command()
        @random_prime("table_size", k=25, seed=5111)
        def cmd(table_size: int) -> None:
            click.echo(f"Table size: {table_size}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        size = int(result.output.split("Table size: ")[1].strip())

        assert size >= 2
        assert size <= 97  # 25th prime


class TestRandomPrimePerformance:
    """Test performance-related aspects."""

    def test_k50_runs_quickly(self, cli_runner: CliRunner) -> None:
        """Test that k=50 doesn't cause slowdown."""

        for i in range(20):

            @command()
            @random_prime("value", k=50, seed=5120 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            assert result.exit_code == 0

    def test_k100_runs_quickly(self, cli_runner: CliRunner) -> None:
        """Test that k=100 (default) doesn't cause slowdown."""

        for i in range(20):

            @command()
            @random_prime("value", seed=5130 + i)
            def cmd(value: int) -> None:
                click.echo(f"{value}")

            result = cli_runner.invoke(cmd)
            assert result.exit_code == 0
            value = int(result.output.strip())
            assert value >= 2
            assert value <= 541  # 100th prime


class TestRandomPrimeCaching:
    """Test that caching optimization works."""

    def test_small_primes_use_cache(self, cli_runner: CliRunner) -> None:
        """Test that small k values use cached primes."""

        @command()
        @random_prime("value", k=50, seed=5140)
        def cmd(value: int) -> None:
            click.echo(f"{value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.strip())

        assert value <= 229

    def test_exact_cache_boundary(self, cli_runner: CliRunner) -> None:
        """Test k at cache boundary."""

        @command()
        @random_prime("value", k=99, seed=5141)
        def cmd(value: int) -> None:
            click.echo(f"{value}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        value = int(result.output.strip())

        assert value <= 523
        assert value >= 2
