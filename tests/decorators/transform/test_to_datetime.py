"""Tests for to_datetime decorator."""

from datetime import datetime
from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.transform.to_datetime import to_datetime


class TestToDatetimeBasic:
    """Test basic to_datetime functionality."""

    def test_to_datetime_single_format_strptime(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with single Python strptime format."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Year: {date.year}")
            click.echo(f"Month: {date.month}")
            click.echo(f"Day: {date.day}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0
        assert "Year: 2024" in result.output
        assert "Month: 12" in result.output
        assert "Day: 4" in result.output

    def test_to_datetime_single_format_simplified(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with single simplified format."""

        @command()
        @option("date", default=None)
        @to_datetime("YYYY-MM-DD")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Year: {date.year}")
            click.echo(f"Month: {date.month}")
            click.echo(f"Day: {date.day}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0
        assert "Year: 2024" in result.output
        assert "Month: 12" in result.output
        assert "Day: 4" in result.output

    def test_to_datetime_with_time(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with date and time."""

        @command()
        @option("datetime_val", default=None)
        @to_datetime("%Y-%m-%d %H:%M:%S")
        def cmd(datetime_val: Any) -> None:
            assert isinstance(datetime_val, datetime)
            click.echo(f"Date: {datetime_val.date()}")
            click.echo(f"Hour: {datetime_val.hour}")
            click.echo(f"Minute: {datetime_val.minute}")
            click.echo(f"Second: {datetime_val.second}")

        result = cli_runner.invoke(
            cmd, ["--datetime-val", "2024-12-04 14:30:45"]
        )
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 45" in result.output

    def test_to_datetime_with_time_simplified(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with simplified format including time."""

        @command()
        @option("datetime_val", default=None)
        @to_datetime("YYYY-MM-DD HH:mm:SS")
        def cmd(datetime_val: Any) -> None:
            assert isinstance(datetime_val, datetime)
            click.echo(f"Hour: {datetime_val.hour}")
            click.echo(f"Minute: {datetime_val.minute}")

        result = cli_runner.invoke(
            cmd, ["--datetime-val", "2024-12-04 14:30:45"]
        )
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output


class TestToDatetimeMultipleFormats:
    """Test to_datetime with multiple format fallbacks."""

    def test_to_datetime_multiple_formats_first_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime tries first format and succeeds."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_multiple_formats_second_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime falls back to second format."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "04/12/2024"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_multiple_formats_third_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime falls back to third format."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "12-04-2024"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_mixed_format_styles(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with mix of strptime and simplified formats."""

        @command()
        @option("date", default=None)
        @to_datetime("YYYY-MM-DD", "%d/%m/%Y", "MM-DD-YYYY")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        # Test first format (simplified)
        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0

        # Test second format (strptime)
        result = cli_runner.invoke(cmd, ["--date", "04/12/2024"])
        assert result.exit_code == 0

        # Test third format (simplified)
        result = cli_runner.invoke(cmd, ["--date", "12-04-2024"])
        assert result.exit_code == 0


class TestToDatetimeTimezone:
    """Test to_datetime timezone support."""

    def test_to_datetime_with_utc_timezone(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with UTC timezone."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d %H:%M:%S", tz="UTC")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            assert date.tzinfo is not None
            click.echo(f"Timezone: {date.tzinfo}")
            click.echo(f"ISO: {date.isoformat()}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04 14:30:00"])
        assert result.exit_code == 0
        assert "UTC" in result.output

    def test_to_datetime_with_custom_timezone(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with custom timezone."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d", tz="America/New_York")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            assert date.tzinfo is not None
            click.echo(f"Timezone: {date.tzinfo}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0
        assert "America/New_York" in result.output

    def test_to_datetime_without_timezone(self, cli_runner: CliRunner) -> None:
        """Test to_datetime without timezone produces naive datetime."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Has timezone: {date.tzinfo is not None}")

        result = cli_runner.invoke(cmd, ["--date", "2024-12-04"])
        assert result.exit_code == 0
        assert "Has timezone: False" in result.output


class TestToDatetimeTuples:
    """Test to_datetime with tuple inputs."""

    def test_to_datetime_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with flat tuple of date strings."""

        @command()
        @argument("dates", nargs=-1)
        @to_datetime("%Y-%m-%d")
        def cmd(dates: Any) -> None:
            assert isinstance(dates, tuple)
            click.echo(f"Count: {len(dates)}")
            for i, date in enumerate(dates, 1):
                assert isinstance(date, datetime)
                click.echo(f"Date {i}: {date.date()}")

        result = cli_runner.invoke(
            cmd, ["2024-01-01", "2024-06-15", "2024-12-31"]
        )
        assert result.exit_code == 0
        assert "Count: 3" in result.output
        assert "Date 1: 2024-01-01" in result.output
        assert "Date 2: 2024-06-15" in result.output
        assert "Date 3: 2024-12-31" in result.output

    def test_to_datetime_flat_tuple_multiple_formats(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with tuple where different items match different formats."""

        @command()
        @argument("dates", nargs=-1)
        @to_datetime("%Y-%m-%d", "%d/%m/%Y")
        def cmd(dates: Any) -> None:
            assert isinstance(dates, tuple)
            click.echo(f"Count: {len(dates)}")
            for date in dates:
                assert isinstance(date, datetime)
                click.echo(f"Year: {date.year}")

        result = cli_runner.invoke(cmd, ["2024-12-04", "04/06/2024"])
        assert result.exit_code == 0
        assert "Count: 2" in result.output
        assert "Year: 2024" in result.output

    def test_to_datetime_empty_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with empty tuple."""

        @command()
        @argument("dates", nargs=-1, required=False)
        @to_datetime("%Y-%m-%d")
        def cmd(dates: Any) -> None:
            click.echo(f"Count: {len(dates)}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Count: 0" in result.output


class TestToDatetimeErrors:
    """Test to_datetime error handling."""

    def test_to_datetime_invalid_format(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with string that doesn't match format."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d")
        def cmd(date: Any) -> None:
            click.echo(f"Date: {date}")

        result = cli_runner.invoke(cmd, ["--date", "not-a-date"])
        assert result.exit_code != 0
        assert "Invalid datetime" in result.output

    def test_to_datetime_no_matching_format(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime when no format matches."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d", "%d/%m/%Y")
        def cmd(date: Any) -> None:
            click.echo(f"Date: {date}")

        result = cli_runner.invoke(cmd, ["--date", "12-04-2024"])
        assert result.exit_code != 0
        assert "Invalid datetime" in result.output

    def test_to_datetime_invalid_date_values(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_datetime with invalid date values."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d")
        def cmd(date: Any) -> None:
            click.echo(f"Date: {date}")

        # Invalid month
        result = cli_runner.invoke(cmd, ["--date", "2024-13-01"])
        assert result.exit_code != 0

        # Invalid day
        result = cli_runner.invoke(cmd, ["--date", "2024-02-30"])
        assert result.exit_code != 0

    def test_to_datetime_partial_match(self, cli_runner: CliRunner) -> None:
        """Test to_datetime rejects partial format matches."""

        @command()
        @option("date", default=None)
        @to_datetime("%Y-%m-%d")
        def cmd(date: Any) -> None:
            click.echo(f"Date: {date}")

        # Missing day
        result = cli_runner.invoke(cmd, ["--date", "2024-12"])
        assert result.exit_code != 0


class TestToDatetimeFormatVariations:
    """Test various datetime format patterns."""

    def test_to_datetime_two_digit_year(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with two-digit year."""

        @command()
        @option("date", default=None)
        @to_datetime("YY-MM-DD")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Year: {date.year}")

        result = cli_runner.invoke(cmd, ["--date", "24-12-04"])
        assert result.exit_code == 0
        assert "Year: 2024" in result.output

    def test_to_datetime_slash_separator(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with slash separators."""

        @command()
        @option("date", default=None)
        @to_datetime("DD/MM/YYYY")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "04/12/2024"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_dot_separator(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with dot separators."""

        @command()
        @option("date", default=None)
        @to_datetime("DD.MM.YYYY")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "04.12.2024"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_no_separator(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with no separators."""

        @command()
        @option("date", default=None)
        @to_datetime("YYYYMMDD")
        def cmd(date: Any) -> None:
            assert isinstance(date, datetime)
            click.echo(f"Date: {date.date()}")

        result = cli_runner.invoke(cmd, ["--date", "20241204"])
        assert result.exit_code == 0
        assert "Date: 2024-12-04" in result.output

    def test_to_datetime_12_hour_format(self, cli_runner: CliRunner) -> None:
        """Test to_datetime with 12-hour time format."""

        @command()
        @option("datetime_val", default=None)
        @to_datetime("%Y-%m-%d %I:%M %p")
        def cmd(datetime_val: Any) -> None:
            assert isinstance(datetime_val, datetime)
            click.echo(f"Hour: {datetime_val.hour}")

        result = cli_runner.invoke(
            cmd, ["--datetime-val", "2024-12-04 02:30 PM"]
        )
        assert result.exit_code == 0
        assert "Hour: 14" in result.output


class TestToDatetimePractical:
    """Test practical use cases for to_datetime."""

    def test_to_datetime_log_timestamp(self, cli_runner: CliRunner) -> None:
        """Test to_datetime for parsing log timestamps."""

        @command()
        @option("timestamp", default=None)
        @to_datetime("%Y-%m-%d %H:%M:%S", tz="UTC")
        def cmd(timestamp: Any) -> None:
            assert isinstance(timestamp, datetime)
            click.echo(f"Log time: {timestamp.isoformat()}")

        result = cli_runner.invoke(cmd, ["--timestamp", "2024-12-04 10:30:00"])
        assert result.exit_code == 0
        assert "Log time:" in result.output

    def test_to_datetime_birth_date(self, cli_runner: CliRunner) -> None:
        """Test to_datetime for birth date handling multiple formats."""

        @command()
        @option("birth_date", default=None)
        @to_datetime("YYYY-MM-DD", "DD/MM/YYYY", "MM-DD-YYYY")
        def cmd(birth_date: Any) -> None:
            assert isinstance(birth_date, datetime)
            age = 2024 - birth_date.year
            click.echo(f"Age: {age}")

        result = cli_runner.invoke(cmd, ["--birth-date", "1990-06-15"])
        assert result.exit_code == 0
        assert "Age: 34" in result.output

    def test_to_datetime_event_schedule(self, cli_runner: CliRunner) -> None:
        """Test to_datetime for event scheduling with multiple dates."""

        @command()
        @argument("event_dates", nargs=-1)
        @to_datetime("YYYY-MM-DD")
        def cmd(event_dates: Any) -> None:
            assert isinstance(event_dates, tuple)
            click.echo(f"Total events: {len(event_dates)}")
            if event_dates:
                earliest = min(event_dates)
                click.echo(f"First event: {earliest.date()}")

        result = cli_runner.invoke(
            cmd, ["2024-12-10", "2024-12-15", "2024-12-20"]
        )
        assert result.exit_code == 0
        assert "Total events: 3" in result.output
        assert "First event: 2024-12-10" in result.output
