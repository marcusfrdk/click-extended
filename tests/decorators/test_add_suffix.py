"""Tests for add_suffix decorator."""

from typing import Any

from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.add_suffix import add_suffix


class TestAddSuffixBasic:
    """Test basic add_suffix functionality."""

    def test_add_suffix_simple(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with simple string."""

        @command()
        @option("text", default=None)
        @add_suffix("_suf")
        def cmd(text: Any) -> None:
            assert text == "hello_suf"

        result = cli_runner.invoke(cmd, ["--text", "hello"])
        assert result.exit_code == 0

    def test_add_suffix_empty_string(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with empty string."""

        @command()
        @option("text", default=None)
        @add_suffix("_suffix")
        def cmd(text: Any) -> None:
            assert text == "_suffix"

        result = cli_runner.invoke(cmd, ["--text", ""])
        assert result.exit_code == 0

    def test_add_suffix_with_special_chars(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with special characters."""

        @command()
        @option("text", default=None)
        @add_suffix("_@#$")
        def cmd(text: Any) -> None:
            assert text == "test_@#$"

        result = cli_runner.invoke(cmd, ["--text", "test"])
        assert result.exit_code == 0

    def test_add_suffix_multiple_words(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with multi-word string."""

        @command()
        @option("text", default=None)
        @add_suffix(" World!")
        def cmd(text: Any) -> None:
            assert text == "Hello World!"

        result = cli_runner.invoke(cmd, ["--text", "Hello"])
        assert result.exit_code == 0

    def test_add_suffix_numbers(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with numbers."""

        @command()
        @option("text", default=None)
        @add_suffix(".txt")
        def cmd(text: Any) -> None:
            assert text == "file123.txt"

        result = cli_runner.invoke(cmd, ["--text", "file123"])
        assert result.exit_code == 0


class TestAddSuffixVariations:
    """Test add_suffix with different suffix types."""

    def test_add_suffix_file_extension(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for file extensions."""

        @command()
        @option("filename", default=None)
        @add_suffix(".json")
        def cmd(filename: Any) -> None:
            assert filename == "config.json"

        result = cli_runner.invoke(cmd, ["--filename", "config"])
        assert result.exit_code == 0

    def test_add_suffix_backup_naming(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for backup file naming."""

        @command()
        @option("filename", default=None)
        @add_suffix(".backup")
        def cmd(filename: Any) -> None:
            assert filename == "database.sql.backup"

        result = cli_runner.invoke(cmd, ["--filename", "database.sql"])
        assert result.exit_code == 0

    def test_add_suffix_timestamp_style(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for timestamp-style suffixes."""

        @command()
        @option("name", default=None)
        @add_suffix("_2024-12-04")
        def cmd(name: Any) -> None:
            assert name == "report_2024-12-04"

        result = cli_runner.invoke(cmd, ["--name", "report"])
        assert result.exit_code == 0

    def test_add_suffix_version_number(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for version numbers."""

        @command()
        @option("name", default=None)
        @add_suffix("-v1")
        def cmd(name: Any) -> None:
            assert name == "package-v1"

        result = cli_runner.invoke(cmd, ["--name", "package"])
        assert result.exit_code == 0


class TestAddSuffixFlatTuple:
    """Test add_suffix with flat tuples."""

    def test_add_suffix_flat_tuple(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with flat tuple of strings."""

        @command()
        @option("names", default=None, nargs=3)
        @add_suffix(".txt")
        def cmd(names: Any) -> None:
            assert names is not None
            assert isinstance(names, tuple)
            assert len(names) == 3
            assert names[0] == "file1.txt"
            assert names[1] == "file2.txt"
            assert names[2] == "file3.txt"

        result = cli_runner.invoke(cmd, ["--names", "file1", "file2", "file3"])
        assert result.exit_code == 0

    def test_add_suffix_flat_tuple_extensions(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_suffix with flat tuple for multiple extensions."""

        @command()
        @option("files", default=None, nargs=2)
        @add_suffix(".bak")
        def cmd(files: Any) -> None:
            assert files is not None
            assert files[0] == "data.csv.bak"
            assert files[1] == "config.json.bak"

        result = cli_runner.invoke(cmd, ["--files", "data.csv", "config.json"])
        assert result.exit_code == 0

    def test_add_suffix_flat_tuple_compiled_files(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_suffix with flat tuple for compiled file naming."""

        @command()
        @option("modules", default=None, nargs=4)
        @add_suffix(".o")
        def cmd(modules: Any) -> None:
            assert modules is not None
            assert len(modules) == 4
            assert all(mod.endswith(".o") for mod in modules)
            assert modules[0] == "main.o"
            assert modules[3] == "utils.o"

        result = cli_runner.invoke(
            cmd, ["--modules", "main", "app", "lib", "utils"]
        )
        assert result.exit_code == 0


class TestAddSuffixNestedTuple:
    """Test add_suffix with nested tuples."""

    def test_add_suffix_nested_tuple(self, cli_runner: CliRunner) -> None:
        """Test add_suffix with nested tuple of strings."""

        @command()
        @option("groups", multiple=True, nargs=2)
        @add_suffix(".log")
        def cmd(groups: Any) -> None:
            assert groups is not None
            assert isinstance(groups, tuple)
            assert len(groups) == 2
            assert groups[0][0] == "app.log"
            assert groups[0][1] == "error.log"
            assert groups[1][0] == "access.log"
            assert groups[1][1] == "debug.log"

        result = cli_runner.invoke(
            cmd,
            [
                "--groups",
                "app",
                "error",
                "--groups",
                "access",
                "debug",
            ],
        )
        assert result.exit_code == 0

    def test_add_suffix_nested_tuple_dated_backups(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_suffix nested tuple for dated backup files."""

        @command()
        @option("batches", multiple=True, nargs=2)
        @add_suffix("_20241204.bak")
        def cmd(batches: Any) -> None:
            assert batches is not None
            assert len(batches) == 2
            # First batch
            assert batches[0][0] == "db1_20241204.bak"
            assert batches[0][1] == "db2_20241204.bak"
            # Second batch
            assert batches[1][0] == "config1_20241204.bak"
            assert batches[1][1] == "config2_20241204.bak"

        result = cli_runner.invoke(
            cmd,
            [
                "--batches",
                "db1",
                "db2",
                "--batches",
                "config1",
                "config2",
            ],
        )
        assert result.exit_code == 0

    def test_add_suffix_nested_tuple_compressed_archives(
        self, cli_runner: CliRunner
    ) -> None:
        """Test add_suffix nested tuple for compressed archive naming."""

        @command()
        @option("archives", multiple=True, nargs=3)
        @add_suffix(".tar.gz")
        def cmd(archives: Any) -> None:
            assert archives is not None
            assert len(archives) == 2
            # First archive group
            for archive in archives[0]:
                assert archive.endswith(".tar.gz")
            # Second archive group
            assert archives[1][0] == "module1.tar.gz"
            assert archives[1][1] == "module2.tar.gz"
            assert archives[1][2] == "module3.tar.gz"

        result = cli_runner.invoke(
            cmd,
            [
                "--archives",
                "src",
                "docs",
                "tests",
                "--archives",
                "module1",
                "module2",
                "module3",
            ],
        )
        assert result.exit_code == 0


class TestAddSuffixPractical:
    """Test practical use cases for add_suffix."""

    def test_add_suffix_image_formats(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for image file format conversion."""

        @command()
        @option("images", default=None, nargs=3)
        @add_suffix(".png")
        def cmd(images: Any) -> None:
            assert images is not None
            assert images[0] == "photo1.png"
            assert images[1] == "photo2.png"
            assert images[2] == "photo3.png"

        result = cli_runner.invoke(
            cmd, ["--images", "photo1", "photo2", "photo3"]
        )
        assert result.exit_code == 0

    def test_add_suffix_log_rotation(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for log file rotation naming."""

        @command()
        @option("logs", default=None, nargs=2)
        @add_suffix(".1")
        def cmd(logs: Any) -> None:
            assert logs is not None
            assert logs[0] == "app.log.1"
            assert logs[1] == "error.log.1"

        result = cli_runner.invoke(cmd, ["--logs", "app.log", "error.log"])
        assert result.exit_code == 0

    def test_add_suffix_build_artifacts(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for build artifact naming."""

        @command()
        @option("artifacts", multiple=True, nargs=2)
        @add_suffix("_amd64.deb")
        def cmd(artifacts: Any) -> None:
            assert artifacts is not None
            # First build
            assert artifacts[0][0] == "myapp_1.0.0_amd64.deb"
            assert artifacts[0][1] == "myapp-dev_1.0.0_amd64.deb"
            # Second build
            assert artifacts[1][0] == "myapp_2.0.0_amd64.deb"
            assert artifacts[1][1] == "myapp-dev_2.0.0_amd64.deb"

        result = cli_runner.invoke(
            cmd,
            [
                "--artifacts",
                "myapp_1.0.0",
                "myapp-dev_1.0.0",
                "--artifacts",
                "myapp_2.0.0",
                "myapp-dev_2.0.0",
            ],
        )
        assert result.exit_code == 0

    def test_add_suffix_temporary_files(self, cli_runner: CliRunner) -> None:
        """Test add_suffix for temporary file naming."""

        @command()
        @option("files", default=None, nargs=3)
        @add_suffix(".tmp")
        def cmd(files: Any) -> None:
            assert files is not None
            assert files[0] == "processing.tmp"
            assert files[1] == "cache.tmp"
            assert files[2] == "download.tmp"

        result = cli_runner.invoke(
            cmd, ["--files", "processing", "cache", "download"]
        )
        assert result.exit_code == 0
