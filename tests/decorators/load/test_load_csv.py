"""Tests for load_csv decorator."""

from pathlib import Path
from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.load.load_csv import load_csv
from click_extended.decorators.transform.to_path import to_path


class TestLoadCsvBasic:
    """Test basic load_csv functionality."""

    def test_load_csv_as_dict(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with as_dict=True (default)."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")
            click.echo(f"First name: {file[0]['name']}")
            click.echo(f"First age: {file[0]['age']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 2" in result.output
        assert "First name: Alice" in result.output
        assert "First age: 30" in result.output

    def test_load_csv_as_list(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with as_dict=False."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(as_dict=False, has_header=True)
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")
            click.echo(f"First row: {file[0]}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 2" in result.output
        assert "['Alice', '30', 'NYC']" in result.output

    def test_load_csv_no_header(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv without header."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Alice,30,NYC\nBob,25,LA\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(as_dict=False, has_header=False)
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")
            click.echo(f"First: {file[0][0]}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 2" in result.output
        assert "First: Alice" in result.output

    def test_load_csv_empty_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 0" in result.output

    def test_load_csv_single_row(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with single data row."""
        csv_file = tmp_path / "single.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")
            click.echo(f"Name: {file[0]['name']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 1" in result.output
        assert "Name: Alice" in result.output


class TestLoadCsvDelimiters:
    """Test load_csv with different delimiters."""

    def test_load_csv_comma_delimiter(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with comma delimiter (default)."""
        csv_file = tmp_path / "comma.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Name: {file[0]['name']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output

    def test_load_csv_tab_delimiter(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with tab delimiter."""
        csv_file = tmp_path / "tab.csv"
        csv_file.write_text("name\tage\nAlice\t30\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(delimiter="\t")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Name: {file[0]['name']}")
            click.echo(f"Age: {file[0]['age']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output
        assert "Age: 30" in result.output

    def test_load_csv_semicolon_delimiter(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with semicolon delimiter."""
        csv_file = tmp_path / "semicolon.csv"
        csv_file.write_text("name;age;city\nAlice;30;NYC\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(delimiter=";")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"City: {file[0]['city']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "City: NYC" in result.output

    def test_load_csv_pipe_delimiter(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with pipe delimiter."""
        csv_file = tmp_path / "pipe.csv"
        csv_file.write_text("name|age|city\nAlice|30|NYC\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(delimiter="|")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Name: {file[0]['name']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output


class TestLoadCsvEmptyRows:
    """Test load_csv with empty rows."""

    def test_load_csv_skip_empty_rows(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv skips empty rows by default."""
        csv_file = tmp_path / "with_empty.csv"
        csv_file.write_text("name,age\nAlice,30\n\nBob,25\n\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(skip_empty=True)
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 2" in result.output

    def test_load_csv_keep_empty_rows(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv keeps empty rows when skip_empty=False."""
        csv_file = tmp_path / "with_empty.csv"
        csv_file.write_text("name,age\nAlice,30\n,\nBob,25\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(skip_empty=False)
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 3" in result.output


class TestLoadCsvEncoding:
    """Test load_csv encoding parameter."""

    def test_load_csv_utf8_encoding(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with UTF-8 encoding (default)."""
        csv_file = tmp_path / "utf8.csv"
        csv_file.write_text(
            "name,message\nAlice,Hello 世界 🌍\n", encoding="utf-8"
        )

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(encoding="utf-8")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Message: {file[0]['message']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Hello 世界 🌍" in result.output

    def test_load_csv_custom_encoding(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with custom encoding."""
        csv_file = tmp_path / "latin1.csv"
        csv_file.write_text("name,text\nAlice,café\n", encoding="latin-1")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(encoding="latin-1")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Text: {file[0]['text']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "café" in result.output


class TestLoadCsvDialects:
    """Test load_csv dialect parameter."""

    def test_load_csv_excel_dialect(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with excel dialect."""
        csv_file = tmp_path / "excel.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(dialect="excel")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Name: {file[0]['name']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Name: Alice" in result.output

    def test_load_csv_unix_dialect(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with unix dialect."""
        csv_file = tmp_path / "unix.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv(dialect="unix")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Count: {len(file)}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Count: 1" in result.output


class TestLoadCsvErrors:
    """Test load_csv error handling."""

    def test_load_csv_directory_path(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv rejects directory paths."""
        test_dir = tmp_path / "dir"
        test_dir.mkdir()

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--file", str(test_dir)])
        assert result.exit_code != 0
        assert "is a directory" in result.output.lower()

    def test_load_csv_nonexistent_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with nonexistent file."""
        csv_file = tmp_path / "nonexistent.csv"

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()


class TestLoadCsvSpecialCases:
    """Test load_csv with special cases."""

    def test_load_csv_quoted_fields(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with quoted fields."""
        csv_file = tmp_path / "quoted.csv"
        csv_file.write_text(
            'name,description\nAlice,"Has, comma"\nBob,"Has ""quotes"""\n'
        )

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Alice desc: {file[0]['description']}")
            click.echo(f"Bob desc: {file[1]['description']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Alice desc: Has, comma" in result.output
        assert 'Bob desc: Has "quotes"' in result.output

    def test_load_csv_multiline_fields(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with multiline fields."""
        csv_file = tmp_path / "multiline.csv"
        csv_file.write_text('name,notes\nAlice,"Line 1\nLine 2"\n')

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Has newline: {'Line 2' in file[0]['notes']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Has newline: True" in result.output

    def test_load_csv_unicode_content(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with Unicode content."""
        csv_file = tmp_path / "unicode.csv"
        csv_file.write_text(
            "name,city\nAlice,北京\nBob,東京\n", encoding="utf-8"
        )

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"City 1: {file[0]['city']}")
            click.echo(f"City 2: {file[1]['city']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "City 1: 北京" in result.output
        assert "City 2: 東京" in result.output


class TestLoadCsvPractical:
    """Test practical use cases for load_csv."""

    def test_load_csv_data_processing(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv for data processing."""
        csv_file = tmp_path / "users.csv"
        csv_file.write_text(
            "name,age,score\nAlice,30,85\nBob,25,90\nCharlie,35,78\n"
        )

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            total_score = sum(int(row["score"]) for row in file)
            avg_score = total_score / len(file)
            click.echo(f"Total users: {len(file)}")
            click.echo(f"Average score: {avg_score:.1f}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Total users: 3" in result.output
        assert "Average score: 84.3" in result.output

    def test_load_csv_with_to_path_validation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv chained with to_path validation."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("id,value\n1,test\n")

        @command()
        @option("file", default=None)
        @to_path(
            extensions=[".csv"],
            allow_directory=False,
            allow_empty_file=False,
        )
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"ID: {file[0]['id']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "ID: 1" in result.output

    def test_load_csv_large_dataset(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with larger dataset."""
        csv_file = tmp_path / "large.csv"
        rows = ["name,age,score"]
        for i in range(100):
            rows.append(f"User{i},{20 + i % 50},{50 + i % 50}")
        csv_file.write_text("\n".join(rows) + "\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_csv()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Total rows: {len(file)}")
            click.echo(f"First: {file[0]['name']}")
            click.echo(f"Last: {file[-1]['name']}")

        result = cli_runner.invoke(cmd, ["--file", str(csv_file)])
        assert result.exit_code == 0
        assert "Total rows: 100" in result.output
        assert "First: User0" in result.output
        assert "Last: User99" in result.output


class TestLoadCsvFlatTuple:
    """Test load_csv with flat tuples."""

    def test_load_csv_flat_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with flat tuple of CSV files."""
        file1 = tmp_path / "data1.csv"
        file2 = tmp_path / "data2.csv"
        file3 = tmp_path / "data3.csv"
        file1.write_text("name,value\nA,10\nB,20\n")
        file2.write_text("name,value\nC,30\nD,40\n")
        file3.write_text("name,value\nE,50\nF,60\n")

        @command()
        @option("files", default=None, nargs=3)
        @to_path()
        @load_csv()
        def cmd(files: Any) -> None:
            assert files is not None
            assert isinstance(files, tuple)
            assert len(files) == 3
            total = sum(
                sum(int(row["value"]) for row in csv_data) for csv_data in files
            )
            click.echo(f"Total: {total}")

        result = cli_runner.invoke(
            cmd, ["--files", str(file1), str(file2), str(file3)]
        )
        assert result.exit_code == 0
        assert "Total: 210" in result.output

    def test_load_csv_flat_tuple_as_list(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv flat tuple with as_dict=False."""
        file1 = tmp_path / "data1.csv"
        file2 = tmp_path / "data2.csv"
        file1.write_text("1,2,3\n4,5,6\n")
        file2.write_text("7,8,9\n10,11,12\n")

        @command()
        @option("files", default=None, nargs=2)
        @to_path()
        @load_csv(as_dict=False, has_header=False)
        def cmd(files: Any) -> None:
            assert files is not None
            total = sum(
                sum(int(cell) for row in csv_data for cell in row)
                for csv_data in files
            )
            click.echo(f"Total: {total}")

        result = cli_runner.invoke(cmd, ["--files", str(file1), str(file2)])
        assert result.exit_code == 0
        assert "Total: 78" in result.output


class TestLoadCsvNestedTuple:
    """Test load_csv with nested tuples."""

    def test_load_csv_nested_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv with nested tuple of CSV files."""
        file1 = tmp_path / "quarter1_jan.csv"
        file2 = tmp_path / "quarter1_feb.csv"
        file3 = tmp_path / "quarter2_mar.csv"
        file4 = tmp_path / "quarter2_apr.csv"
        file1.write_text("month,revenue\nJan,1000\n")
        file2.write_text("month,revenue\nFeb,1500\n")
        file3.write_text("month,revenue\nMar,2000\n")
        file4.write_text("month,revenue\nApr,2500\n")

        @command()
        @option("quarters", multiple=True, nargs=2)
        @to_path()
        @load_csv()
        def cmd(quarters: Any) -> None:
            assert quarters is not None
            assert isinstance(quarters, tuple)
            assert len(quarters) == 2
            for i, quarter in enumerate(quarters, 1):
                total = sum(int(csv_data[0]["revenue"]) for csv_data in quarter)
                click.echo(f"Q{i}: ${total}")

        result = cli_runner.invoke(
            cmd,
            [
                "--quarters",
                str(file1),
                str(file2),
                "--quarters",
                str(file3),
                str(file4),
            ],
        )
        assert result.exit_code == 0
        assert "Q1: $2500" in result.output
        assert "Q2: $4500" in result.output

    def test_load_csv_nested_tuple_data_aggregation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_csv nested tuple for data aggregation."""
        region1_store1 = tmp_path / "region1_store1.csv"
        region1_store2 = tmp_path / "region1_store2.csv"
        region2_store1 = tmp_path / "region2_store1.csv"
        region2_store2 = tmp_path / "region2_store2.csv"
        region1_store1.write_text("item,sales\nA,100\nB,150\n")
        region1_store2.write_text("item,sales\nA,120\nB,180\n")
        region2_store1.write_text("item,sales\nA,200\nB,250\n")
        region2_store2.write_text("item,sales\nA,220\nB,280\n")

        @command()
        @option("regions", multiple=True, nargs=2)
        @to_path()
        @load_csv()
        def cmd(regions: Any) -> None:
            assert regions is not None
            for i, region in enumerate(regions, 1):
                total = sum(
                    int(row["sales"]) for csv_data in region for row in csv_data
                )
                click.echo(f"Region {i}: {total} sales")

        result = cli_runner.invoke(
            cmd,
            [
                "--regions",
                str(region1_store1),
                str(region1_store2),
                "--regions",
                str(region2_store1),
                str(region2_store2),
            ],
        )
        assert result.exit_code == 0
        assert "Region 1: 550 sales" in result.output
        assert "Region 2: 950 sales" in result.output
