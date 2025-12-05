"""Tests for the `to_date` decorator."""

from datetime import date as date_type
from typing import Any

from click.testing import CliRunner

from click_extended import command, option
from click_extended.decorators.transform.to_date import to_date


class TestToDateBasic:
    """Tests basic functionality of `to_date`."""

    def test_to_date_basic(self, cli_runner: CliRunner) -> None:
        """Test basic date parsing with default format."""

        @command()
        @option("date", default=None)
        @to_date()
        def cmd(date: Any) -> None:
            assert isinstance(date, date_type)
            assert date == date_type(2024, 1, 15)

        result = cli_runner.invoke(cmd, ["--date", "2024-01-15"])
        assert result.exit_code == 0

    def test_to_date_with_option(self, cli_runner: CliRunner) -> None:
        """Test to_date with option."""

        @command()
        @option("date", default=None)
        @to_date()
        def cmd(date: Any) -> None:
            assert isinstance(date, date_type)
            assert date == date_type(2024, 12, 25)

        result = cli_runner.invoke(cmd, ["--date", "2024-12-25"])
        assert result.exit_code == 0


class TestToDateMultipleFormats:
    """Tests for multiple format support."""

    def test_to_date_multiple_formats_first_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that first matching format is used."""

        @command()
        @option("date", default=None)
        @to_date("%Y-%m-%d", "%d/%m/%Y")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 3, 15)

        result = cli_runner.invoke(cmd, ["--date", "2024-03-15"])
        assert result.exit_code == 0

    def test_to_date_multiple_formats_second_match(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that second format is tried if first fails."""

        @command()
        @option("date", default=None)
        @to_date("%Y-%m-%d", "%d/%m/%Y")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 3, 15)

        result = cli_runner.invoke(cmd, ["--date", "15/03/2024"])
        assert result.exit_code == 0

    def test_to_date_simplified_format(self, cli_runner: CliRunner) -> None:
        """Test simplified format notation (YYYY-MM-DD)."""

        @command()
        @option("date", default=None)
        @to_date("YYYY-MM-DD")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 6, 30)

        result = cli_runner.invoke(cmd, ["--date", "2024-06-30"])
        assert result.exit_code == 0

    def test_to_date_mixed_formats(self, cli_runner: CliRunner) -> None:
        """Test mixing simplified and strptime formats."""

        @command()
        @option("date", default=None)
        @to_date("YYYY-MM-DD", "%d/%m/%Y", "MM/DD/YYYY")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 4, 7)

        result = cli_runner.invoke(cmd, ["--date", "07/04/2024"])
        assert result.exit_code == 0


class TestToDateTuples:
    """Tests for tuple support."""

    def test_to_date_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_date with flat tuple."""

        @command()
        @option("dates", default=None, nargs=2)
        @to_date()
        def cmd(dates: Any) -> None:
            assert isinstance(dates, tuple)
            assert len(dates) == 2  # type: ignore
            assert all(isinstance(d, date_type) for d in dates)  # type: ignore
            assert dates[0] == date_type(2024, 1, 1)
            assert dates[1] == date_type(2024, 12, 31)

        result = cli_runner.invoke(cmd, ["--dates", "2024-01-01", "2024-12-31"])
        assert result.exit_code == 0

    def test_to_date_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test to_date with nested tuple (multiple option)."""

        @command()
        @option("dates", multiple=True, nargs=2)
        @to_date()
        def cmd(dates: Any) -> None:
            assert isinstance(dates, tuple)
            assert len(dates) == 2  # type: ignore
            assert all(isinstance(t, tuple) for t in dates)  # type: ignore
            assert dates[0][0] == date_type(2024, 1, 1)
            assert dates[0][1] == date_type(2024, 6, 30)
            assert dates[1][0] == date_type(2024, 7, 1)
            assert dates[1][1] == date_type(2024, 12, 31)

        result = cli_runner.invoke(
            cmd,
            [
                "--dates",
                "2024-01-01",
                "2024-06-30",
                "--dates",
                "2024-07-01",
                "2024-12-31",
            ],
        )
        assert result.exit_code == 0


class TestToDateErrors:
    """Tests for error handling."""

    def test_to_date_invalid_format(self, cli_runner: CliRunner) -> None:
        """Test error for invalid date format."""

        @command()
        @option("date", default=None)
        @to_date()
        def cmd(date: Any) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--date", "not-a-date"])
        assert result.exit_code != 0
        assert "Invalid date" in result.output

    def test_to_date_no_matching_format(self, cli_runner: CliRunner) -> None:
        """Test error when no format matches."""

        @command()
        @option("date", default=None)
        @to_date("%Y-%m-%d")
        def cmd(date: Any) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--date", "15/03/2024"])
        assert result.exit_code != 0
        assert "Invalid date" in result.output


class TestToDateFormatVariations:
    """Tests for different format variations."""

    def test_to_date_european_format(self, cli_runner: CliRunner) -> None:
        """Test European date format (DD/MM/YYYY)."""

        @command()
        @option("date", default=None)
        @to_date("DD/MM/YYYY")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 3, 15)

        result = cli_runner.invoke(cmd, ["--date", "15/03/2024"])
        assert result.exit_code == 0

    def test_to_date_american_format(self, cli_runner: CliRunner) -> None:
        """Test American date format (MM/DD/YYYY)."""

        @command()
        @option("date", default=None)
        @to_date("MM/DD/YYYY")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 3, 15)

        result = cli_runner.invoke(cmd, ["--date", "03/15/2024"])
        assert result.exit_code == 0

    def test_to_date_short_year(self, cli_runner: CliRunner) -> None:
        """Test short year format (YY)."""

        @command()
        @option("date", default=None)
        @to_date("YY-MM-DD")
        def cmd(date: Any) -> None:
            assert date.year == 2024
            assert date.month == 6
            assert date.day == 15

        result = cli_runner.invoke(cmd, ["--date", "24-06-15"])
        assert result.exit_code == 0

    def test_to_date_no_separators(self, cli_runner: CliRunner) -> None:
        """Test date format without separators."""

        @command()
        @option("date", default=None)
        @to_date("YYYYMMDD")
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 7, 4)

        result = cli_runner.invoke(cmd, ["--date", "20240704"])
        assert result.exit_code == 0


class TestToDatePractical:
    """Practical usage tests."""

    def test_to_date_birthday(self, cli_runner: CliRunner) -> None:
        """Test parsing birthday date."""

        @command()
        @option("birthday", required=True)
        @to_date("YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY")
        def cmd(birthday: Any) -> None:
            assert isinstance(birthday, date_type)
            today = date_type.today()
            age = (
                today.year
                - birthday.year
                - ((today.month, today.day) < (birthday.month, birthday.day))
            )
            assert age >= 0

        result = cli_runner.invoke(cmd, ["--birthday", "1990-05-15"])
        assert result.exit_code == 0

    def test_to_date_date_range(self, cli_runner: CliRunner) -> None:
        """Test parsing date range."""

        @command()
        @option("start", required=True)
        @to_date()
        @option("end", required=True)
        @to_date()
        def cmd(start: Any, end: Any) -> None:
            assert isinstance(start, date_type)
            assert isinstance(end, date_type)
            assert start < end
            days = (end - start).days
            assert days > 0

        result = cli_runner.invoke(
            cmd, ["--start", "2024-01-01", "--end", "2024-12-31"]
        )
        assert result.exit_code == 0

    def test_to_date_leap_year(self, cli_runner: CliRunner) -> None:
        """Test parsing leap year date."""

        @command()
        @option("date", default=None)
        @to_date()
        def cmd(date: Any) -> None:
            assert date == date_type(2024, 2, 29)
            assert date.year % 4 == 0

        result = cli_runner.invoke(cmd, ["--date", "2024-02-29"])
        assert result.exit_code == 0
