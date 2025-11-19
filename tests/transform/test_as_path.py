"""Test the `as_path` transformer decorator."""

import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from click_extended.core._child_node import ChildNode, ProcessContext
from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.transform.as_path import AsPath, as_path


def make_context(parent_name: str = "test") -> ProcessContext:
    """Helper to create a ProcessContext for testing."""
    from unittest.mock import MagicMock

    parent = MagicMock()
    parent.name = parent_name
    return ProcessContext(
        parent=parent,
        siblings=[],
        tags={},
        args=(),
        kwargs={},
    )


class TestAsPathBasic:
    """Test basic AsPath functionality."""

    def test_transformer_is_child_node(self) -> None:
        """Test that AsPath is a ChildNode subclass."""
        transformer = AsPath(name="test_transformer")
        assert isinstance(transformer, ChildNode)

    def test_string_to_path_conversion(self) -> None:
        """Test converting string to Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": False,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert isinstance(result, Path)
            assert result.is_absolute()

    def test_path_object_passthrough(self) -> None:
        """Test that Path objects are accepted and processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": False,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(test_file, context)
            assert isinstance(result, Path)
            assert result.is_absolute()

    def test_expanduser(self) -> None:
        """Test that ~ is expanded to home directory."""
        transformer = AsPath(name="test_transformer")
        context = make_context("config")
        context.kwargs = {
            "exists": False,
            "parents": False,
            "extensions": None,
            "include_pattern": None,
            "exclude_pattern": None,
            "allow_file": True,
            "allow_directory": True,
            "allow_empty_directory": True,
            "allow_empty_file": True,
            "allow_symlink": False,
            "follow_symlink": True,
            "is_readable": False,
            "is_writable": False,
            "is_executable": False,
        }

        result = transformer.process("~/test.txt", context)
        assert isinstance(result, Path)
        assert "~" not in str(result)
        assert result.is_absolute()


class TestAsPathExistence:
    """Test path existence validation."""

    def test_exists_true_with_existing_file(self) -> None:
        """Test that exists=True passes for existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.exists()

    def test_exists_true_with_nonexistent_file(self) -> None:
        """Test that exists=True fails for non-existent files."""
        transformer = AsPath(name="test_transformer")
        context = make_context("config")
        context.kwargs = {
            "exists": True,
            "parents": False,
            "extensions": None,
            "include_pattern": None,
            "exclude_pattern": None,
            "allow_file": True,
            "allow_directory": True,
            "allow_empty_directory": True,
            "allow_empty_file": True,
            "allow_symlink": False,
            "follow_symlink": True,
            "is_readable": False,
            "is_writable": False,
            "is_executable": False,
        }

        with pytest.raises(ValueError) as exc_info:
            transformer.process("/nonexistent/file.txt", context)
        assert "does not exist" in str(exc_info.value)
        assert "config" in str(exc_info.value)

    def test_exists_false_with_nonexistent_file(self) -> None:
        """Test that exists=False allows non-existent files."""
        transformer = AsPath(name="test_transformer")
        context = make_context("config")
        context.kwargs = {
            "exists": False,
            "parents": False,
            "extensions": None,
            "include_pattern": None,
            "exclude_pattern": None,
            "allow_file": True,
            "allow_directory": True,
            "allow_empty_directory": True,
            "allow_empty_file": True,
            "allow_symlink": False,
            "follow_symlink": True,
            "is_readable": False,
            "is_writable": False,
            "is_executable": False,
        }

        result = transformer.process("/nonexistent/file.txt", context)
        assert isinstance(result, Path)


class TestAsPathParents:
    """Test parent directory validation."""

    def test_parents_true_with_existing_parent(self) -> None:
        """Test that parents=True passes when parent exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": False,
                "parents": True,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.parent.exists()

    def test_parents_true_with_nonexistent_parent(self) -> None:
        """Test that parents=True fails when parent doesn't exist."""
        transformer = AsPath(name="test_transformer")
        context = make_context("config")
        context.kwargs = {
            "exists": False,
            "parents": True,
            "extensions": None,
            "include_pattern": None,
            "exclude_pattern": None,
            "allow_file": True,
            "allow_directory": True,
            "allow_empty_directory": True,
            "allow_empty_file": True,
            "allow_symlink": False,
            "follow_symlink": True,
            "is_readable": False,
            "is_writable": False,
            "is_executable": False,
        }

        with pytest.raises(ValueError) as exc_info:
            transformer.process("/nonexistent/dir/file.txt", context)
        assert "Parent directory" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)


class TestAsPathFileDirectory:
    """Test file vs directory validation."""

    def test_allow_file_true_with_file(self) -> None:
        """Test that files are allowed when allow_file=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.is_file()

    def test_allow_file_false_with_file(self) -> None:
        """Test that files are rejected when allow_file=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": False,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(test_file), context)
            assert "is a file" in str(exc_info.value)
            assert "files are not allowed" in str(exc_info.value)

    def test_allow_directory_true_with_directory(self) -> None:
        """Test that directories are allowed when allow_directory=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": False,
                "allow_directory": True,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(tmpdir, context)
            assert result.is_dir()

    def test_allow_directory_false_with_directory(self) -> None:
        """Test that directories are rejected when allow_directory=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(tmpdir, context)
            assert "is a directory" in str(exc_info.value)
            assert "directories are not allowed" in str(exc_info.value)


class TestAsPathEmpty:
    """Test empty file/directory validation."""

    def test_allow_empty_file_false_with_empty_file(self) -> None:
        """Test that empty files are rejected when allow_empty_file=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "empty.txt"
            test_file.touch()

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": False,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(test_file), context)
            assert "empty" in str(exc_info.value).lower()
            assert "file" in str(exc_info.value).lower()

    def test_allow_empty_directory_false_with_empty_dir(self) -> None:
        """Test that empty dirs are rejected when allow_empty_directory=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_dir = Path(tmpdir) / "empty_dir"
            empty_dir.mkdir()

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": False,
                "allow_directory": True,
                "allow_empty_directory": False,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(empty_dir), context)
            assert "empty" in str(exc_info.value).lower()
            assert "director" in str(exc_info.value).lower()


class TestAsPathExtensions:
    """Test file extension validation."""

    def test_extensions_matching(self) -> None:
        """Test that matching extensions pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text("{}")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": [".json", ".yaml"],
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.suffix == ".json"

    def test_extensions_not_matching(self) -> None:
        """Test that non-matching extensions fail validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": [".json", ".yaml"],
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(test_file), context)
            assert "extension" in str(exc_info.value).lower()
            assert ".json" in str(exc_info.value)
            assert ".yaml" in str(exc_info.value)


class TestAsPathPatterns:
    """Test include/exclude pattern validation."""

    def test_include_pattern_matching(self) -> None:
        """Test that matching include patterns pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.toml"
            test_file.write_text("")

            transformer = AsPath(name="test_transformer")
            context = make_context("path")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": "*.toml",
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.name == "config.toml"

    def test_include_pattern_not_matching(self) -> None:
        """Test that non-matching include patterns fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.txt"
            test_file.write_text("")

            transformer = AsPath(name="test_transformer")
            context = make_context("path")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": "*.toml",
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(test_file), context)
            assert "does not match include pattern" in str(exc_info.value)
            assert "*.toml" in str(exc_info.value)

    def test_exclude_pattern_matching(self) -> None:
        """Test that matching exclude patterns fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_file.txt"
            test_file.write_text("")

            transformer = AsPath(name="test_transformer")
            context = make_context("path")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": "test_*",
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            with pytest.raises(ValueError) as exc_info:
                transformer.process(str(test_file), context)
            assert "matches exclude pattern" in str(exc_info.value)
            assert "test_*" in str(exc_info.value)

    def test_exclude_pattern_not_matching(self) -> None:
        """Test that non-matching exclude patterns pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.txt"
            test_file.write_text("")

            transformer = AsPath(name="test_transformer")
            context = make_context("path")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": "test_*",
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.name == "config.txt"

    def test_include_takes_precedence_over_exclude(self) -> None:
        """Test that include pattern overrides exclude pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.toml"
            test_file.write_text("")

            transformer = AsPath(name="test_transformer")
            context = make_context("path")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": "*.toml",
                "exclude_pattern": "*",
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

            # Should pass because include takes precedence
            result = transformer.process(str(test_file), context)
            assert result.name == "config.toml"


class TestAsPathPermissions:
    """Test permission validation."""

    def test_readable_permission(self) -> None:
        """Test readable permission check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": True,
                "is_writable": False,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.exists()
            assert os.access(result, os.R_OK)

    def test_writable_permission(self) -> None:
        """Test writable permission check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            transformer = AsPath(name="test_transformer")
            context = make_context("config")
            context.kwargs = {
                "exists": True,
                "parents": False,
                "extensions": None,
                "include_pattern": None,
                "exclude_pattern": None,
                "allow_file": True,
                "allow_directory": False,
                "allow_empty_directory": True,
                "allow_empty_file": True,
                "allow_symlink": False,
                "follow_symlink": True,
                "is_readable": False,
                "is_writable": True,
                "is_executable": False,
            }

            result = transformer.process(str(test_file), context)
            assert result.exists()
            assert os.access(result, os.W_OK)


class TestAsPathDecorator:
    """Test as_path decorator in CLI context."""

    def test_decorator_with_existing_file(self) -> None:
        """Test decorator with existing file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True)
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config}")
                print(f"Is Path: {isinstance(config, Path)}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", str(test_file)])  # type: ignore

            assert result.exit_code == 0
            assert "Is Path: True" in result.output
            assert test_file.name in result.output

    def test_decorator_with_nonexistent_file(self) -> None:
        """Test decorator rejects non-existent file when exists=True."""

        @command()
        @option("--config", "-c", type=str)
        @as_path(exists=True)
        def test_cmd(config: Path) -> None:
            """Test command."""
            print(f"Config: {config}")

        runner = CliRunner()
        result = runner.invoke(test_cmd, ["--config", "/nonexistent/file.txt"])  # type: ignore

        assert result.exit_code != 0
        assert result.exception is not None
        assert isinstance(result.exception, ValueError)
        assert "does not exist" in str(result.exception)

    def test_decorator_with_extension_filter(self) -> None:
        """Test decorator with extension filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.json"
            test_file.write_text("{}")

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True, extensions=[".json", ".yaml"])
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config.name}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", str(test_file)])  # type: ignore

            assert result.exit_code == 0
            assert "config.json" in result.output

    def test_decorator_with_wrong_extension(self) -> None:
        """Test decorator rejects wrong extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.txt"
            test_file.write_text("test")

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True, extensions=[".json", ".yaml"])
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config.name}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", str(test_file)])  # type: ignore

            assert result.exit_code != 0
            assert result.exception is not None
            assert "extension" in str(result.exception).lower()

    def test_decorator_with_include_pattern(self) -> None:
        """Test decorator with include pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.toml"
            test_file.write_text("")

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True, include_pattern="*.toml")
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config.name}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", str(test_file)])  # type: ignore

            assert result.exit_code == 0
            assert "config.toml" in result.output

    def test_decorator_with_exclude_pattern(self) -> None:
        """Test decorator with exclude pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_config.toml"
            test_file.write_text("")

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True, exclude_pattern="test_*")
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config.name}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", str(test_file)])  # type: ignore

            assert result.exit_code != 0
            assert result.exception is not None
            assert "exclude pattern" in str(result.exception)

    def test_decorator_only_files(self) -> None:
        """Test decorator that only allows files."""
        with tempfile.TemporaryDirectory() as tmpdir:

            @command()
            @option("--config", "-c", type=str)
            @as_path(exists=True, allow_file=True, allow_directory=False)
            def test_cmd(config: Path) -> None:
                """Test command."""
                print(f"Config: {config}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--config", tmpdir])  # type: ignore

            assert result.exit_code != 0
            assert result.exception is not None
            assert "director" in str(result.exception).lower()

    def test_decorator_only_directories(self) -> None:
        """Test decorator that only allows directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            @command()
            @option("--dir", "-d", type=str)
            @as_path(exists=True, allow_file=False, allow_directory=True)
            def test_cmd(dir: Path) -> None:
                """Test command."""
                print(f"Dir: {dir}")

            runner = CliRunner()
            result = runner.invoke(test_cmd, ["--dir", str(test_file)])  # type: ignore

            assert result.exit_code != 0
            assert result.exception is not None
            assert "file" in str(result.exception).lower()

    def test_decorator_returns_callable(self) -> None:
        """Test that as_path decorator returns a callable."""
        decorator = as_path()
        assert callable(decorator)
