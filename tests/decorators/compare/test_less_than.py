"""Tests for the less_than decorator."""

from datetime import date, datetime, time
from decimal import Decimal

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.compare.less_than import less_than
from click_extended.decorators.transform.to_date import to_date
from click_extended.decorators.transform.to_datetime import to_datetime
from click_extended.decorators.transform.to_time import to_time


class TestLessThanNumeric:
    """Test less_than with numeric values."""

    def test_less_than_int_valid(self, cli_runner: CliRunner) -> None:
        """Test less_than with valid integer."""

        @command()
        @option("age", type=int, default=None)
        @less_than(100)
        def cmd(age: int | None) -> None:
            assert age == 25
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "25"])
        assert result.exit_code == 0
        assert "Age: 25" in result.output

    def test_less_than_int_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than with invalid integer."""

        @command()
        @option("age", type=int, default=None)
        @less_than(100)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "150"])
        assert result.exit_code != 0
        assert "Value must be less than 100, got 150" in result.output

    def test_less_than_int_equal_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than rejects equal value when inclusive=False."""

        @command()
        @option("age", type=int, default=None)
        @less_than(100)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "100"])
        assert result.exit_code != 0
        assert "Value must be less than 100, got 100" in result.output

    def test_less_than_int_equal_valid_inclusive(
        self, cli_runner: CliRunner
    ) -> None:
        """Test less_than accepts equal value when inclusive=True."""

        @command()
        @option("age", type=int, default=None)
        @less_than(100, inclusive=True)
        def cmd(age: int | None) -> None:
            assert age == 100
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "100"])
        assert result.exit_code == 0
        assert "Age: 100" in result.output

    def test_less_than_float_valid(self, cli_runner: CliRunner) -> None:
        """Test less_than with valid float."""

        @command()
        @option("score", type=float, default=None)
        @less_than(100.0)
        def cmd(score: float | None) -> None:
            assert score == 85.5
            click.echo(f"Score: {score}")

        result = cli_runner.invoke(cmd, ["--score", "85.5"])
        assert result.exit_code == 0
        assert "Score: 85.5" in result.output

    def test_less_than_float_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than with invalid float."""

        @command()
        @option("score", type=float, default=None)
        @less_than(100.0)
        def cmd(score: float | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--score", "105.5"])
        assert result.exit_code != 0
        assert "Value must be less than 100.0, got 105.5" in result.output

    def test_less_than_negative_threshold(self, cli_runner: CliRunner) -> None:
        """Test less_than with negative threshold."""

        @command()
        @option("temp", type=int, default=None)
        @less_than(-10)
        def cmd(temp: int | None) -> None:
            assert temp == -20
            click.echo(f"Temperature: {temp}")

        result = cli_runner.invoke(cmd, ["--temp", "-20"])
        assert result.exit_code == 0

    def test_less_than_zero_boundary(self, cli_runner: CliRunner) -> None:
        """Test less_than with zero as threshold."""

        @command()
        @option("value", type=int, default=None)
        @less_than(0)
        def cmd(value: int | None) -> None:
            assert value == -1
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "-1"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "0"])
        assert result.exit_code != 0
        assert "Value must be less than 0, got 0" in result.output


class TestLessThanDateTime:
    """Test less_than with datetime values."""

    def test_less_than_datetime_valid(self, cli_runner: CliRunner) -> None:
        """Test less_than with valid datetime."""

        @command()
        @option("event_date", default=None)
        @to_datetime()
        @less_than(datetime(2025, 12, 31))
        def cmd(event_date: datetime | None) -> None:
            assert event_date == datetime(2024, 6, 15)
            click.echo(f"Event: {event_date}")

        result = cli_runner.invoke(cmd, ["--event-date", "2024-06-15"])
        assert result.exit_code == 0

    def test_less_than_datetime_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than with invalid datetime."""

        @command()
        @option("event_date", default=None)
        @to_datetime()
        @less_than(datetime(2024, 1, 1))
        def cmd(event_date: datetime | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--event-date", "2024-06-15"])
        assert result.exit_code != 0
        assert "Value must be less than" in result.output

    def test_less_than_date_valid(self, cli_runner: CliRunner) -> None:
        """Test less_than with valid date."""

        @command()
        @option("end_date", default=None)
        @to_date()
        @less_than(date(2025, 12, 31), inclusive=True)
        def cmd(end_date: date | None) -> None:
            assert end_date == date(2025, 12, 31)
            click.echo(f"End: {end_date}")

        result = cli_runner.invoke(cmd, ["--end-date", "2025-12-31"])
        assert result.exit_code == 0

    def test_less_than_date_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than with invalid date."""

        @command()
        @option("end_date", default=None)
        @to_date()
        @less_than(date(2025, 12, 31))
        def cmd(end_date: date | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--end-date", "2025-12-31"])
        assert result.exit_code != 0
        assert "Value must be less than" in result.output

    def test_less_than_time_valid(self, cli_runner: CliRunner) -> None:
        """Test less_than with valid time."""

        @command()
        @option("meeting_time", default=None)
        @to_time()
        @less_than(time(17, 0))
        def cmd(meeting_time: time | None) -> None:
            assert meeting_time == time(14, 30)
            click.echo(f"Meeting: {meeting_time}")

        result = cli_runner.invoke(cmd, ["--meeting-time", "14:30:00"])
        assert result.exit_code == 0

    def test_less_than_time_invalid(self, cli_runner: CliRunner) -> None:
        """Test less_than with invalid time."""

        @command()
        @option("meeting_time", default=None)
        @to_time()
        @less_than(time(17, 0))
        def cmd(meeting_time: time | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--meeting-time", "18:00:00"])
        assert result.exit_code != 0
        assert "Value must be less than" in result.output


class TestLessThanInclusive:
    """Test inclusive parameter behavior."""

    def test_less_than_inclusive_false_default(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that inclusive defaults to False."""

        @command()
        @option("value", type=int, default=None)
        @less_than(10)
        def cmd(value: int | None) -> None:
            pass

        # Should reject equal value
        result = cli_runner.invoke(cmd, ["--value", "10"])
        assert result.exit_code != 0
        assert "Value must be less than 10" in result.output

    def test_less_than_inclusive_true(self, cli_runner: CliRunner) -> None:
        """Test inclusive=True allows equal value."""

        @command()
        @option("value", type=int, default=None)
        @less_than(10, inclusive=True)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "10"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "11"])
        assert result.exit_code != 0
        assert "Value must be at most 10, got 11" in result.output

    def test_less_than_inclusive_true_message(
        self, cli_runner: CliRunner
    ) -> None:
        """Test inclusive=True uses correct error message."""

        @command()
        @option("value", type=int, default=None)
        @less_than(10, inclusive=True)
        def cmd(value: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--value", "15"])
        assert result.exit_code != 0
        assert "Value must be at most 10" in result.output


class TestLessThanEdgeCases:
    """Test edge cases and special values."""

    def test_less_than_large_numbers(self, cli_runner: CliRunner) -> None:
        """Test less_than with very large numbers."""

        @command()
        @option("value", type=int, default=None)
        @less_than(1000000)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "999999"])
        assert result.exit_code == 0

    def test_less_than_decimal_precision(self, cli_runner: CliRunner) -> None:
        """Test less_than with Decimal for precision."""

        @command()
        @option("value", type=float, default=None)
        @less_than(1.0)
        def cmd(value: float | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "0.5"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "1.5"])
        assert result.exit_code != 0

    def test_less_than_negative_numbers(self, cli_runner: CliRunner) -> None:
        """Test less_than with negative numbers."""

        @command()
        @option("value", type=int, default=None)
        @less_than(-100)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "-150"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "-50"])
        assert result.exit_code != 0


class TestLessThanPractical:
    """Test practical use cases."""

    def test_less_than_percentage_validation(
        self, cli_runner: CliRunner
    ) -> None:
        """Test percentage validation (must be <= 100)."""

        @command()
        @option("percentage", type=float, default=None)
        @less_than(100.0, inclusive=True)
        def set_percentage(percentage: float | None) -> None:
            click.echo(f"Percentage: {percentage}%")

        result = cli_runner.invoke(set_percentage, ["--percentage", "100.0"])
        assert result.exit_code == 0
        assert "Percentage: 100.0%" in result.output

        result = cli_runner.invoke(set_percentage, ["--percentage", "101.0"])
        assert result.exit_code != 0

    def test_less_than_discount_validation(self, cli_runner: CliRunner) -> None:
        """Test discount validation (must be < 100)."""

        @command()
        @option("discount", type=float, default=None)
        @less_than(100.0)
        def apply_discount(discount: float | None) -> None:
            click.echo(f"Discount: {discount}%")

        result = cli_runner.invoke(apply_discount, ["--discount", "25.5"])
        assert result.exit_code == 0

        result = cli_runner.invoke(apply_discount, ["--discount", "100.0"])
        assert result.exit_code != 0

    def test_less_than_deadline_validation(self, cli_runner: CliRunner) -> None:
        """Test deadline must be before end date."""

        @command()
        @option("deadline", default=None)
        @to_date()
        @less_than(date(2025, 12, 31), inclusive=True)
        def create_task(deadline: date | None) -> None:
            click.echo(f"Task deadline: {deadline}")

        result = cli_runner.invoke(create_task, ["--deadline", "2025-06-15"])
        assert result.exit_code == 0

        result = cli_runner.invoke(create_task, ["--deadline", "2026-01-01"])
        assert result.exit_code != 0
