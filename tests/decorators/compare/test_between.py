"""Tests for the between decorator."""

from datetime import date, datetime, time

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.compare.between import between
from click_extended.decorators.transform.to_date import to_date
from click_extended.decorators.transform.to_datetime import to_datetime
from click_extended.decorators.transform.to_time import to_time


class TestBetweenNumeric:
    """Test between with numeric values."""

    def test_between_int_valid(self, cli_runner: CliRunner) -> None:
        """Test between with valid integer."""

        @command()
        @option("age", type=int, default=None)
        @between(18, 100)
        def cmd(age: int | None) -> None:
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "25"])
        assert result.exit_code == 0
        assert "Age: 25" in result.output

    def test_between_int_invalid_lower(self, cli_runner: CliRunner) -> None:
        """Test between with integer below lower bound."""

        @command()
        @option("age", type=int, default=None)
        @between(18, 100)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "10"])
        assert result.exit_code != 0
        assert "Value '10' is not between '18' and '100'." in result.output

    def test_between_int_invalid_upper(self, cli_runner: CliRunner) -> None:
        """Test between with integer above upper bound."""

        @command()
        @option("age", type=int, default=None)
        @between(18, 100)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "150"])
        assert result.exit_code != 0
        assert "Value '150' is not between '18' and '100'." in result.output

    def test_between_int_inclusive_bounds(self, cli_runner: CliRunner) -> None:
        """Test between with inclusive bounds."""

        @command()
        @option("age", type=int, default=None)
        @between(18, 100, inclusive=True)
        def cmd(age: int | None) -> None:
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "18"])
        assert result.exit_code == 0
        assert "Age: 18" in result.output

        result = cli_runner.invoke(cmd, ["--age", "100"])
        assert result.exit_code == 0
        assert "Age: 100" in result.output

    def test_between_int_exclusive_bounds(self, cli_runner: CliRunner) -> None:
        """Test between with exclusive bounds."""

        @command()
        @option("age", type=int, default=None)
        @between(18, 100, inclusive=False)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "18"])
        assert result.exit_code != 0
        assert "Value '18' is not between '18' and '100'." in result.output

        result = cli_runner.invoke(cmd, ["--age", "100"])
        assert result.exit_code != 0
        assert "Value '100' is not between '18' and '100'." in result.output

    def test_between_float_valid(self, cli_runner: CliRunner) -> None:
        """Test between with valid float."""

        @command()
        @option("score", type=float, default=None)
        @between(0.0, 1.0)
        def cmd(score: float | None) -> None:
            click.echo(f"Score: {score}")

        result = cli_runner.invoke(cmd, ["--score", "0.5"])
        assert result.exit_code == 0
        assert "Score: 0.5" in result.output


class TestBetweenDate:
    """Test between with date values."""

    def test_between_date_valid(self, cli_runner: CliRunner) -> None:
        """Test between with valid date."""

        @command()
        @option("dt", default=None)
        @to_date()
        @between(date(2023, 1, 1), date(2023, 12, 31))
        def cmd(dt: date | None) -> None:
            click.echo(f"Date: {dt}")

        result = cli_runner.invoke(cmd, ["--dt", "2023-06-15"])
        assert result.exit_code == 0
        assert "Date: 2023-06-15" in result.output

    def test_between_date_invalid(self, cli_runner: CliRunner) -> None:
        """Test between with invalid date."""

        @command()
        @option("dt", default=None)
        @to_date()
        @between(date(2023, 1, 1), date(2023, 12, 31))
        def cmd(dt: date | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--dt", "2022-12-31"])
        assert result.exit_code != 0
        assert (
            "Value '2022-12-31' is not between '2023-01-01' and '2023-12-31'."
            in result.output
        )


class TestBetweenTime:
    """Test between with time values."""

    def test_between_time_valid(self, cli_runner: CliRunner) -> None:
        """Test between with valid time."""

        @command()
        @option("tm", default=None)
        @to_time()
        @between(time(9, 0), time(17, 0))
        def cmd(tm: time | None) -> None:
            click.echo(f"Time: {tm}")

        result = cli_runner.invoke(cmd, ["--tm", "12:00"])
        assert result.exit_code == 0
        assert "Time: 12:00:00" in result.output

    def test_between_time_invalid(self, cli_runner: CliRunner) -> None:
        """Test between with invalid time."""

        @command()
        @option("tm", default=None)
        @to_time()
        @between(time(9, 0), time(17, 0))
        def cmd(tm: time | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--tm", "08:00"])
        assert result.exit_code != 0
        assert (
            "Value '08:00:00' is not between '09:00:00' and '17:00:00'."
            in result.output
        )


class TestBetweenDatetime:
    """Test between with datetime values."""

    def test_between_datetime_valid(self, cli_runner: CliRunner) -> None:
        """Test between with valid datetime."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @between(datetime(2023, 1, 1, 9, 0), datetime(2023, 1, 1, 17, 0))
        def cmd(dt: datetime | None) -> None:
            click.echo(f"Datetime: {dt}")

        result = cli_runner.invoke(cmd, ["--dt", "2023-01-01 12:00:00"])
        assert result.exit_code == 0
        assert "Datetime: 2023-01-01 12:00:00" in result.output

    def test_between_datetime_invalid(self, cli_runner: CliRunner) -> None:
        """Test between with invalid datetime."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @between(datetime(2023, 1, 1, 9, 0), datetime(2023, 1, 1, 17, 0))
        def cmd(dt: datetime | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--dt", "2023-01-01 18:00:00"])
        assert result.exit_code != 0
        assert (
            "Value '2023-01-01 18:00:00' is not between '2023-01-01 09:00:00' and '2023-01-01 17:00:00'."
            in result.output
        )
