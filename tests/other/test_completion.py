"""Tests for shell completion registration."""

import os
from pathlib import Path
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from click_extended import command, group, register_completion
from click_extended.completion import _comp_path, _detect_shell

# ---------------------------------------------------------------------------
# _detect_shell
# ---------------------------------------------------------------------------


class TestDetectShell:
    """Tests for _detect_shell()."""

    def test_detects_bash(self) -> None:
        with patch.dict(os.environ, {"SHELL": "/bin/bash"}, clear=False):
            os.environ.pop("FISH_VERSION", None)
            assert _detect_shell() == "bash"

    def test_detects_zsh(self) -> None:
        with patch.dict(os.environ, {"SHELL": "/usr/bin/zsh"}, clear=False):
            os.environ.pop("FISH_VERSION", None)
            assert _detect_shell() == "zsh"

    def test_detects_fish_via_fish_version(self) -> None:
        with patch.dict(
            os.environ, {"FISH_VERSION": "3.7.0", "SHELL": "/bin/bash"}, clear=False
        ):
            assert _detect_shell() == "fish"

    def test_detects_fish_via_shell(self) -> None:
        with patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}, clear=False):
            os.environ.pop("FISH_VERSION", None)
            assert _detect_shell() == "fish"

    def test_returns_none_for_unknown_shell(self) -> None:
        with patch.dict(os.environ, {"SHELL": "/bin/csh"}, clear=False):
            os.environ.pop("FISH_VERSION", None)
            assert _detect_shell() is None

    def test_returns_none_when_shell_unset(self) -> None:
        env = os.environ.copy()
        env.pop("SHELL", None)
        env.pop("FISH_VERSION", None)
        with patch.dict(os.environ, env, clear=True):
            assert _detect_shell() is None


# ---------------------------------------------------------------------------
# --show-completion
# ---------------------------------------------------------------------------


class TestShowCompletion:
    """Tests for the --show-completion flag."""

    @pytest.fixture
    def cli(self) -> click.Command:
        @command()
        def hello() -> None:
            pass

        register_completion(hello)
        return hello

    def test_prints_bash_script(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--show-completion"], env={"SHELL": "/bin/bash"})
        assert result.exit_code == 0
        assert "COMP_WORDS" in result.output
        assert "complete" in result.output

    def test_prints_zsh_script(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--show-completion"], env={"SHELL": "/usr/bin/zsh"}
        )
        assert result.exit_code == 0
        assert "compdef" in result.output or "compadd" in result.output

    def test_prints_fish_script(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--show-completion"], env={"SHELL": "/usr/bin/fish"}
        )
        assert result.exit_code == 0
        assert "complete" in result.output

    def test_errors_when_shell_unknown(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--show-completion"], env={"SHELL": "/bin/csh"})
        assert result.exit_code != 0
        assert "Supported shells:" in result.output


# ---------------------------------------------------------------------------
# --install-completion
# ---------------------------------------------------------------------------


class TestInstallCompletion:
    """Tests for the --install-completion flag."""

    @pytest.fixture
    def cli(self) -> click.Command:
        @command()
        def mycli() -> None:
            pass

        register_completion(mycli)
        return mycli

    def test_installs_fish_completion(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            result = runner.invoke(
                cli, ["--install-completion"], env={"SHELL": "/usr/bin/fish"}
            )

        assert result.exit_code == 0
        assert "Installed Fish completion" in result.output

        comp_file = tmp_path / ".config" / "fish" / "completions" / "mycli.fish"
        assert comp_file.exists()
        assert "complete" in comp_file.read_text()

    def test_installs_bash_completion(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        bashrc = tmp_path / ".bashrc"
        bashrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            result = runner.invoke(
                cli, ["--install-completion"], env={"SHELL": "/bin/bash"}
            )

        assert result.exit_code == 0
        assert "Installed Bash completion" in result.output

        comp_file = tmp_path / ".bash_completions" / "mycli.bash"
        assert comp_file.exists()

        rc_text = bashrc.read_text()
        assert "click-extended:mycli:completion" in rc_text
        assert "source" in rc_text

    def test_installs_zsh_completion(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        zshrc = tmp_path / ".zshrc"
        zshrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            result = runner.invoke(
                cli, ["--install-completion"], env={"SHELL": "/usr/bin/zsh"}
            )

        assert result.exit_code == 0
        assert "Installed Zsh completion" in result.output

        comp_file = tmp_path / ".zsh" / "completions" / "_mycli"
        assert comp_file.exists()

        rc_text = zshrc.read_text()
        assert "fpath=" in rc_text
        assert "compinit" in rc_text
        assert "click-extended:mycli:completion" in rc_text

    def test_bash_idempotent(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        bashrc = tmp_path / ".bashrc"
        bashrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            runner.invoke(cli, ["--install-completion"], env={"SHELL": "/bin/bash"})
            result = runner.invoke(
                cli, ["--install-completion"], env={"SHELL": "/bin/bash"}
            )

        assert "already installed" in result.output
        rc_text = bashrc.read_text()
        assert rc_text.count("click-extended:mycli:completion") == 1

    def test_fish_idempotent(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            runner.invoke(cli, ["--install-completion"], env={"SHELL": "/usr/bin/fish"})
            result = runner.invoke(
                cli, ["--install-completion"], env={"SHELL": "/usr/bin/fish"}
            )

        assert "already installed" in result.output

    def test_errors_when_shell_unknown(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--install-completion"], env={"SHELL": "/bin/csh"})
        assert result.exit_code != 0
        assert "Supported shells:" in result.output


# ---------------------------------------------------------------------------
# register_completion with groups
# ---------------------------------------------------------------------------


class TestRegisterCompletionGroup:
    """Tests that register_completion works with groups too."""

    def test_group_has_flags(self) -> None:
        @group()
        def cli() -> None:
            pass

        register_completion(cli)

        param_names = [p.name for p in cli.params]
        assert "show_completion" in param_names
        assert "install_completion" in param_names
        assert "completion_path" in param_names
        assert "uninstall_completion" in param_names

    def test_group_show_completion(self) -> None:
        @group()
        def cli() -> None:
            pass

        register_completion(cli)

        runner = CliRunner()
        result = runner.invoke(cli, ["--show-completion"], env={"SHELL": "/bin/bash"})
        assert result.exit_code == 0
        assert "COMP_WORDS" in result.output

    def test_group_has_all_flags(self) -> None:
        @group()
        def cli() -> None:
            pass

        register_completion(cli)

        param_names = [p.name for p in cli.params]
        assert "show_completion" in param_names
        assert "install_completion" in param_names
        assert "completion_path" in param_names
        assert "uninstall_completion" in param_names


# ---------------------------------------------------------------------------
# --completion-path
# ---------------------------------------------------------------------------


class TestCompletionPath:
    """Tests for the --completion-path flag."""

    @pytest.fixture
    def cli(self) -> click.Command:
        @command()
        def mycli() -> None:
            pass

        register_completion(mycli)
        return mycli

    def test_prints_bash_path(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--completion-path"], env={"SHELL": "/bin/bash"})
        assert result.exit_code == 0
        assert ".bash_completions/mycli.bash" in result.output

    def test_prints_zsh_path(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--completion-path"], env={"SHELL": "/usr/bin/zsh"}
        )
        assert result.exit_code == 0
        assert ".zsh/completions/_mycli" in result.output

    def test_prints_fish_path(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--completion-path"], env={"SHELL": "/usr/bin/fish"}
        )
        assert result.exit_code == 0
        assert "fish/completions/mycli.fish" in result.output

    def test_errors_when_shell_unknown(self, cli: click.Command) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--completion-path"], env={"SHELL": "/bin/csh"})
        assert result.exit_code != 0

    def test_comp_path_helper_bash(self) -> None:
        path = _comp_path("bash", "mycli")
        assert path.name == "mycli.bash"

    def test_comp_path_helper_zsh(self) -> None:
        path = _comp_path("zsh", "mycli")
        assert path.name == "_mycli"

    def test_comp_path_helper_fish(self) -> None:
        path = _comp_path("fish", "mycli")
        assert path.name == "mycli.fish"


# ---------------------------------------------------------------------------
# --uninstall-completion
# ---------------------------------------------------------------------------


class TestUninstallCompletion:
    """Tests for the --uninstall-completion flag."""

    @pytest.fixture
    def cli(self) -> click.Command:
        @command()
        def mycli() -> None:
            pass

        register_completion(mycli)
        return mycli

    def test_uninstalls_fish(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            runner.invoke(cli, ["--install-completion"], env={"SHELL": "/usr/bin/fish"})
            comp_file = tmp_path / ".config" / "fish" / "completions" / "mycli.fish"
            assert comp_file.exists()

            result = runner.invoke(
                cli, ["--uninstall-completion"], env={"SHELL": "/usr/bin/fish"}
            )

        assert result.exit_code == 0
        assert "Uninstalled Fish completion" in result.output
        assert not comp_file.exists()

    def test_uninstalls_bash(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        bashrc = tmp_path / ".bashrc"
        bashrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            runner.invoke(cli, ["--install-completion"], env={"SHELL": "/bin/bash"})
            assert "click-extended:mycli:completion" in bashrc.read_text()

            result = runner.invoke(
                cli, ["--uninstall-completion"], env={"SHELL": "/bin/bash"}
            )

        assert result.exit_code == 0
        assert "Uninstalled Bash completion" in result.output
        assert "click-extended:mycli:completion" not in bashrc.read_text()
        comp_file = tmp_path / ".bash_completions" / "mycli.bash"
        assert not comp_file.exists()

    def test_uninstalls_zsh(self, cli: click.Command, tmp_path: Path) -> None:
        runner = CliRunner()
        zshrc = tmp_path / ".zshrc"
        zshrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            runner.invoke(cli, ["--install-completion"], env={"SHELL": "/usr/bin/zsh"})
            assert "click-extended:mycli:completion" in zshrc.read_text()

            result = runner.invoke(
                cli, ["--uninstall-completion"], env={"SHELL": "/usr/bin/zsh"}
            )

        assert result.exit_code == 0
        assert "Uninstalled Zsh completion" in result.output
        assert "click-extended:mycli:completion" not in zshrc.read_text()
        comp_file = tmp_path / ".zsh" / "completions" / "_mycli"
        assert not comp_file.exists()

    def test_uninstall_nonexistent_is_silent(
        self, cli: click.Command, tmp_path: Path
    ) -> None:
        """Uninstalling when nothing is installed should not raise."""
        runner = CliRunner()
        bashrc = tmp_path / ".bashrc"
        bashrc.touch()

        with patch("click_extended.completion.Path.home", return_value=tmp_path):
            result = runner.invoke(
                cli, ["--uninstall-completion"], env={"SHELL": "/bin/bash"}
            )

        assert result.exit_code == 0
