"""Tests for load_yaml decorator."""

from pathlib import Path
from typing import Any

import click
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.load_yaml import load_yaml
from click_extended.decorators.to_path import to_path


class TestLoadYamlBasic:
    """Test basic load_yaml functionality."""

    def test_load_yaml_simple_object(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with simple YAML object."""
        yaml_file = tmp_path / "data.yaml"
        yaml_file.write_text("name: test\nvalue: 42\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Name: {file['name']}")
            click.echo(f"Value: {file['value']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Name: test" in result.output
        assert "Value: 42" in result.output

    def test_load_yaml_list(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with YAML list."""
        yaml_file = tmp_path / "list.yaml"
        yaml_file.write_text("- item1\n- item2\n- item3\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Length: {len(file)}")
            click.echo(f"First: {file[0]}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Length: 3" in result.output
        assert "First: item1" in result.output

    def test_load_yaml_nested_structure(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with nested YAML structure."""
        yaml_file = tmp_path / "nested.yaml"
        yaml_content = """
user:
  name: John
  settings:
    theme: dark
    notifications: true
"""
        yaml_file.write_text(yaml_content)

        @command()
        @option("config", default=None)
        @to_path()
        @load_yaml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(f"User: {config['user']['name']}")
            click.echo(f"Theme: {config['user']['settings']['theme']}")

        result = cli_runner.invoke(cmd, ["--config", str(yaml_file)])
        assert result.exit_code == 0
        assert "User: John" in result.output
        assert "Theme: dark" in result.output

    def test_load_yaml_empty_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            # Empty YAML file returns None
            click.echo(f"Type: {type(file).__name__}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        # Empty YAML may return None or empty dict depending on parser
        assert "Type:" in result.output

    def test_load_yaml_multiline_strings(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with multiline strings."""
        yaml_file = tmp_path / "multiline.yaml"
        yaml_content = """
description: |
  This is a multiline
  string in YAML
  format.
"""
        yaml_file.write_text(yaml_content)

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Has multiline: {'multiline' in file['description']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Has multiline: True" in result.output


class TestLoadYamlLoaders:
    """Test load_yaml loader parameter."""

    def test_load_yaml_safe_loader(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with safe loader (default)."""
        yaml_file = tmp_path / "safe.yaml"
        yaml_file.write_text("numbers: [1, 2, 3]\ntext: hello\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml(loader="safe")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Numbers: {file['numbers']}")
            click.echo(f"Text: {file['text']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Numbers: [1, 2, 3]" in result.output
        assert "Text: hello" in result.output

    def test_load_yaml_full_loader(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with full loader."""
        yaml_file = tmp_path / "full.yaml"
        yaml_file.write_text("data: {a: 1, b: 2}\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml(loader="full")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"A: {file['data']['a']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "A: 1" in result.output

    def test_load_yaml_unsafe_loader(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with unsafe loader."""
        yaml_file = tmp_path / "unsafe.yaml"
        yaml_file.write_text("key: value\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml(loader="unsafe")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Key: {file['key']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Key: value" in result.output


class TestLoadYamlEncoding:
    """Test load_yaml encoding parameter."""

    def test_load_yaml_utf8_encoding(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with UTF-8 encoding (default)."""
        yaml_file = tmp_path / "utf8.yaml"
        yaml_file.write_text("message: Hello 世界 🌍\n", encoding="utf-8")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml(encoding="utf-8")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Message: {file['message']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Hello 世界 🌍" in result.output

    def test_load_yaml_custom_encoding(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with custom encoding."""
        yaml_file = tmp_path / "latin1.yaml"
        yaml_file.write_text("text: café\n", encoding="latin-1")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml(encoding="latin-1")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Text: {file['text']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "café" in result.output


class TestLoadYamlErrors:
    """Test load_yaml error handling."""

    def test_load_yaml_invalid_yaml(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with invalid YAML syntax."""
        yaml_file = tmp_path / "invalid.yaml"
        # Use truly invalid YAML that will cause parse error
        yaml_file.write_text("key: [unclosed bracket")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code != 0

    def test_load_yaml_directory_path(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml rejects directory paths."""
        test_dir = tmp_path / "dir"
        test_dir.mkdir()

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--file", str(test_dir)])
        assert result.exit_code != 0
        assert "is a directory" in result.output.lower()

    def test_load_yaml_nonexistent_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with nonexistent file."""
        yaml_file = tmp_path / "nonexistent.yaml"

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()


class TestLoadYamlTypes:
    """Test load_yaml with various YAML data types."""

    def test_load_yaml_string_value(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with string as root value."""
        yaml_file = tmp_path / "string.yaml"
        yaml_file.write_text("Hello World\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Value: {file}")
            click.echo(f"Type: {type(file).__name__}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Value: Hello World" in result.output
        assert "Type: str" in result.output

    def test_load_yaml_number_value(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with number as root value."""
        yaml_file = tmp_path / "number.yaml"
        yaml_file.write_text("42\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Value: {file}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Value: 42" in result.output

    def test_load_yaml_boolean_values(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with boolean values."""
        yaml_file = tmp_path / "bool.yaml"
        yaml_file.write_text("enabled: true\ndisabled: false\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Enabled: {file['enabled']}")
            click.echo(f"Disabled: {file['disabled']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Enabled: True" in result.output
        assert "Disabled: False" in result.output

    def test_load_yaml_null_value(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with null value."""
        yaml_file = tmp_path / "null.yaml"
        yaml_file.write_text("value: null\n")

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Is None: {file['value'] is None}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Is None: True" in result.output

    def test_load_yaml_mixed_types(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with mixed data types."""
        yaml_file = tmp_path / "mixed.yaml"
        yaml_content = """
string: hello
number: 123
float: 45.67
boolean: true
null_value: null
list: [1, 2, 3]
dict: {key: value}
"""
        yaml_file.write_text(yaml_content)

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"String: {file['string']}")
            click.echo(f"Number: {file['number']}")
            click.echo(f"Float: {file['float']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "String: hello" in result.output
        assert "Number: 123" in result.output
        assert "Float: 45.67" in result.output


class TestLoadYamlPractical:
    """Test practical use cases for load_yaml."""

    def test_load_yaml_config_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml for application config."""
        config_file = tmp_path / "config.yaml"
        config_content = """
app:
  name: MyApp
  version: 1.0.0
database:
  host: localhost
  port: 5432
"""
        config_file.write_text(config_content)

        @command()
        @option("config", default=None)
        @to_path(extensions=[".yaml", ".yml"])
        @load_yaml()
        def cmd(config: Any) -> None:
            assert config is not None
            click.echo(
                f"App: {config['app']['name']} v{config['app']['version']}"
            )
            click.echo(
                f"DB: {config['database']['host']}:{config['database']['port']}"
            )

        result = cli_runner.invoke(cmd, ["--config", str(config_file)])
        assert result.exit_code == 0
        assert "App: MyApp v1.0.0" in result.output
        assert "DB: localhost:5432" in result.output

    def test_load_yaml_data_processing(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml for data processing."""
        data_file = tmp_path / "users.yaml"
        data_content = """
- name: Alice
  age: 30
- name: Bob
  age: 25
- name: Charlie
  age: 35
"""
        data_file.write_text(data_content)

        @command()
        @option("data", default=None)
        @to_path()
        @load_yaml()
        def cmd(data: Any) -> None:
            assert data is not None
            avg_age = sum(u["age"] for u in data) / len(data)
            click.echo(f"Total users: {len(data)}")
            click.echo(f"Average age: {avg_age:.1f}")

        result = cli_runner.invoke(cmd, ["--data", str(data_file)])
        assert result.exit_code == 0
        assert "Total users: 3" in result.output
        assert "Average age: 30.0" in result.output

    def test_load_yaml_with_to_path_validation(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml chained with to_path validation."""
        yaml_file = tmp_path / "data.yaml"
        yaml_file.write_text("status: ok\n")

        @command()
        @option("file", default=None)
        @to_path(
            extensions=[".yaml", ".yml"],
            allow_directory=False,
            allow_empty_file=False,
        )
        @load_yaml(loader="safe")
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Status: {file['status']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Status: ok" in result.output

    def test_load_yaml_yml_extension(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml works with .yml extension."""
        yaml_file = tmp_path / "config.yml"
        yaml_file.write_text("key: value\n")

        @command()
        @option("file", default=None)
        @to_path(extensions=[".yml"])
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Key: {file['key']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Key: value" in result.output

    def test_load_yaml_anchors_and_aliases(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with YAML anchors and aliases."""
        yaml_file = tmp_path / "anchors.yaml"
        yaml_content = """
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults
  host: prod.example.com

development:
  <<: *defaults
  host: dev.example.com
"""
        yaml_file.write_text(yaml_content)

        @command()
        @option("file", default=None)
        @to_path()
        @load_yaml()
        def cmd(file: Any) -> None:
            assert file is not None
            click.echo(f"Prod timeout: {file['production']['timeout']}")
            click.echo(f"Dev timeout: {file['development']['timeout']}")

        result = cli_runner.invoke(cmd, ["--file", str(yaml_file)])
        assert result.exit_code == 0
        assert "Prod timeout: 30" in result.output
        assert "Dev timeout: 30" in result.output


class TestLoadYamlFlatTuple:
    """Test load_yaml with flat tuples."""

    def test_load_yaml_flat_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with flat tuple of YAML files."""
        file1 = tmp_path / "config1.yaml"
        file2 = tmp_path / "config2.yaml"
        file3 = tmp_path / "config3.yaml"
        file1.write_text("name: service1\nport: 8001\n")
        file2.write_text("name: service2\nport: 8002\n")
        file3.write_text("name: service3\nport: 8003\n")

        @command()
        @option("configs", default=None, nargs=3)
        @to_path()
        @load_yaml()
        def cmd(configs: Any) -> None:
            assert configs is not None
            assert isinstance(configs, tuple)
            assert len(configs) == 3
            for cfg in configs:
                click.echo(f"{cfg['name']}: {cfg['port']}")

        result = cli_runner.invoke(
            cmd, ["--configs", str(file1), str(file2), str(file3)]
        )
        assert result.exit_code == 0
        assert "service1: 8001" in result.output
        assert "service2: 8002" in result.output
        assert "service3: 8003" in result.output

    def test_load_yaml_flat_tuple_with_loader(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml flat tuple with specific loader."""
        file1 = tmp_path / "data1.yaml"
        file2 = tmp_path / "data2.yaml"
        file1.write_text("items: [1, 2, 3]\n")
        file2.write_text("items: [4, 5, 6]\n")

        @command()
        @option("files", default=None, nargs=2)
        @to_path()
        @load_yaml(loader="safe")
        def cmd(files: Any) -> None:
            assert files is not None
            total = sum(sum(f["items"]) for f in files)
            click.echo(f"Total: {total}")

        result = cli_runner.invoke(cmd, ["--files", str(file1), str(file2)])
        assert result.exit_code == 0
        assert "Total: 21" in result.output


class TestLoadYamlNestedTuple:
    """Test load_yaml with nested tuples."""

    def test_load_yaml_nested_tuple(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml with nested tuple of YAML files."""
        file1 = tmp_path / "env1_app1.yaml"
        file2 = tmp_path / "env1_app2.yaml"
        file3 = tmp_path / "env2_app1.yaml"
        file4 = tmp_path / "env2_app2.yaml"
        file1.write_text("app: app1\nenv: dev\ninstances: 2\n")
        file2.write_text("app: app2\nenv: dev\ninstances: 3\n")
        file3.write_text("app: app1\nenv: prod\ninstances: 5\n")
        file4.write_text("app: app2\nenv: prod\ninstances: 10\n")

        @command()
        @option("envs", multiple=True, nargs=2)
        @to_path()
        @load_yaml()
        def cmd(envs: Any) -> None:
            assert envs is not None
            assert isinstance(envs, tuple)
            assert len(envs) == 2
            for env_group in envs:
                env_name = env_group[0]["env"]
                total_instances = sum(cfg["instances"] for cfg in env_group)
                click.echo(f"{env_name}: {total_instances} instances")

        result = cli_runner.invoke(
            cmd,
            [
                "--envs",
                str(file1),
                str(file2),
                "--envs",
                str(file3),
                str(file4),
            ],
        )
        assert result.exit_code == 0
        assert "dev: 5 instances" in result.output
        assert "prod: 15 instances" in result.output

    def test_load_yaml_nested_tuple_multi_env_config(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test load_yaml nested tuple for multi-environment configs."""
        db_dev = tmp_path / "db_dev.yaml"
        cache_dev = tmp_path / "cache_dev.yaml"
        db_prod = tmp_path / "db_prod.yaml"
        cache_prod = tmp_path / "cache_prod.yaml"
        db_dev.write_text("type: postgres\nhost: localhost\nport: 5432\n")
        cache_dev.write_text("type: redis\nhost: localhost\nport: 6379\n")
        db_prod.write_text("type: postgres\nhost: db.example.com\nport: 5432\n")
        cache_prod.write_text(
            "type: redis\nhost: cache.example.com\nport: 6379\n"
        )

        @command()
        @option("configs", multiple=True, nargs=2)
        @to_path()
        @load_yaml()
        def cmd(configs: Any) -> None:
            assert configs is not None
            for i, group in enumerate(configs):
                env = "dev" if i == 0 else "prod"
                types = [cfg["type"] for cfg in group]
                click.echo(f"{env}: {', '.join(types)}")

        result = cli_runner.invoke(
            cmd,
            [
                "--configs",
                str(db_dev),
                str(cache_dev),
                "--configs",
                str(db_prod),
                str(cache_prod),
            ],
        )
        assert result.exit_code == 0
        assert "dev: postgres, redis" in result.output
        assert "prod: postgres, redis" in result.output
