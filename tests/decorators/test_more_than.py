"""Tests for the greater_than decorator."""

from datetime import date, datetime, time
from decimal import Decimal

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.greater_than import greater_than
from click_extended.decorators.to_date import to_date
from click_extended.decorators.to_datetime import to_datetime
from click_extended.decorators.to_time import to_time


class TestMoreThanNumeric:
    """Test greater_than with numeric values."""

    def test_more_than_int_valid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with valid integer."""

        @command()
        @option("age", type=int, default=None)
        @greater_than(18)
        def cmd(age: int | None) -> None:
            assert age == 25
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "25"])
        assert result.exit_code == 0
        assert "Age: 25" in result.output

    def test_more_than_int_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with invalid integer."""

        @command()
        @option("age", type=int, default=None)
        @greater_than(18)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "15"])
        assert result.exit_code != 0
        assert "Value must be more than 18, got 15" in result.output

    def test_more_than_int_equal_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than rejects equal value when inclusive=False."""

        @command()
        @option("age", type=int, default=None)
        @greater_than(18)
        def cmd(age: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--age", "18"])
        assert result.exit_code != 0
        assert "Value must be more than 18, got 18" in result.output

    def test_more_than_int_equal_valid_inclusive(
        self, cli_runner: CliRunner
    ) -> None:
        """Test greater_than accepts equal value when inclusive=True."""

        @command()
        @option("age", type=int, default=None)
        @greater_than(18, inclusive=True)
        def cmd(age: int | None) -> None:
            assert age == 18
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--age", "18"])
        assert result.exit_code == 0
        assert "Age: 18" in result.output

    def test_more_than_float_valid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with valid float."""

        @command()
        @option("score", type=float, default=None)
        @greater_than(0.0)
        def cmd(score: float | None) -> None:
            assert score == 85.5
            click.echo(f"Score: {score}")

        result = cli_runner.invoke(cmd, ["--score", "85.5"])
        assert result.exit_code == 0
        assert "Score: 85.5" in result.output

    def test_more_than_float_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with invalid float."""

        @command()
        @option("score", type=float, default=None)
        @greater_than(0.0)
        def cmd(score: float | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--score", "-5.5"])
        assert result.exit_code != 0
        assert "Value must be more than 0.0, got -5.5" in result.output

    def test_more_than_negative_threshold(self, cli_runner: CliRunner) -> None:
        """Test greater_than with negative threshold."""

        @command()
        @option("temp", type=int, default=None)
        @greater_than(-10)
        def cmd(temp: int | None) -> None:
            assert temp == 5
            click.echo(f"Temperature: {temp}")

        result = cli_runner.invoke(cmd, ["--temp", "5"])
        assert result.exit_code == 0

    def test_more_than_zero_boundary(self, cli_runner: CliRunner) -> None:
        """Test greater_than with zero as threshold."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(0)
        def cmd(value: int | None) -> None:
            assert value == 1
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "1"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "0"])
        assert result.exit_code != 0
        assert "Value must be more than 0, got 0" in result.output


class TestMoreThanDateTime:
    """Test greater_than with datetime values."""

    def test_more_than_datetime_valid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with valid datetime."""

        @command()
        @option("event_date", default=None)
        @to_datetime()
        @greater_than(datetime(2024, 1, 1))
        def cmd(event_date: datetime | None) -> None:
            assert event_date == datetime(2024, 6, 15)
            click.echo(f"Event: {event_date}")

        result = cli_runner.invoke(cmd, ["--event-date", "2024-06-15"])
        assert result.exit_code == 0

    def test_more_than_datetime_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with invalid datetime."""

        @command()
        @option("event_date", default=None)
        @to_datetime()
        @greater_than(datetime(2024, 1, 1))
        def cmd(event_date: datetime | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--event-date", "2023-12-31"])
        assert result.exit_code != 0
        assert "Value must be more than" in result.output

    def test_more_than_date_valid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with valid date."""

        @command()
        @option("start_date", default=None)
        @to_date()
        @greater_than(date(2024, 1, 1), inclusive=True)
        def cmd(start_date: date | None) -> None:
            assert start_date == date(2024, 1, 1)
            click.echo(f"Start: {start_date}")

        result = cli_runner.invoke(cmd, ["--start-date", "2024-01-01"])
        assert result.exit_code == 0

    def test_more_than_date_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with invalid date."""

        @command()
        @option("start_date", default=None)
        @to_date()
        @greater_than(date(2024, 1, 1))
        def cmd(start_date: date | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--start-date", "2024-01-01"])
        assert result.exit_code != 0
        assert "Value must be more than" in result.output

    def test_more_than_time_valid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with valid time."""

        @command()
        @option("meeting_time", default=None)
        @to_time()
        @greater_than(time(9, 0))
        def cmd(meeting_time: time | None) -> None:
            assert meeting_time == time(14, 30)
            click.echo(f"Meeting: {meeting_time}")

        result = cli_runner.invoke(cmd, ["--meeting-time", "14:30:00"])
        assert result.exit_code == 0

    def test_more_than_time_invalid(self, cli_runner: CliRunner) -> None:
        """Test greater_than with invalid time."""

        @command()
        @option("meeting_time", default=None)
        @to_time()
        @greater_than(time(9, 0))
        def cmd(meeting_time: time | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--meeting-time", "08:00:00"])
        assert result.exit_code != 0
        assert "Value must be more than" in result.output


class TestMoreThanInclusive:
    """Test inclusive parameter behavior."""

    def test_more_than_inclusive_false_default(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that inclusive defaults to False."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(10)
        def cmd(value: int | None) -> None:
            pass

        # Should reject equal value
        result = cli_runner.invoke(cmd, ["--value", "10"])
        assert result.exit_code != 0
        assert "Value must be more than 10" in result.output

    def test_more_than_inclusive_true(self, cli_runner: CliRunner) -> None:
        """Test inclusive=True allows equal value."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(10, inclusive=True)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "10"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "9"])
        assert result.exit_code != 0
        assert "Value must be at least 10, got 9" in result.output

    def test_more_than_inclusive_true_message(
        self, cli_runner: CliRunner
    ) -> None:
        """Test inclusive=True uses correct error message."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(10, inclusive=True)
        def cmd(value: int | None) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--value", "5"])
        assert result.exit_code != 0
        assert "Value must be at least 10" in result.output


class TestMoreThanEdgeCases:
    """Test edge cases and special values."""

    def test_more_than_large_numbers(self, cli_runner: CliRunner) -> None:
        """Test greater_than with very large numbers."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(1000000)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "1000001"])
        assert result.exit_code == 0

    def test_more_than_decimal_precision(self, cli_runner: CliRunner) -> None:
        """Test greater_than with Decimal for precision."""

        @command()
        @option("value", type=float, default=None)
        @greater_than(0.1)
        def cmd(value: float | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "0.2"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "0.05"])
        assert result.exit_code != 0

    def test_more_than_negative_numbers(self, cli_runner: CliRunner) -> None:
        """Test greater_than with negative numbers."""

        @command()
        @option("value", type=int, default=None)
        @greater_than(-100)
        def cmd(value: int | None) -> None:
            click.echo(f"Value: {value}")

        result = cli_runner.invoke(cmd, ["--value", "-50"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--value", "-150"])
        assert result.exit_code != 0


class TestMoreThanPractical:
    """Test practical use cases."""

    def test_more_than_age_validation(self, cli_runner: CliRunner) -> None:
        """Test age validation (must be 18+)."""

        @command()
        @option("age", type=int, default=None)
        @greater_than(18, inclusive=True)
        def register(age: int | None) -> None:
            click.echo(f"Registered user aged {age}")

        result = cli_runner.invoke(register, ["--age", "18"])
        assert result.exit_code == 0
        assert "Registered user aged 18" in result.output

        result = cli_runner.invoke(register, ["--age", "17"])
        assert result.exit_code != 0

    def test_more_than_price_validation(self, cli_runner: CliRunner) -> None:
        """Test price validation (must be positive)."""

        @command()
        @option("price", type=float, default=None)
        @greater_than(0.0)
        def set_price(price: float | None) -> None:
            click.echo(f"Price set to ${price}")

        result = cli_runner.invoke(set_price, ["--price", "9.99"])
        assert result.exit_code == 0

        result = cli_runner.invoke(set_price, ["--price", "0"])
        assert result.exit_code != 0

    def test_more_than_deadline_validation(self, cli_runner: CliRunner) -> None:
        """Test deadline must be after today."""

        @command()
        @option("deadline", default=None)
        @to_date()
        @greater_than(date(2024, 1, 1))
        def create_task(deadline: date | None) -> None:
            click.echo(f"Task deadline: {deadline}")

        result = cli_runner.invoke(create_task, ["--deadline", "2024-12-31"])
        assert result.exit_code == 0

        result = cli_runner.invoke(create_task, ["--deadline", "2023-12-31"])
        assert result.exit_code != 0
