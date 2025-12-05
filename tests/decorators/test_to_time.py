"""Tests for to_time decorator."""

from datetime import time
from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.decorators.argument import argument
from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.to_time import to_time


class TestToTimeBasic:
    """Test basic to_time functionality."""

    def test_to_time_single_format_strptime(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time with single Python strptime format."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 45" in result.output

    def test_to_time_single_format_simplified(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time with single simplified format."""

        @command()
        @option("time_val", default=None)
        @to_time("HH:mm:SS")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 45" in result.output

    def test_to_time_without_seconds(self, cli_runner: CliRunner) -> None:
        """Test to_time with format without seconds."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 0" in result.output

    def test_to_time_simplified_without_seconds(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time with simplified format without seconds."""

        @command()
        @option("time_val", default=None)
        @to_time("HH:mm")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")

        result = cli_runner.invoke(cmd, ["--time-val", "09:15"])
        assert result.exit_code == 0
        assert "Hour: 9" in result.output
        assert "Minute: 15" in result.output

    def test_to_time_default_formats(self, cli_runner: CliRunner) -> None:
        """Test to_time with default formats."""

        @command()
        @option("time_val", default=None)
        @to_time()
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Time: {time_val}")

        # Should accept HH:MM:SS format (default)
        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0


class TestToTimeMultipleFormats:
    """Test to_time with multiple format fallbacks."""

    def test_to_time_multiple_formats_first_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time tries first format and succeeds."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S", "%H:%M", "%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output

    def test_to_time_multiple_formats_second_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time falls back to second format."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S", "%H:%M", "%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output

    def test_to_time_multiple_formats_third_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time falls back to third format."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S", "%H:%M", "%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "02:30 PM"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output

    def test_to_time_mixed_format_styles(self, cli_runner: CliRunner) -> None:
        """Test to_time with mix of strptime and simplified formats."""

        @command()
        @option("time_val", default=None)
        @to_time("HH:mm:SS", "%I:%M %p", "HH:mm")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        # Test first format (simplified)
        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output

        # Test second format (strptime)
        result = cli_runner.invoke(cmd, ["--time-val", "02:30 PM"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output

        # Test third format (simplified)
        result = cli_runner.invoke(cmd, ["--time-val", "14:30"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output


class TestToTime12HourFormat:
    """Test to_time with 12-hour clock formats."""

    def test_to_time_12_hour_with_am(self, cli_runner: CliRunner) -> None:
        """Test to_time with 12-hour AM format."""

        @command()
        @option("time_val", default=None)
        @to_time("%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")

        result = cli_runner.invoke(cmd, ["--time-val", "09:30 AM"])
        assert result.exit_code == 0
        assert "Hour: 9" in result.output
        assert "Minute: 30" in result.output

    def test_to_time_12_hour_with_pm(self, cli_runner: CliRunner) -> None:
        """Test to_time with 12-hour PM format."""

        @command()
        @option("time_val", default=None)
        @to_time("%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "03:45 PM"])
        assert result.exit_code == 0
        assert "Hour: 15" in result.output

    def test_to_time_12_hour_with_seconds(self, cli_runner: CliRunner) -> None:
        """Test to_time with 12-hour format including seconds."""

        @command()
        @option("time_val", default=None)
        @to_time("%I:%M:%S %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "11:30:45 PM"])
        assert result.exit_code == 0
        assert "Hour: 23" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 45" in result.output

    def test_to_time_noon(self, cli_runner: CliRunner) -> None:
        """Test to_time with noon (12:00 PM)."""

        @command()
        @option("time_val", default=None)
        @to_time("%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "12:00 PM"])
        assert result.exit_code == 0
        assert "Hour: 12" in result.output

    def test_to_time_midnight(self, cli_runner: CliRunner) -> None:
        """Test to_time with midnight (12:00 AM)."""

        @command()
        @option("time_val", default=None)
        @to_time("%I:%M %p")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["--time-val", "12:00 AM"])
        assert result.exit_code == 0
        assert "Hour: 0" in result.output


class TestToTimeTuples:
    """Test to_time with tuple inputs."""

    def test_to_time_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_time with flat tuple of time strings."""

        @command()
        @argument("times", nargs=-1)
        @to_time("%H:%M:%S")
        def cmd(times: Any) -> None:
            assert isinstance(times, tuple)
            click.echo(f"Count: {len(times)}")
            for i, time_val in enumerate(times, 1):
                assert isinstance(time_val, time)
                click.echo(f"Time {i}: {time_val}")

        result = cli_runner.invoke(cmd, ["09:00:00", "12:30:00", "18:45:30"])
        assert result.exit_code == 0
        assert "Count: 3" in result.output
        assert "Time 1: 09:00:00" in result.output
        assert "Time 2: 12:30:00" in result.output
        assert "Time 3: 18:45:30" in result.output

    def test_to_time_flat_tuple_multiple_formats(
        self, cli_runner: CliRunner
    ) -> None:
        """Test to_time with tuple where different items match different formats."""

        @command()
        @argument("times", nargs=-1)
        @to_time("%H:%M:%S", "%H:%M", "%I:%M %p")
        def cmd(times: Any) -> None:
            assert isinstance(times, tuple)
            click.echo(f"Count: {len(times)}")
            for time_val in times:
                assert isinstance(time_val, time)
                click.echo(f"Hour: {time_val.hour}")

        result = cli_runner.invoke(cmd, ["14:30:45", "09:15", "03:00 PM"])
        assert result.exit_code == 0
        assert "Count: 3" in result.output

    def test_to_time_empty_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_time with empty tuple."""

        @command()
        @argument("times", nargs=-1, required=False)
        @to_time("%H:%M:%S")
        def cmd(times: Any) -> None:
            click.echo(f"Count: {len(times)}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Count: 0" in result.output


class TestToTimeErrors:
    """Test to_time error handling."""

    def test_to_time_invalid_format(self, cli_runner: CliRunner) -> None:
        """Test to_time with string that doesn't match format."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        result = cli_runner.invoke(cmd, ["--time-val", "not-a-time"])
        assert result.exit_code != 0
        assert "Invalid time" in result.output

    def test_to_time_no_matching_format(self, cli_runner: CliRunner) -> None:
        """Test to_time when no format matches."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S", "%I:%M %p")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        result = cli_runner.invoke(cmd, ["--time-val", "25:99:99"])
        assert result.exit_code != 0
        assert "Invalid time" in result.output

    def test_to_time_invalid_hour(self, cli_runner: CliRunner) -> None:
        """Test to_time with invalid hour value."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        result = cli_runner.invoke(cmd, ["--time-val", "25:30:00"])
        assert result.exit_code != 0

    def test_to_time_invalid_minute(self, cli_runner: CliRunner) -> None:
        """Test to_time with invalid minute value."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:99:00"])
        assert result.exit_code != 0

    def test_to_time_invalid_second(self, cli_runner: CliRunner) -> None:
        """Test to_time with invalid second value."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30:99"])
        assert result.exit_code != 0

    def test_to_time_partial_match(self, cli_runner: CliRunner) -> None:
        """Test to_time rejects partial format matches."""

        @command()
        @option("time_val", default=None)
        @to_time("%H:%M:%S")
        def cmd(time_val: Any) -> None:
            click.echo(f"Time: {time_val}")

        # Missing seconds
        result = cli_runner.invoke(cmd, ["--time-val", "14:30"])
        assert result.exit_code != 0


class TestToTimeFormatVariations:
    """Test various time format patterns."""

    def test_to_time_dot_separator(self, cli_runner: CliRunner) -> None:
        """Test to_time with dot separators."""

        @command()
        @option("time_val", default=None)
        @to_time("HH.mm.SS")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")

        result = cli_runner.invoke(cmd, ["--time-val", "14.30.45"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output

    def test_to_time_no_separator(self, cli_runner: CliRunner) -> None:
        """Test to_time with no separators."""

        @command()
        @option("time_val", default=None)
        @to_time("HHmmSS")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Hour: {time_val.hour}")
            click.echo(f"Minute: {time_val.minute}")
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "143045"])
        assert result.exit_code == 0
        assert "Hour: 14" in result.output
        assert "Minute: 30" in result.output
        assert "Second: 45" in result.output

    def test_to_time_lowercase_ss(self, cli_runner: CliRunner) -> None:
        """Test to_time with lowercase 'ss' for seconds."""

        @command()
        @option("time_val", default=None)
        @to_time("HH:mm:ss")
        def cmd(time_val: Any) -> None:
            assert isinstance(time_val, time)
            click.echo(f"Second: {time_val.second}")

        result = cli_runner.invoke(cmd, ["--time-val", "14:30:45"])
        assert result.exit_code == 0
        assert "Second: 45" in result.output


class TestToTimePractical:
    """Test practical use cases for to_time."""

    def test_to_time_business_hours(self, cli_runner: CliRunner) -> None:
        """Test to_time for business hours handling."""

        @command()
        @option("start", default=None)
        @to_time("HH:mm")
        @option("end", default=None)
        @to_time("HH:mm")
        def cmd(start: Any, end: Any) -> None:
            assert isinstance(start, time)
            assert isinstance(end, time)
            # Calculate duration in minutes
            start_mins = start.hour * 60 + start.minute
            end_mins = end.hour * 60 + end.minute
            duration = end_mins - start_mins
            click.echo(f"Duration: {duration} minutes")

        result = cli_runner.invoke(cmd, ["--start", "09:00", "--end", "17:30"])
        assert result.exit_code == 0
        assert "Duration: 510 minutes" in result.output

    def test_to_time_schedule(self, cli_runner: CliRunner) -> None:
        """Test to_time for scheduling multiple times."""

        @command()
        @argument("meeting_times", nargs=-1)
        @to_time("HH:mm")
        def cmd(meeting_times: Any) -> None:
            assert isinstance(meeting_times, tuple)
            click.echo(f"Total meetings: {len(meeting_times)}")
            if meeting_times:
                earliest = min(meeting_times)
                latest = max(meeting_times)
                click.echo(f"First: {earliest}")
                click.echo(f"Last: {latest}")

        result = cli_runner.invoke(cmd, ["09:00", "11:30", "14:00", "16:30"])
        assert result.exit_code == 0
        assert "Total meetings: 4" in result.output
        assert "First: 09:00:00" in result.output
        assert "Last: 16:30:00" in result.output

    def test_to_time_alarm_settings(self, cli_runner: CliRunner) -> None:
        """Test to_time for alarm/reminder settings."""

        @command()
        @option("alarm", default=None)
        @to_time("HH:mm", "%I:%M %p")
        def cmd(alarm: Any) -> None:
            assert isinstance(alarm, time)
            click.echo(f"Alarm set for: {alarm.strftime('%I:%M %p')}")

        # Test 24-hour format
        result = cli_runner.invoke(cmd, ["--alarm", "07:30"])
        assert result.exit_code == 0
        assert "Alarm set for: 07:30 AM" in result.output

        # Test 12-hour format
        result = cli_runner.invoke(cmd, ["--alarm", "07:30 PM"])
        assert result.exit_code == 0
        assert "Alarm set for: 07:30 PM" in result.output

    def test_to_time_timestamp_parsing(self, cli_runner: CliRunner) -> None:
        """Test to_time for parsing timestamps from logs."""

        @command()
        @option("timestamp", default=None)
        @to_time("%H:%M:%S")
        def cmd(timestamp: Any) -> None:
            assert isinstance(timestamp, time)
            click.echo(f"Log time: {timestamp}")

        result = cli_runner.invoke(cmd, ["--timestamp", "14:23:56"])
        assert result.exit_code == 0
        assert "Log time: 14:23:56" in result.output
