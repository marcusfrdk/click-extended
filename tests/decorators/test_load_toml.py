"""Tests for load_toml decorator."""

from pathlib import Path
from typing import Any

import click
import pytest
from click.testing import CliRunner

from click_extended.core.decorators.command import command
from click_extended.core.decorators.option import option
from click_extended.decorators.load_toml import load_toml
from click_extended.decorators.to_path import to_path


class TestLoadTomlBasic:
    """Test basic load_toml functionality."""

    def test_load_toml_simple_config(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with simple TOML config."""
        toml_file = tmp_path / "config.toml"
        toml_file.write_text('[server]\nhost = "localhost"\nport = 8080\n')

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"Host: {config['server']['host']}")
            click.echo(f"Port: {config['server']['port']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Host: localhost" in result.output
        assert "Port: 8080" in result.output

    def test_load_toml_nested_structure(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with nested TOML structure."""
        toml_file = tmp_path / "app.toml"
        content = """
[database]
host = "db.example.com"
port = 5432

[database.credentials]
user = "admin"
password = "secret"
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"DB Host: {config['database']['host']}")
            click.echo(f"DB User: {config['database']['credentials']['user']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "DB Host: db.example.com" in result.output
        assert "DB User: admin" in result.output

    def test_load_toml_arrays(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with arrays."""
        toml_file = tmp_path / "config.toml"
        content = """
name = "MyApp"
versions = [1, 2, 3]
features = ["auth", "api", "dashboard"]
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"Name: {config['name']}")
            click.echo(f"Versions: {len(config['versions'])}")
            click.echo(f"Features: {', '.join(config['features'])}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Name: MyApp" in result.output
        assert "Versions: 3" in result.output
        assert "Features: auth, api, dashboard" in result.output

    def test_load_toml_tables(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with table arrays."""
        toml_file = tmp_path / "config.toml"
        content = """
[[servers]]
name = "alpha"
ip = "10.0.0.1"

[[servers]]
name = "beta"
ip = "10.0.0.2"
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            assert len(config["servers"]) == 2
            for server in config["servers"]:
                click.echo(f"{server['name']}: {server['ip']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "alpha: 10.0.0.1" in result.output
        assert "beta: 10.0.0.2" in result.output


class TestLoadTomlTypes:
    """Test load_toml with different data types."""

    def test_load_toml_strings(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with string types."""
        toml_file = tmp_path / "strings.toml"
        content = '''
basic = "Hello"
multiline = """
Line 1
Line 2
"""
literal = 'C:\\Users\\Path'
'''
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            assert config["basic"] == "Hello"
            assert "Line 1" in config["multiline"]
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Success" in result.output

    def test_load_toml_numbers(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with numeric types."""
        toml_file = tmp_path / "numbers.toml"
        content = """
integer = 42
float = 3.14
negative = -17
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"Int: {config['integer']}")
            click.echo(f"Float: {config['float']}")
            click.echo(f"Negative: {config['negative']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Int: 42" in result.output
        assert "Float: 3.14" in result.output
        assert "Negative: -17" in result.output

    def test_load_toml_booleans(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with boolean types."""
        toml_file = tmp_path / "bools.toml"
        content = """
enabled = true
disabled = false
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            assert config["enabled"] is True
            assert config["disabled"] is False
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Success" in result.output


class TestLoadTomlErrors:
    """Test load_toml error handling."""

    def test_load_toml_invalid_toml(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with invalid TOML."""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("[invalid\nno closing bracket")

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            click.echo("Should not reach here")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code != 0

    def test_load_toml_directory_path(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml rejects directory path."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            click.echo("Should not reach here")

        result = cli_runner.invoke(cmd, ["--config", str(config_dir)])
        assert result.exit_code != 0
        assert "is a directory" in result.output

    def test_load_toml_nonexistent_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with nonexistent file."""
        toml_file = tmp_path / "nonexistent.toml"

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            click.echo("Should not reach here")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code != 0
        assert "does not exist" in result.output


class TestLoadTomlFlatTuple:
    """Test load_toml with flat tuples."""

    def test_load_toml_flat_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with flat tuple of TOML files."""
        file1 = tmp_path / "service1.toml"
        file2 = tmp_path / "service2.toml"
        file3 = tmp_path / "service3.toml"
        file1.write_text('[service]\nname = "api"\nport = 8001\n')
        file2.write_text('[service]\nname = "web"\nport = 8002\n')
        file3.write_text('[service]\nname = "worker"\nport = 8003\n')

        @command()
        @option("configs", default=None, nargs=3)
        @to_path()
        @load_toml()
        def cmd(configs: Any) -> None:
            assert configs is not None
            assert isinstance(configs, tuple)
            assert len(configs) == 3
            for cfg in configs:
                click.echo(
                    f"{cfg['service']['name']}: {cfg['service']['port']}"
                )

        result = cli_runner.invoke(
            cmd, ["--configs", str(file1), str(file2), str(file3)]
        )
        assert result.exit_code == 0
        assert "api: 8001" in result.output
        assert "web: 8002" in result.output
        assert "worker: 8003" in result.output

    def test_load_toml_flat_tuple_aggregation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml flat tuple with data aggregation."""
        file1 = tmp_path / "metrics1.toml"
        file2 = tmp_path / "metrics2.toml"
        file1.write_text("[metrics]\nrequests = 100\nerrors = 5\n")
        file2.write_text("[metrics]\nrequests = 150\nerrors = 3\n")

        @command()
        @option("files", default=None, nargs=2)
        @to_path()
        @load_toml()
        def cmd(files: Any) -> None:
            assert files is not None
            total_requests = sum(f["metrics"]["requests"] for f in files)
            total_errors = sum(f["metrics"]["errors"] for f in files)
            click.echo(f"Total requests: {total_requests}")
            click.echo(f"Total errors: {total_errors}")

        result = cli_runner.invoke(cmd, ["--files", str(file1), str(file2)])
        assert result.exit_code == 0
        assert "Total requests: 250" in result.output
        assert "Total errors: 8" in result.output


class TestLoadTomlNestedTuple:
    """Test load_toml with nested tuples."""

    def test_load_toml_nested_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with nested tuple of TOML files."""
        env1_db = tmp_path / "dev_db.toml"
        env1_cache = tmp_path / "dev_cache.toml"
        env2_db = tmp_path / "prod_db.toml"
        env2_cache = tmp_path / "prod_cache.toml"
        env1_db.write_text('[database]\nhost = "localhost"\nport = 5432\n')
        env1_cache.write_text('[cache]\nhost = "localhost"\nport = 6379\n')
        env2_db.write_text('[database]\nhost = "db.prod.com"\nport = 5432\n')
        env2_cache.write_text('[cache]\nhost = "cache.prod.com"\nport = 6379\n')

        @command()
        @option("envs", multiple=True, nargs=2)
        @to_path()
        @load_toml()
        def cmd(envs: Any) -> None:
            assert envs is not None
            assert isinstance(envs, tuple)
            assert len(envs) == 2
            env_names = ["dev", "prod"]
            for i, env_group in enumerate(envs):
                db_host = env_group[0]["database"]["host"]
                cache_host = env_group[1]["cache"]["host"]
                click.echo(f"{env_names[i]}: db={db_host}, cache={cache_host}")

        result = cli_runner.invoke(
            cmd,
            [
                "--envs",
                str(env1_db),
                str(env1_cache),
                "--envs",
                str(env2_db),
                str(env2_cache),
            ],
        )
        assert result.exit_code == 0
        assert "dev: db=localhost, cache=localhost" in result.output
        assert "prod: db=db.prod.com, cache=cache.prod.com" in result.output

    def test_load_toml_nested_tuple_config_layers(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml nested tuple for layered configs."""
        base1 = tmp_path / "base1.toml"
        override1 = tmp_path / "override1.toml"
        base2 = tmp_path / "base2.toml"
        override2 = tmp_path / "override2.toml"
        base1.write_text("[app]\ntimeout = 30\nretries = 3\n")
        override1.write_text("[app]\ntimeout = 60\n")
        base2.write_text("[app]\ntimeout = 30\nretries = 3\n")
        override2.write_text("[app]\nretries = 5\n")

        @command()
        @option("configs", multiple=True, nargs=2)
        @to_path()
        @load_toml()
        def cmd(configs: Any) -> None:
            assert configs is not None
            for i, group in enumerate(configs, 1):
                # Merge configs
                merged = {}
                for cfg in group:
                    if "app" in cfg:
                        merged.update(cfg["app"])
                click.echo(
                    f"Config {i}: timeout={merged.get('timeout')}, "
                    f"retries={merged.get('retries')}"
                )

        result = cli_runner.invoke(
            cmd,
            [
                "--configs",
                str(base1),
                str(override1),
                "--configs",
                str(base2),
                str(override2),
            ],
        )
        assert result.exit_code == 0
        assert "Config 1: timeout=60, retries=3" in result.output
        assert "Config 2: timeout=30, retries=5" in result.output


class TestLoadTomlPractical:
    """Test practical use cases for load_toml."""

    def test_load_toml_pyproject(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml with pyproject.toml-like file."""
        toml_file = tmp_path / "pyproject.toml"
        content = """
[project]
name = "mypackage"
version = "1.0.0"
dependencies = ["click>=8.0"]

[tool.pytest]
testpaths = ["tests"]
"""
        toml_file.write_text(content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"Package: {config['project']['name']}")
            click.echo(f"Version: {config['project']['version']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Package: mypackage" in result.output
        assert "Version: 1.0.0" in result.output

    def test_load_toml_with_to_path_validation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_toml chained with to_path validation."""
        toml_file = tmp_path / "config.toml"
        toml_file.write_text('[app]\nstatus = "ok"\n')

        @command()
        @option("config", default=None)
        @to_path(
            extensions=[".toml"],
            allow_directory=False,
            allow_empty_file=False,
        )
        @load_toml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"Status: {config['app']['status']}")

        result = cli_runner.invoke(cmd, ["--config", str(toml_file)])
        assert result.exit_code == 0
        assert "Status: ok" in result.output
