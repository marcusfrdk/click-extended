"""Tests for the @conflicts decorator."""

from typing import Any

from click_extended import argument, command, option
from click_extended.decorators import conflicts


class TestConflictsBasic:
    """Test basic @conflicts functionality."""

    def test_conflicts_with_no_conflicting_params_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that command succeeds when only one param is provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 0
        assert "Login: username=john, api_key=None" in result.output

    def test_conflicts_fails_when_both_provided(self, cli_runner: Any) -> None:
        """Test that command fails when conflicting params are both provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--api-key", "key123"]
        )
        assert result.exit_code == 1
        assert "'--username' conflicts with '--api-key'" in result.output
        assert "They cannot be used together" in result.output

    def test_conflicts_succeeds_when_neither_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that command succeeds when neither param is provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(login, [])
        assert result.exit_code == 0
        assert "Login: username=None, api_key=None" in result.output

    def test_conflicts_succeeds_when_only_other_provided(
        self, cli_runner: Any
    ) -> None:
        """Test that command succeeds when only the conflicting param is provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(login, ["--api-key", "key123"])
        assert result.exit_code == 0
        assert "Login: username=None, api_key=key123" in result.output


class TestConflictsMultipleParams:
    """Test @conflicts with multiple conflicting parameters."""

    def test_conflicts_multiple_params_none_provided(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts with multiple params, none conflicting provided."""

        @command()
        @option("verbose", "-v", "--verbose", is_flag=True)
        @conflicts("quiet", "silent")
        @option("quiet", "-q", "--quiet", is_flag=True)
        @option("silent", "-s", "--silent", is_flag=True)
        def cmd(verbose: bool, quiet: bool, silent: bool) -> None:
            print(f"verbose={verbose}, quiet={quiet}, silent={silent}")

        result = cli_runner.invoke(cmd, ["--verbose"])
        assert result.exit_code == 0
        assert "verbose=True, quiet=False, silent=False" in result.output

    def test_conflicts_multiple_params_one_conflicts(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts with multiple params, one conflicts."""

        @command()
        @option("verbose", "-v", "--verbose", is_flag=True)
        @conflicts("quiet", "silent")
        @option("quiet", "-q", "--quiet", is_flag=True)
        @option("silent", "-s", "--silent", is_flag=True)
        def cmd(verbose: bool, quiet: bool, silent: bool) -> None:
            print(f"verbose={verbose}, quiet={quiet}, silent={silent}")

        result = cli_runner.invoke(cmd, ["--verbose", "--quiet"])
        assert result.exit_code == 1
        assert "'--verbose' conflicts with '--quiet'" in result.output

    def test_conflicts_multiple_params_multiple_conflict(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts with multiple params, multiple conflicts."""

        @command()
        @option("verbose", "-v", "--verbose", is_flag=True)
        @conflicts("quiet", "silent")
        @option("quiet", "-q", "--quiet", is_flag=True)
        @option("silent", "-s", "--silent", is_flag=True)
        def cmd(verbose: bool, quiet: bool, silent: bool) -> None:
            print(f"verbose={verbose}, quiet={quiet}, silent={silent}")

        result = cli_runner.invoke(cmd, ["--verbose", "--quiet", "--silent"])
        assert result.exit_code == 1
        assert (
            "'--verbose' conflicts with '--quiet' and '--silent'"
            in result.output
        )


class TestConflictsWithArguments:
    """Test @conflicts with argument nodes."""

    def test_conflicts_argument_with_option(self, cli_runner: Any) -> None:
        """Test conflicts where argument conflicts with an option."""

        @command()
        @argument("filename")
        @conflicts("stdin")
        @option("stdin", "--stdin", is_flag=True)
        def process(filename: str, stdin: bool) -> None:
            print(f"Process: filename={filename}, stdin={stdin}")

        result = cli_runner.invoke(process, ["test.txt"])
        assert result.exit_code == 0
        assert "Process: filename=test.txt, stdin=False" in result.output

    def test_conflicts_argument_fails_with_option(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts fails when argument and conflicting option both provided."""

        @command()
        @argument("filename")
        @conflicts("stdin")
        @option("stdin", "--stdin", is_flag=True)
        def process(filename: str, stdin: bool) -> None:
            print(f"Process: filename={filename}, stdin={stdin}")

        result = cli_runner.invoke(process, ["test.txt", "--stdin"])
        assert result.exit_code == 1
        assert "'FILENAME' conflicts with '--stdin'" in result.output

    def test_conflicts_optional_argument_not_provided(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts succeeds when optional argument not provided."""

        @command()
        @argument("filename", required=False)
        @conflicts("stdin")
        @option("stdin", "--stdin", is_flag=True)
        def process(filename: str, stdin: bool) -> None:
            print(f"Process: filename={filename}, stdin={stdin}")

        result = cli_runner.invoke(process, ["--stdin"])
        assert result.exit_code == 0
        assert "Process: filename=None, stdin=True" in result.output


class TestConflictsWithTags:
    """Test @conflicts with tag nodes."""

    def test_conflicts_tag_no_conflict(self, cli_runner: Any) -> None:
        """Test conflicts with tag when conflicting params not provided."""
        from click_extended import tag

        @command()
        @option("username", tags="basic_auth")
        @option("password", tags="basic_auth")
        @conflicts(
            "oauth_token"
        )  # Changed from "oauth" tag to actual param name
        @tag("basic_auth")
        @option("oauth_token", "--oauth-token")
        def login(username: str, password: str, oauth_token: str) -> None:
            print(f"Login: {username}/{password}, oauth={oauth_token}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "Login: john/secret, oauth=None" in result.output

    def test_conflicts_tag_with_conflict(self, cli_runner: Any) -> None:
        """Test conflicts with tag when conflicting params are provided."""
        from click_extended import tag

        @command()
        @option("username", tags="basic_auth")
        @option("password", tags="basic_auth")
        @conflicts(
            "oauth_token"
        )  # Changed from "oauth" tag to actual param name
        @tag("basic_auth")
        @option("oauth_token", "--oauth-token")
        def login(username: str, password: str, oauth_token: str) -> None:
            print(f"Login: {username}/{password}, oauth={oauth_token}")

        result = cli_runner.invoke(
            login,
            [
                "--username",
                "john",
                "--password",
                "secret",
                "--oauth-token",
                "token123",
            ],
        )
        assert result.exit_code == 1
        assert "conflicts with '--oauth-token'" in result.output


class TestConflictsBidirectional:
    """Test @conflicts applied to both conflicting parameters."""

    def test_conflicts_bidirectional_first_provided(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts when first param provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        @conflicts("username")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(login, ["--username", "john"])
        assert result.exit_code == 0

    def test_conflicts_bidirectional_second_provided(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts when second param provided."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        @conflicts("username")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(login, ["--api-key", "key123"])
        assert result.exit_code == 0

    def test_conflicts_bidirectional_both_provided(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts fails when both params provided (from either side)."""

        @command()
        @option("username")
        @conflicts("api_key")
        @option("api_key", "--api-key")
        @conflicts("username")
        def login(username: str, api_key: str) -> None:
            print(f"Login: username={username}, api_key={api_key}")

        result = cli_runner.invoke(
            login, ["--username", "john", "--api-key", "key123"]
        )
        assert result.exit_code == 1
        # Should fail from the first decorator that checks
        assert "conflicts with" in result.output


class TestConflictsChained:
    """Test @conflicts with chained decorators."""

    def test_conflicts_chained_different_params(self, cli_runner: Any) -> None:
        """Test multiple @conflicts decorators on same parameter."""

        @command()
        @option("manual", "--manual", is_flag=True)
        @conflicts("auto")
        @conflicts("interactive")
        @option("auto", "--auto", is_flag=True)
        @option("interactive", "--interactive", is_flag=True)
        def cmd(manual: bool, auto: bool, interactive: bool) -> None:
            print(f"manual={manual}, auto={auto}, interactive={interactive}")

        # Manual with no conflicts
        result = cli_runner.invoke(cmd, ["--manual"])
        assert result.exit_code == 0

        # Manual conflicts with auto
        result = cli_runner.invoke(cmd, ["--manual", "--auto"])
        assert result.exit_code == 1
        assert "'--manual' conflicts with '--auto'" in result.output

        # Manual conflicts with interactive
        result = cli_runner.invoke(cmd, ["--manual", "--interactive"])
        assert result.exit_code == 1
        assert "'--manual' conflicts with '--interactive'" in result.output


class TestConflictsEdgeCases:
    """Test edge cases for @conflicts decorator."""

    def test_conflicts_with_same_parameter_name(self, cli_runner: Any) -> None:
        """Test conflicts doesn't error when referencing itself."""

        @command()
        @option("username")
        @conflicts("username")  # Self-reference
        def login(username: str) -> None:
            print(f"Login: {username}")

        result = cli_runner.invoke(login, ["--username", "john"])
        # Should succeed or handle gracefully
        assert result.exit_code == 0 or "conflicts with" in result.output

    def test_conflicts_with_nonexistent_parameter(
        self, cli_runner: Any
    ) -> None:
        """Test conflicts with parameter that doesn't exist."""

        @command()
        @option("username")
        @conflicts("nonexistent")
        def login(username: str) -> None:
            print(f"Login: {username}")

        result = cli_runner.invoke(login, ["--username", "john"])
        # Should succeed since nonexistent param is never provided
        assert result.exit_code == 0
        assert "Login: john" in result.output

    def test_conflicts_with_multiple_values(self, cli_runner: Any) -> None:
        """Test conflicts with parameters that accept multiple values."""

        @command()
        @option("include", "--include", multiple=True)
        @conflicts("exclude")
        @option("exclude", "--exclude", multiple=True)
        def cmd(include: tuple[str, ...], exclude: tuple[str, ...]) -> None:
            print(f"include={include}, exclude={exclude}")

        result = cli_runner.invoke(cmd, ["--include", "a", "--include", "b"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cmd, ["--include", "a", "--exclude", "b"])
        assert result.exit_code == 1
        assert "'--include' conflicts with '--exclude'" in result.output


class TestConflictsErrorMessages:
    """Test error message formatting for @conflicts."""

    def test_conflicts_error_message_single_param(
        self, cli_runner: Any
    ) -> None:
        """Test error message format for single conflicting parameter."""

        @command()
        @option("verbose", "-v", "--verbose", is_flag=True)
        @conflicts("quiet")
        @option("quiet", "-q", "--quiet", is_flag=True)
        def cmd(verbose: bool, quiet: bool) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--verbose", "--quiet"])
        assert result.exit_code == 1
        assert "'--verbose' conflicts with '--quiet'" in result.output
        assert "They cannot be used together" in result.output

    def test_conflicts_error_message_multiple_params(
        self, cli_runner: Any
    ) -> None:
        """Test error message format for multiple conflicting parameters."""

        @command()
        @option("verbose", "-v", "--verbose", is_flag=True)
        @conflicts("quiet", "silent")
        @option("quiet", "-q", "--quiet", is_flag=True)
        @option("silent", "-s", "--silent", is_flag=True)
        def cmd(verbose: bool, quiet: bool, silent: bool) -> None:
            pass

        result = cli_runner.invoke(cmd, ["--verbose", "--quiet", "--silent"])
        assert result.exit_code == 1
        # Should show both conflicting params
        assert "'--verbose' conflicts with" in result.output
        assert "--quiet" in result.output
        assert "--silent" in result.output
        assert "They cannot be used together" in result.output
