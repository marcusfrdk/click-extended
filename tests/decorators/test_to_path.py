"""Tests for to_path decorator."""

import os
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.to_path import to_path


class TestToPathBasic:
    """Test basic to_path functionality."""

    def test_to_path_existing_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path()
        def cmd(path: Path | None) -> None:
            click.echo(f"Path: {path}")
            click.echo(f"Type: {type(path).__name__}")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Path:" in result.output
        assert (
            "Type: PosixPath" in result.output
            or "Type: WindowsPath" in result.output
        )

    def test_to_path_existing_directory(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with existing directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        @command()
        @option("path", default=None)
        @to_path()
        def cmd(path: Path | None) -> None:
            assert path is not None
            click.echo(f"Is directory: {path.is_dir()}")

        result = cli_runner.invoke(cmd, ["--path", str(test_dir)])
        assert result.exit_code == 0
        assert "Is directory: True" in result.output

    def test_to_path_nonexistent_file_with_exists_false(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows nonexistent path when exists=False."""
        nonexistent = tmp_path / "does_not_exist.txt"

        @command()
        @option("path", default=None)
        @to_path(exists=False)
        def cmd(path: Path | None) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", str(nonexistent)])
        assert result.exit_code == 0
        assert "Path:" in result.output

    def test_to_path_nonexistent_file_with_exists_true(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path fails with nonexistent path when exists=True."""
        nonexistent = tmp_path / "does_not_exist.txt"

        @command()
        @option("path", default=None)
        @to_path(exists=True)
        def cmd(path: Path | None) -> None:
            click.echo(f"Path: {path}")

        result = cli_runner.invoke(cmd, ["--path", str(nonexistent)])
        assert result.exit_code != 0
        assert "does not exist" in result.output


class TestToPathParents:
    """Test to_path parents functionality."""

    def test_to_path_creates_parents(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path creates parent directories."""
        nested_path = tmp_path / "level1" / "level2" / "file.txt"

        @command()
        @option("path", default=None)
        @to_path(exists=False, parents=True)
        def cmd(path: Path | None) -> None:
            assert path is not None
            click.echo(f"Parent exists: {path.parent.exists()}")

        result = cli_runner.invoke(cmd, ["--path", str(nested_path)])
        assert result.exit_code == 0
        assert "Parent exists: True" in result.output
        assert nested_path.parent.exists()

    def test_to_path_no_parents_creation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path doesn't create parents by default."""
        nested_path = tmp_path / "level1" / "level2" / "file.txt"

        @command()
        @option("path", default=None)
        @to_path(exists=False, parents=False)
        def cmd(path: Path | None) -> None:
            assert path is not None
            click.echo(f"Parent exists: {path.parent.exists()}")

        result = cli_runner.invoke(cmd, ["--path", str(nested_path)])
        assert result.exit_code == 0
        assert "Parent exists: False" in result.output


class TestToPathExtensions:
    """Test to_path extension validation."""

    def test_to_path_valid_extension_with_dot(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path accepts valid extension with dot."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(extensions=[".txt"])
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_valid_extension_without_dot(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path accepts valid extension without dot (normalized)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# code")

        @command()
        @option("path", default=None)
        @to_path(extensions=["py"])
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_invalid_extension(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects invalid extension."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# markdown")

        @command()
        @option("path", default=None)
        @to_path(extensions=[".txt", ".py"])
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code != 0
        assert "does not have an allowed extension" in result.output

    def test_to_path_multiple_extensions(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with multiple allowed extensions."""
        test_file = tmp_path / "script.py"
        test_file.write_text("print('hello')")

        @command()
        @option("path", default=None)
        @to_path(extensions=[".py", ".js", ".ts"])
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output


class TestToPathFileDirectory:
    """Test to_path file/directory restrictions."""

    def test_to_path_only_files(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows only files."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(allow_file=True, allow_directory=False)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_only_files_rejects_directory(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects directory when only files allowed."""
        test_dir = tmp_path / "dir"
        test_dir.mkdir()

        @command()
        @option("path", default=None)
        @to_path(allow_file=True, allow_directory=False)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_dir)])
        assert result.exit_code != 0
        assert "is a directory" in result.output

    def test_to_path_only_directories(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows only directories."""
        test_dir = tmp_path / "dir"
        test_dir.mkdir()

        @command()
        @option("path", default=None)
        @to_path(allow_file=False, allow_directory=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_dir)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_only_directories_rejects_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects file when only directories allowed."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(allow_file=False, allow_directory=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code != 0
        assert "is a file" in result.output


class TestToPathEmpty:
    """Test to_path empty file/directory checks."""

    def test_to_path_empty_file_allowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows empty file when configured."""
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()

        @command()
        @option("path", default=None)
        @to_path(allow_empty_file=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(empty_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_empty_file_disallowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects empty file when configured."""
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()

        @command()
        @option("path", default=None)
        @to_path(allow_empty_file=False)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(empty_file)])
        assert result.exit_code != 0
        assert "is empty" in result.output

    def test_to_path_empty_directory_allowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows empty directory when configured."""
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()

        @command()
        @option("path", default=None)
        @to_path(allow_empty_directory=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(empty_dir)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_empty_directory_disallowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects empty directory when configured."""
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()

        @command()
        @option("path", default=None)
        @to_path(allow_empty_directory=False)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(empty_dir)])
        assert result.exit_code != 0
        assert "is empty" in result.output


class TestToPathPermissions:
    """Test to_path permission checks."""

    def test_to_path_readable(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path checks readable permission."""
        test_file = tmp_path / "readable.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(is_readable=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_writable(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path checks writable permission."""
        test_file = tmp_path / "writable.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(is_writable=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    @pytest.mark.skipif(os.name == "nt", reason="Unix-only test")
    def test_to_path_executable(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path checks executable permission."""
        test_file = tmp_path / "script.sh"
        test_file.write_text("#!/bin/bash\necho hello")
        test_file.chmod(0o755)

        @command()
        @option("path", default=None)
        @to_path(is_executable=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output


class TestToPathPatterns:
    """Test to_path pattern matching."""

    def test_to_path_include_pattern_match(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with matching include pattern."""
        test_file = tmp_path / "config_main.yaml"
        test_file.write_text("key: value")

        @command()
        @option("path", default=None)
        @to_path(include_pattern="config_*")
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_include_pattern_no_match(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with non-matching include pattern."""
        test_file = tmp_path / "data.yaml"
        test_file.write_text("key: value")

        @command()
        @option("path", default=None)
        @to_path(include_pattern="config_*")
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code != 0
        assert "does not match include pattern" in result.output

    def test_to_path_exclude_pattern_no_match(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with non-matching exclude pattern."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(exclude_pattern="*.tmp")
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_to_path_exclude_pattern_match(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path with matching exclude pattern."""
        test_file = tmp_path / "temp.tmp"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(exclude_pattern="*.tmp")
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code != 0
        assert "matches exclude pattern" in result.output


class TestToPathSymlinks:
    """Test to_path symlink handling."""

    @pytest.mark.skipif(
        os.name == "nt", reason="Symlinks may require admin on Windows"
    )
    def test_to_path_symlink_allowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path allows symlinks when configured."""
        target = tmp_path / "target.txt"
        target.write_text("content")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(target)

        @command()
        @option("path", default=None)
        @to_path(allow_symlink=True)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(symlink)])
        assert result.exit_code == 0
        assert "Success" in result.output

    @pytest.mark.skipif(
        os.name == "nt", reason="Symlinks may require admin on Windows"
    )
    def test_to_path_symlink_disallowed(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path rejects symlinks when configured."""
        target = tmp_path / "target.txt"
        target.write_text("content")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(target)

        @command()
        @option("path", default=None)
        @to_path(allow_symlink=False)
        def cmd(path: Path | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--path", str(symlink)])
        assert result.exit_code != 0
        assert "is a symlink" in result.output


class TestToPathResolve:
    """Test to_path resolve functionality."""

    def test_to_path_resolve_true(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path resolves path with resolve=True."""
        test_file = tmp_path / "file.txt"
        test_file.write_text("content")

        @command()
        @option("path", default=None)
        @to_path(resolve=True)
        def cmd(path: Path | None) -> None:
            assert path is not None
            click.echo(f"Is absolute: {path.is_absolute()}")

        result = cli_runner.invoke(cmd, ["--path", str(test_file)])
        assert result.exit_code == 0
        assert "Is absolute: True" in result.output

    def test_to_path_expanduser(self, cli_runner: CliRunner) -> None:
        """Test to_path expands ~ in paths."""

        @command()
        @option("path", default=None)
        @to_path(exists=False)
        def cmd(path: Path | None) -> None:
            # Should not contain ~ after expansion
            click.echo(f"Has tilde: {'~' in str(path)}")

        result = cli_runner.invoke(cmd, ["--path", "~/test.txt"])
        assert result.exit_code == 0
        assert "Has tilde: False" in result.output


class TestToPathPractical:
    """Test practical use cases for to_path."""

    def test_to_path_output_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path for output file creation."""
        output_file = tmp_path / "output" / "result.txt"

        @command()
        @option("output", default=None)
        @to_path(exists=False, parents=True)
        def cmd(output: Path | None) -> None:
            assert output is not None
            output.write_text("Generated content")
            click.echo("File created")

        result = cli_runner.invoke(cmd, ["--output", str(output_file)])
        assert result.exit_code == 0
        assert "File created" in result.output
        assert output_file.exists()
        assert output_file.read_text() == "Generated content"

    def test_to_path_config_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path for config file validation."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("key: value")

        @command()
        @option("config", default=None)
        @to_path(extensions=[".yaml", ".yml"], allow_directory=False)
        def cmd(config: Path | None) -> None:
            assert config is not None
            click.echo(f"Config: {config.read_text()}")

        result = cli_runner.invoke(cmd, ["--config", str(config_file)])
        assert result.exit_code == 0
        assert "Config: key: value" in result.output

    def test_to_path_log_directory(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test to_path for log directory validation."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        @command()
        @option("log_dir", default=None)
        @to_path(allow_file=False, allow_directory=True, is_writable=True)
        def cmd(log_dir: Path | None) -> None:
            assert log_dir is not None
            log_file = log_dir / "app.log"
            log_file.write_text("Log entry")
            click.echo("Log written")

        result = cli_runner.invoke(cmd, ["--log-dir", str(log_dir)])
        assert result.exit_code == 0
        assert "Log written" in result.output
