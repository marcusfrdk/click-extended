"""Tests for the @dependencies decorator."""

from typing import Any

import pytest
from click.testing import CliRunner

from click_extended import argument, command, option
from click_extended.decorators import dependencies


class TestDependenciesBasic:
    """Test basic @dependencies functionality."""

    def test_dependencies_both_provided(self, cli_runner: Any) -> None:
        """Test that command succeeds when both params are provided."""

        @command()
        @option("username")
        @option("password")
        @dependencies("username", "password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "Login: john/secret" in result.output

    def test_dependencies_neither_provided(self, cli_runner: Any) -> None:
        """Test that command succeeds when neither param is provided."""

        @command()
        @option("username")
        @option("password")
        @dependencies("username", "password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(login, [])
        assert result.exit_code == 0
        assert "Login: None/None" in result.output

    def test_dependencies_one_provided_fails(self, cli_runner: Any) -> None:
        """Test that command fails when only one param is provided."""

        @command()
        @option("username")
        @option("password")
        @dependencies("username", "password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 1
        assert (
            "'--username' requires '--password' to be provided" in result.output
        )

    def test_dependencies_other_provided_fails(self, cli_runner: Any) -> None:
        """Test that command fails when the other param is provided."""

        @command()
        @option("username")
        @option("password")
        @dependencies("username", "password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        result = cli_runner.invoke(login, ["--password", "secret"])
        assert result.exit_code == 1
        assert (
            "'--password' requires '--username' to be provided" in result.output
        )


class TestDependenciesMultipleGroups:
    """Test @dependencies with multiple dependency groups."""

    def test_dependencies_multiple_groups_all_provided(
        self, cli_runner: Any
    ) -> None:
        """Test multiple groups with all params provided."""

        @command()
        @option("username")
        @option("password")
        @option("api_key", "--api-key")
        @option("api_secret", "--api-secret")
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(**kwargs: Any) -> None:
            print(f"Auth: {kwargs}")

        result = cli_runner.invoke(
            auth,
            [
                "--username",
                "john",
                "--password",
                "secret",
                "--api-key",
                "key123",
                "--api-secret",
                "secret456",
            ],
        )
        assert result.exit_code == 0

    def test_dependencies_multiple_groups_none_provided(
        self, cli_runner: Any
    ) -> None:
        """Test multiple groups with no params provided."""

        @command()
        @option("username")
        @option("password")
        @option("api_key", "--api-key")
        @option("api_secret", "--api-secret")
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(**kwargs: Any) -> None:
            print(f"Auth: {kwargs}")

        result = cli_runner.invoke(auth, [])
        assert result.exit_code == 0

    def test_dependencies_multiple_groups_first_group_incomplete(
        self, cli_runner: Any
    ) -> None:
        """Test multiple groups with first group incomplete."""

        @command()
        @option("username")
        @option("password")
        @option("api_key", "--api-key")
        @option("api_secret", "--api-secret")
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(**kwargs: Any) -> None:
            print(f"Auth: {kwargs}")

        result = cli_runner.invoke(auth, ["--username", "john"])
        assert result.exit_code == 1
        assert (
            "'--username' requires '--password' to be provided" in result.output
        )

    def test_dependencies_multiple_groups_second_group_incomplete(
        self, cli_runner: Any
    ) -> None:
        """Test multiple groups with second group incomplete."""

        @command()
        @option("username")
        @option("password")
        @option("api_key", "--api-key")
        @option("api_secret", "--api-secret")
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(**kwargs: Any) -> None:
            print(f"Auth: {kwargs}")

        result = cli_runner.invoke(auth, ["--api-key", "key123"])
        assert result.exit_code == 1
        assert (
            "'--api-key' requires '--api-secret' to be provided"
            in result.output
        )

    def test_dependencies_multiple_groups_first_complete_second_incomplete(
        self, cli_runner: Any
    ) -> None:
        """Test with first group complete and second incomplete."""

        @command()
        @option("username")
        @option("password")
        @option("api_key", "--api-key")
        @option("api_secret", "--api-secret")
        @dependencies("username", "password")
        @dependencies("api_key", "api_secret")
        def auth(**kwargs: Any) -> None:
            print(f"Auth: {kwargs}")

        result = cli_runner.invoke(
            auth,
            [
                "--username",
                "john",
                "--password",
                "secret",
                "--api-key",
                "key123",
            ],
        )
        assert result.exit_code == 1
        assert (
            "'--api-key' requires '--api-secret' to be provided"
            in result.output
        )


class TestDependenciesWithThreeOrMore:
    """Test @dependencies with three or more parameters."""

    def test_dependencies_three_params_all_provided(
        self, cli_runner: Any
    ) -> None:
        """Test three params all provided."""

        @command()
        @option("host")
        @option("port", type=int)
        @option("protocol")
        @dependencies("host", "port", "protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(
            connect,
            ["--host", "localhost", "--port", "8080", "--protocol", "http"],
        )
        assert result.exit_code == 0
        assert "Connect: localhost:8080 via http" in result.output

    def test_dependencies_three_params_none_provided(
        self, cli_runner: Any
    ) -> None:
        """Test three params none provided."""

        @command()
        @option("host")
        @option("port", type=int)
        @option("protocol")
        @dependencies("host", "port", "protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(connect, [])
        assert result.exit_code == 0

    def test_dependencies_three_params_one_provided(
        self, cli_runner: Any
    ) -> None:
        """Test three params with one provided."""

        @command()
        @option("host")
        @option("port", type=int)
        @option("protocol")
        @dependencies("host", "port", "protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(connect, ["--host", "localhost"])
        assert result.exit_code == 1
        assert "'--host' require '--port' and '--protocol'" in result.output

    def test_dependencies_three_params_two_provided(
        self, cli_runner: Any
    ) -> None:
        """Test three params with two provided."""

        @command()
        @option("host")
        @option("port", type=int)
        @option("protocol")
        @dependencies("host", "port", "protocol")
        def connect(host: str, port: int, protocol: str) -> None:
            print(f"Connect: {host}:{port} via {protocol}")

        result = cli_runner.invoke(
            connect, ["--host", "localhost", "--port", "8080"]
        )
        assert result.exit_code == 1
        assert "'--host' and '--port' requires '--protocol'" in result.output


class TestDependenciesWithArguments:
    """Test @dependencies with argument nodes."""

    def test_dependencies_with_arguments_both_provided(
        self, cli_runner: Any
    ) -> None:
        """Test dependencies with arguments when both provided."""

        @command()
        @argument("source")
        @argument("dest")
        @dependencies("source", "dest")
        def copy(source: str, dest: str) -> None:
            print(f"Copy {source} to {dest}")

        result = cli_runner.invoke(copy, ["file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copy file1.txt to file2.txt" in result.output

    def test_dependencies_with_optional_arguments_none_provided(
        self, cli_runner: Any
    ) -> None:
        """Test dependencies with optional arguments when none provided."""

        @command()
        @argument("source", required=False)
        @argument("dest", required=False)
        @dependencies("source", "dest")
        def copy(source: str, dest: str) -> None:
            print(f"Copy {source} to {dest}")

        result = cli_runner.invoke(copy, [])
        assert result.exit_code == 0
        assert "Copy None to None" in result.output

    def test_dependencies_with_optional_arguments_one_provided(
        self, cli_runner: Any
    ) -> None:
        """Test dependencies with optional arguments when one provided."""

        @command()
        @argument("source", required=False)
        @argument("dest", required=False)
        @dependencies("source", "dest")
        def copy(source: str, dest: str) -> None:
            print(f"Copy {source} to {dest}")

        result = cli_runner.invoke(copy, ["file1.txt"])
        assert result.exit_code == 1
        assert "'SOURCE' requires 'DEST' to be provided" in result.output


class TestDependenciesWithTags:
    """Test @dependencies with tag nodes."""

    def test_dependencies_with_tag_all_provided(self, cli_runner: Any) -> None:
        """Test dependencies with tag when all params provided."""
        from click_extended import tag

        @command()
        @option("username", tags="auth")
        @option("password", tags="auth")
        @option("token", tags="auth")
        @dependencies("auth")
        @tag("auth")
        def login(**kwargs: Any) -> None:
            print(f"Login: {kwargs}")

        result = cli_runner.invoke(
            login,
            ["--username", "john", "--password", "secret", "--token", "abc123"],
        )
        assert result.exit_code == 0

    def test_dependencies_with_tag_none_provided(self, cli_runner: Any) -> None:
        """Test dependencies with tag when no params provided."""
        from click_extended import tag

        @command()
        @option("username", tags="auth")
        @option("password", tags="auth")
        @option("token", tags="auth")
        @dependencies("auth")
        @tag("auth")
        def login(**kwargs: Any) -> None:
            print(f"Login: {kwargs}")

        result = cli_runner.invoke(login, [])
        assert result.exit_code == 0

    def test_dependencies_with_tag_one_provided(self, cli_runner: Any) -> None:
        """Test dependencies with tag when one param provided."""
        from click_extended import tag

        @command()
        @option("username", tags="auth")
        @option("password", tags="auth")
        @option("token", tags="auth")
        @dependencies("auth")
        @tag("auth")
        def login(**kwargs: Any) -> None:
            print(f"Login: {kwargs}")

        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 1
        assert (
            "'--username' require '--password' and '--token'" in result.output
        )


class TestDependenciesWithDefaults:
    """Test @dependencies with default values."""

    def test_dependencies_with_defaults_not_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that params with defaults are not considered provided."""

        @command()
        @option("verbose", is_flag=True, default=False)
        @option("debug", is_flag=True, default=False)
        @dependencies("verbose", "debug")
        def run(verbose: bool, debug: bool) -> None:
            print(f"Verbose: {verbose}, Debug: {debug}")

        result = cli_runner.invoke(run, [])
        assert result.exit_code == 0
        assert "Verbose: False, Debug: False" in result.output

    def test_dependencies_with_defaults_one_explicitly_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that explicitly providing one param triggers dependencies."""

        @command()
        @option("verbose", is_flag=True, default=False)
        @option("debug", is_flag=True, default=False)
        @dependencies("verbose", "debug")
        def run(verbose: bool, debug: bool) -> None:
            print(f"Verbose: {verbose}, Debug: {debug}")

        result = cli_runner.invoke(run, ["--verbose"])
        assert result.exit_code == 1
        assert "'--verbose' requires '--debug' to be provided" in result.output

    def test_dependencies_with_defaults_both_explicitly_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that explicitly providing both params succeeds."""

        @command()
        @option("verbose", is_flag=True, default=False)
        @option("debug", is_flag=True, default=False)
        @dependencies("verbose", "debug")
        def run(verbose: bool, debug: bool) -> None:
            print(f"Verbose: {verbose}, Debug: {debug}")

        result = cli_runner.invoke(run, ["--verbose", "--debug"])
        assert result.exit_code == 0
        assert "Verbose: True, Debug: True" in result.output


class TestDependenciesEdgeCases:
    """Test edge cases and special scenarios."""

    def test_dependencies_with_nonexistent_param(self, cli_runner: Any) -> None:
        """Test dependencies with nonexistent parameter name."""

        @command()
        @option("input")
        @dependencies("input", "nonexistent")
        def process(input: str) -> None:
            print(f"Input: {input}")

        # Should not fail - nonexistent param is treated as not provided
        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0

    def test_dependencies_single_param(self, cli_runner: Any) -> None:
        """Test dependencies with single parameter (no-op)."""

        @command()
        @option("input")
        @dependencies("input")
        def process(input: str) -> None:
            print(f"Input: {input}")

        # Should always succeed - single param has no dependencies
        result = cli_runner.invoke(process, ["--input", "file.txt"])
        assert result.exit_code == 0

        result = cli_runner.invoke(process, [])
        assert result.exit_code == 0

    def test_dependencies_mixed_with_other_validators(
        self, cli_runner: Any
    ) -> None:
        """Test dependencies combined with other validators."""
        from click_extended.decorators import not_empty

        @command()
        @option("username")
        @not_empty()
        @option("password")
        @not_empty()
        @dependencies("username", "password")
        def login(username: str, password: str) -> None:
            print(f"Login: {username}/{password}")

        # Both provided and valid
        result = cli_runner.invoke(
            login, ["--username", "john", "--password", "secret"]
        )
        assert result.exit_code == 0

        # One provided triggers dependency check
        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 1

        # Both provided but one empty triggers not_empty
        result = cli_runner.invoke(
            login, ["--username", "john", "--password", ""]
        )
        assert result.exit_code == 1


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture providing a Click CLI runner."""
    return CliRunner()
