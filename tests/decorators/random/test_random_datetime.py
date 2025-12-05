"""Tests for random_datetime decorator."""

from datetime import datetime

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.decorators.random.random_datetime import random_datetime


class TestRandomDateTimeBasic:
    """Test basic random_datetime functionality."""

    def test_generates_datetime_in_range(self, cli_runner: CliRunner) -> None:
        """Test that it generates a datetime within the specified range."""

        @command()
        @random_datetime(
            "created", "2024-01-01 00:00:00", "2024-12-31 23:59:59", seed=6000
        )
        def cmd(created: datetime) -> None:
            click.echo(f"Created: {created}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        created_str = result.output.split("Created: ")[1].strip()
        created = datetime.fromisoformat(created_str)

        assert (
            datetime(2024, 1, 1)
            <= created
            <= datetime(2024, 12, 31, 23, 59, 59)
        )

    def test_date_only_format(self, cli_runner: CliRunner) -> None:
        """Test using date-only format (YYYY-MM-DD)."""

        @command()
        @random_datetime("date", "2024-01-01", "2024-01-31", seed=6001)
        def cmd(date: datetime) -> None:
            click.echo(f"Date: {date.strftime('%Y-%m-%d')}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Date: 2024-01-" in result.output

    def test_time_only_format(self, cli_runner: CliRunner) -> None:
        """Test using time-only format (HH:MM:SS) for today."""

        @command()
        @random_datetime("time", "00:00:00", "23:59:59", seed=6002)
        def cmd(time: datetime) -> None:
            click.echo(f"Time: {time.strftime('%H:%M:%S')}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        output = result.output.split("Time: ")[1].strip()
        datetime.strptime(output, "%H:%M:%S")

    def test_datetime_object_input(self, cli_runner: CliRunner) -> None:
        """Test using datetime objects directly."""

        start = datetime(2024, 6, 1, 12, 0, 0)
        end = datetime(2024, 6, 1, 18, 0, 0)

        @command()
        @random_datetime("appointment", start, end, seed=6003)
        def cmd(appointment: datetime) -> None:
            click.echo(f"Hour: {appointment.hour}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        hour = int(result.output.split("Hour: ")[1].strip())
        assert 12 <= hour <= 18

    def test_different_seeds_different_results(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different seeds produce different results."""

        results: list[str] = []
        for i in range(10):

            @command()
            @random_datetime(
                "timestamp",
                "2024-01-01 00:00:00",
                "2024-01-01 23:59:59",
                seed=6100 + i,
            )
            def cmd(timestamp: datetime) -> None:
                click.echo(f"{timestamp}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        assert len(set(results)) > 1


class TestRandomDateTimeKeywords:
    """Test special keyword support."""

    def test_keyword_now(self, cli_runner: CliRunner) -> None:
        """Test 'now' keyword."""

        @command()
        @random_datetime("timestamp", "2020-01-01", "now", seed=6200)
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Year: {timestamp.year}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        year = int(result.output.split("Year: ")[1].strip())
        assert 2020 <= year <= datetime.now().year

    def test_keyword_today(self, cli_runner: CliRunner) -> None:
        """Test 'today' keyword (midnight)."""

        @command()
        @random_datetime("start", "today", "now", seed=6201)
        def cmd(start: datetime) -> None:
            click.echo(f"Date: {start.strftime('%Y-%m-%d')}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        date_str = result.output.split("Date: ")[1].strip()
        assert date_str == datetime.now().strftime("%Y-%m-%d")

    def test_keyword_yesterday(self, cli_runner: CliRunner) -> None:
        """Test 'yesterday' keyword."""

        @command()
        @random_datetime("event", "yesterday", "today", seed=6202)
        def cmd(event: datetime) -> None:
            click.echo(f"Timestamp: {event}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0

    def test_keyword_tomorrow(self, cli_runner: CliRunner) -> None:
        """Test 'tomorrow' keyword."""

        @command()
        @random_datetime("future", "today", "tomorrow", seed=6203)
        def cmd(future: datetime) -> None:
            click.echo(f"Timestamp: {future}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0


class TestRandomDateTimeTimezones:
    """Test timezone support."""

    def test_utc_timezone(self, cli_runner: CliRunner) -> None:
        """Test UTC timezone."""

        @command()
        @random_datetime(
            "timestamp",
            "2024-01-01 00:00:00",
            "2024-01-02 00:00:00",
            timezone="UTC",
            seed=6300,
        )
        def cmd(timestamp: datetime) -> None:
            click.echo(f"TZ: {timestamp.tzname()}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "TZ: UTC" in result.output

    def test_us_eastern_timezone(self, cli_runner: CliRunner) -> None:
        """Test America/New_York timezone."""

        @command()
        @random_datetime(
            "timestamp",
            "2024-06-01 00:00:00",
            "2024-06-02 00:00:00",
            timezone="America/New_York",
            seed=6301,
        )
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Has TZ: {timestamp.tzinfo is not None}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Has TZ: True" in result.output

    def test_europe_stockholm_timezone(self, cli_runner: CliRunner) -> None:
        """Test Europe/Stockholm timezone."""

        @command()
        @random_datetime(
            "timestamp",
            "2024-06-01 00:00:00",
            "2024-06-02 00:00:00",
            timezone="Europe/Stockholm",
            seed=6302,
        )
        def cmd(timestamp: datetime) -> None:
            click.echo(f"TZ Name: {timestamp.tzname()}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "TZ Name: CEST" in result.output

    def test_timezone_naive_by_default(self, cli_runner: CliRunner) -> None:
        """Test that datetime is timezone-naive by default."""

        @command()
        @random_datetime("timestamp", "2024-01-01", "2024-01-02", seed=6303)
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Has TZ: {timestamp.tzinfo is not None}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Has TZ: False" in result.output

    def test_invalid_timezone_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that invalid timezone raises error."""

        @command()
        @random_datetime(
            "timestamp",
            "2024-01-01",
            "2024-01-02",
            timezone="Invalid/Timezone",
            seed=6304,
        )
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Timestamp: {timestamp}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "Invalid timezone" in result.output


class TestRandomDateTimeErrors:
    """Test error conditions."""

    def test_start_after_end_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that start_date after end_date raises error."""

        @command()
        @random_datetime("timestamp", "2024-12-31", "2024-01-01", seed=6400)
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Timestamp: {timestamp}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "start_date must be before end_date" in result.output

    def test_invalid_format_raises_error(self, cli_runner: CliRunner) -> None:
        """Test that invalid date format raises error."""

        @command()
        @random_datetime("timestamp", "01/01/2024", "12/31/2024", seed=6401)
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Timestamp: {timestamp}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "Unable to parse datetime" in result.output

    def test_tomorrow_before_yesterday_raises_error(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that tomorrow before yesterday raises error."""

        @command()
        @random_datetime("timestamp", "tomorrow", "yesterday", seed=6402)
        def cmd(timestamp: datetime) -> None:
            click.echo(f"Timestamp: {timestamp}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 1
        assert "start_date must be before end_date" in result.output


class TestRandomDateTimeDistribution:
    """Test distribution properties."""

    def test_covers_full_range(self, cli_runner: CliRunner) -> None:
        """Test that generated datetimes cover the full range."""

        hours: set[int] = set()
        for i in range(50):

            @command()
            @random_datetime(
                "timestamp",
                "2024-01-01 00:00:00",
                "2024-01-01 23:59:59",
                seed=6500 + i,
            )
            def cmd(timestamp: datetime) -> None:
                click.echo(f"{timestamp.hour}")

            result = cli_runner.invoke(cmd)
            hour = int(result.output.strip())
            hours.add(hour)

        assert len(hours) >= 10

    def test_same_seed_same_result(self, cli_runner: CliRunner) -> None:
        """Test that same seed produces same result."""

        results: list[str] = []
        for _ in range(3):

            @command()
            @random_datetime(
                "timestamp",
                "2024-01-01 00:00:00",
                "2024-12-31 23:59:59",
                seed=6600,
            )
            def cmd(timestamp: datetime) -> None:
                click.echo(f"{timestamp}")

            result = cli_runner.invoke(cmd)
            results.append(result.output.strip())

        assert len(set(results)) == 1


class TestRandomDateTimeIntegration:
    """Test integration with other decorators."""

    def test_multiple_random_datetimes(self, cli_runner: CliRunner) -> None:
        """Test multiple random_datetime decorators."""

        @command()
        @random_datetime("start", "2024-01-01", "2024-06-30", seed=6700)
        @random_datetime("end", "2024-07-01", "2024-12-31", seed=6701)
        def cmd(start: datetime, end: datetime) -> None:
            click.echo(f"Start: {start.year}, End: {end.year}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Start: 2024, End: 2024" in result.output

    def test_datetime_with_timezone_formatting(
        self, cli_runner: CliRunner
    ) -> None:
        """Test datetime output with timezone."""

        @command()
        @random_datetime(
            "event",
            "2024-01-01 00:00:00",
            "2024-01-01 12:00:00",
            timezone="UTC",
            seed=6702,
        )
        def cmd(event: datetime) -> None:
            formatted = event.strftime("%Y-%m-%d %H:%M:%S %Z")
            click.echo(f"Event: {formatted}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Event: 2024-01-01" in result.output
        assert "UTC" in result.output


class TestRandomDateTimePractical:
    """Test practical use cases."""

    def test_appointment_scheduling(self, cli_runner: CliRunner) -> None:
        """Test scheduling appointments in business hours."""

        @command()
        @random_datetime(
            "appointment",
            "2024-01-15 09:00:00",  # 9 AM
            "2024-01-15 17:00:00",  # 5 PM
            seed=6800,
        )
        def cmd(appointment: datetime) -> None:
            click.echo(f"Hour: {appointment.hour}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        hour = int(result.output.split("Hour: ")[1].strip())
        assert 9 <= hour <= 17

    def test_log_timestamp_generation(self, cli_runner: CliRunner) -> None:
        """Test generating log timestamps for last 7 days."""

        @command()
        @random_datetime("log_time", "yesterday", "now", seed=6801)
        def cmd(log_time: datetime) -> None:
            click.echo(f"Log: {log_time.strftime('%Y-%m-%d %H:%M:%S')}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Log: " in result.output

    def test_historical_data_generation(self, cli_runner: CliRunner) -> None:
        """Test generating historical timestamps."""

        years: set[int] = set()
        for i in range(20):

            @command()
            @random_datetime(
                "historical",
                "2020-01-01",
                "2024-12-31",
                seed=6900 + i,
            )
            def cmd(historical: datetime) -> None:
                click.echo(f"{historical.year}")

            result = cli_runner.invoke(cmd)
            year = int(result.output.strip())
            years.add(year)

        assert len(years) >= 3
