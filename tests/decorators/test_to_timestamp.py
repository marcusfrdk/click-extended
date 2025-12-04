"""Tests for the to_timestamp decorator."""

from datetime import date, datetime, time, timezone

import click
import pytest
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.to_date import to_date
from click_extended.decorators.to_datetime import to_datetime
from click_extended.decorators.to_time import to_time
from click_extended.decorators.to_timestamp import to_timestamp


class TestToTimestampBasic:
    """Test basic timestamp conversions."""

    def test_to_timestamp_datetime(self, cli_runner: CliRunner) -> None:
        """Test converting datetime to seconds timestamp."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="s")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_date(self, cli_runner: CliRunner) -> None:
        """Test converting date to seconds timestamp (midnight UTC)."""

        @command()
        @option("d", default=None)
        @to_date()
        @to_timestamp(unit="s")
        def cmd(d: int | None) -> None:
            assert isinstance(d, int)
            expected = int(
                datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc).timestamp()
            )
            assert d == expected

        result = cli_runner.invoke(cmd, ["--d", "2024-01-15"])
        assert result.exit_code == 0

    def test_to_timestamp_time(self, cli_runner: CliRunner) -> None:
        """Test converting time to seconds timestamp (today's date in UTC)."""

        @command()
        @option("t", default=None)
        @to_time()
        @to_timestamp(unit="s")
        def cmd(t: int | None) -> None:
            assert isinstance(t, int)
            # Just verify it's a valid timestamp
            assert t > 0

        result = cli_runner.invoke(cmd, ["--t", "10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_aware_datetime(self, cli_runner: CliRunner) -> None:
        """Test converting timezone-aware datetime."""

        @command()
        @option("dt", default=None)
        @to_datetime(tz="UTC")
        @to_timestamp(unit="s")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_naive_datetime_assumes_utc(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that naive datetimes are assumed to be UTC."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="s")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0


class TestToTimestampUnits:
    """Test different unit conversions."""

    def test_to_timestamp_seconds(self, cli_runner: CliRunner) -> None:
        """Test conversion to seconds."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="s")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_milliseconds(self, cli_runner: CliRunner) -> None:
        """Test conversion to milliseconds."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="ms")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
                * 1000
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_microseconds(self, cli_runner: CliRunner) -> None:
        """Test conversion to microseconds."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="us")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
                * 1_000_000
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0

    def test_to_timestamp_nanoseconds(self, cli_runner: CliRunner) -> None:
        """Test conversion to nanoseconds."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="ns")
        def cmd(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc
                ).timestamp()
                * 1_000_000_000
            )
            assert dt == expected

        result = cli_runner.invoke(cmd, ["--dt", "2024-01-15 10:30:00"])
        assert result.exit_code == 0


class TestToTimestampPractical:
    """Test practical use cases."""

    def test_to_timestamp_logging_scenario(self, cli_runner: CliRunner) -> None:
        """Test timestamp for logging events with millisecond precision."""

        @command()
        @option("event_time", default=None)
        @to_datetime()
        @to_timestamp(unit="ms")
        def log_event(event_time: int | None) -> None:
            """Simulate logging with millisecond precision."""
            assert isinstance(event_time, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc
                ).timestamp()
                * 1000
            )
            assert event_time == expected
            assert event_time > 1705000000000  # After 2024-01-11
            click.echo(f"Event time: {event_time}")

        result = cli_runner.invoke(
            log_event, ["--event-time", "2024-01-15 10:30:45"]
        )
        assert result.exit_code == 0
        assert "Event time:" in result.output

    def test_to_timestamp_database_scenario(
        self, cli_runner: CliRunner
    ) -> None:
        """Test timestamp for database records with microsecond precision."""

        @command()
        @option("created_at", default=None)
        @to_datetime()
        @to_timestamp(unit="us")
        def store_record(created_at: int | None) -> None:
            """Simulate storing with microsecond precision."""
            assert isinstance(created_at, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc
                ).timestamp()
                * 1_000_000
            )
            assert created_at == expected
            click.echo(f"Created at: {created_at}")

        result = cli_runner.invoke(
            store_record, ["--created-at", "2024-01-15 10:30:45"]
        )
        assert result.exit_code == 0
        assert "Created at:" in result.output

    def test_to_timestamp_epoch_comparison(self, cli_runner: CliRunner) -> None:
        """Test comparing against Unix epoch."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="s")
        def check_epoch(dt: int | None) -> None:
            assert dt == 0  # Unix epoch
            click.echo(f"Epoch: {dt}")

        result = cli_runner.invoke(check_epoch, ["--dt", "1970-01-01 00:00:00"])
        assert result.exit_code == 0
        assert "Epoch: 0" in result.output

    def test_to_timestamp_high_precision(self, cli_runner: CliRunner) -> None:
        """Test nanosecond precision for high-precision timing."""

        @command()
        @option("dt", default=None)
        @to_datetime()
        @to_timestamp(unit="ns")
        def high_precision(dt: int | None) -> None:
            assert isinstance(dt, int)
            expected = int(
                datetime(
                    2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc
                ).timestamp()
                * 1_000_000_000
            )
            assert dt == expected
            assert dt > 1705000000000000000  # Nanosecond scale
            click.echo(f"Nanoseconds: {dt}")

        result = cli_runner.invoke(
            high_precision, ["--dt", "2024-01-15 10:30:45"]
        )
        assert result.exit_code == 0
        assert "Nanoseconds:" in result.output

    def test_to_timestamp_chained_with_to_date(
        self, cli_runner: CliRunner
    ) -> None:
        """Test chaining to_date with to_timestamp."""

        @command()
        @option("start_date", default=None)
        @to_date()
        @to_timestamp(unit="s")
        def process_date(start_date: int | None) -> None:
            assert isinstance(start_date, int)
            # Date should be converted to midnight UTC timestamp
            expected = int(
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp()
            )
            assert start_date == expected
            click.echo(f"Start date timestamp: {start_date}")

        result = cli_runner.invoke(process_date, ["--start-date", "2024-01-01"])
        assert result.exit_code == 0
        assert "Start date timestamp:" in result.output

    def test_to_timestamp_chained_with_to_time(
        self, cli_runner: CliRunner
    ) -> None:
        """Test chaining to_time with to_timestamp."""

        @command()
        @option("meeting_time", default=None)
        @to_time()
        @to_timestamp(unit="s")
        def process_time(meeting_time: int | None) -> None:
            assert isinstance(meeting_time, int)
            # Just verify it's a valid timestamp
            assert meeting_time > 0
            click.echo(f"Meeting time timestamp: {meeting_time}")

        result = cli_runner.invoke(process_time, ["--meeting-time", "14:30:00"])
        assert result.exit_code == 0
        assert "Meeting time timestamp:" in result.output
