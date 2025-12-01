"""Tests for exclusive decorator."""

import click
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.core.tag import tag
from click_extended.decorators.exclusive import exclusive


class TestExclusiveBasic:
    """Test basic exclusive functionality with individual parents."""

    def test_exclusive_with_single_parent_both_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing both exclusive options raises error."""

        @command()
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents="format")
        def cmd(format: str | None, json: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}")

        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()
        assert "'format'" in result.output

    def test_exclusive_with_single_parent_only_one_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing only one exclusive option succeeds."""

        @command()
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents="format")
        def cmd(format: str | None, json: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}")

        # Only --json provided (exclusive decorator not triggered since format not provided)
        result = cli_runner.invoke(cmd, ["--json"])
        assert result.exit_code == 0
        assert "JSON: True" in result.output

        # Only --format provided (exclusive decorator not triggered at all)
        result = cli_runner.invoke(cmd, ["--format", "xml"])
        assert result.exit_code == 0
        assert "Format: xml" in result.output

    def test_exclusive_with_single_parent_neither_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing neither exclusive option succeeds."""

        @command()
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents="format")
        def cmd(format: str | None, json: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0

    def test_exclusive_with_multiple_parents_list(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive with multiple parents as a list."""

        @command()
        @option("--format", default=None)
        @option("--style", default=None)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents=["format", "style"])
        def cmd(format: str | None, style: str | None, json: bool) -> None:
            click.echo(f"Format: {format}, Style: {style}, JSON: {json}")

        # Conflict with format
        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

        # Conflict with style
        result = cli_runner.invoke(cmd, ["--style", "pretty", "--json"])
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

        # Conflict with both
        result = cli_runner.invoke(
            cmd, ["--format", "xml", "--style", "pretty", "--json"]
        )
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

    def test_exclusive_multiple_conflicts_shown(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that all conflicting options are shown in error."""

        @command()
        @option("--opt1", default=None)
        @option("--opt2", default=None)
        @option("--opt3", default=None)
        @option("--target", default=None)
        @exclusive(with_parents=["opt1", "opt2", "opt3"])
        def cmd(
            opt1: str | None,
            opt2: str | None,
            opt3: str | None,
            target: str | None,
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--target", "c"]
        )
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()
        # Should mention both conflicting options
        assert "opt1" in result.output
        assert "opt2" in result.output


class TestExclusiveWithTags:
    """Test exclusive functionality with tags."""

    def test_exclusive_with_tag_single_conflict(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive with a single tag."""

        @command()
        @option("--format", default=None, tags="output")
        @option("--style", default=None, tags="output")
        @option("--json", is_flag=True, default=False)
        @exclusive(with_tags="output")
        def cmd(format: str | None, style: str | None, json: bool) -> None:
            click.echo(f"Format: {format}, Style: {style}, JSON: {json}")

        # Conflict with format
        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

        # Conflict with style
        result = cli_runner.invoke(cmd, ["--style", "pretty", "--json"])
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

    def test_exclusive_with_tag_multiple_conflicts(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive with tag showing multiple conflicts."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @option("--target", default=None)
        @exclusive(with_tags="group")
        def cmd(
            opt1: str | None,
            opt2: str | None,
            opt3: str | None,
            target: str | None,
        ) -> None:
            click.echo("Success")

        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--target", "c"]
        )
        assert result.exit_code == 1
        assert "exclusive" in result.output.lower()

    def test_exclusive_with_multiple_tags(self, cli_runner: CliRunner) -> None:
        """Test exclusive with multiple tags."""

        @command()
        @option("--opt1", default=None, tags="tag1")
        @option("--opt2", default=None, tags="tag2")
        @option("--target", default=None)
        @exclusive(with_tags=["tag1", "tag2"])
        def cmd(opt1: str | None, opt2: str | None, target: str | None) -> None:
            click.echo("Success")

        # Conflict with tag1
        result = cli_runner.invoke(cmd, ["--opt1", "a", "--target", "b"])
        assert result.exit_code == 1

        # Conflict with tag2
        result = cli_runner.invoke(cmd, ["--opt2", "c", "--target", "d"])
        assert result.exit_code == 1


class TestExclusiveMixed:
    """Test exclusive with both parents and tags."""

    def test_exclusive_with_parents_and_tags(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive with both parent names and tags."""

        @command()
        @option("--format", default=None)
        @option("--opt1", default=None, tags="output")
        @option("--opt2", default=None, tags="output")
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents="format", with_tags="output")
        def cmd(
            format: str | None,
            opt1: str | None,
            opt2: str | None,
            json: bool,
        ) -> None:
            click.echo("Success")

        # Conflict with parent
        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1

        # Conflict with tagged option
        result = cli_runner.invoke(cmd, ["--opt1", "val", "--json"])
        assert result.exit_code == 1

        # No conflict
        result = cli_runner.invoke(cmd, ["--json"])
        assert result.exit_code == 0


class TestExclusiveOnTag:
    """Test exclusive decorator on a tag (handle_tag method)."""

    def test_tag_exclusive_multiple_provided(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that providing multiple options in exclusive tag fails."""

        @command()
        @option("--opt1", default=None, tags="exclusive_group")
        @option("--opt2", default=None, tags="exclusive_group")
        @option("--opt3", default=None, tags="exclusive_group")
        @tag("exclusive_group")
        @exclusive()
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        # Two provided - should fail
        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 1
        assert "only one" in result.output.lower()

        # Three provided - should fail
        result = cli_runner.invoke(
            cmd, ["--opt1", "a", "--opt2", "b", "--opt3", "c"]
        )
        assert result.exit_code == 1
        assert "only one" in result.output.lower()

    def test_tag_exclusive_single_provided(self, cli_runner: CliRunner) -> None:
        """Test that providing only one option in exclusive tag succeeds."""

        @command()
        @option("--opt1", default=None, tags="exclusive_group")
        @option("--opt2", default=None, tags="exclusive_group")
        @option("--opt3", default=None, tags="exclusive_group")
        @tag("exclusive_group")
        @exclusive()
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo(f"Opt1: {opt1}, Opt2: {opt2}, Opt3: {opt3}")

        # Only opt1
        result = cli_runner.invoke(cmd, ["--opt1", "value1"])
        assert result.exit_code == 0
        assert "Opt1: value1" in result.output

        # Only opt2
        result = cli_runner.invoke(cmd, ["--opt2", "value2"])
        assert result.exit_code == 0
        assert "Opt2: value2" in result.output

    def test_tag_exclusive_none_provided(self, cli_runner: CliRunner) -> None:
        """Test that providing no options in exclusive tag succeeds."""

        @command()
        @option("--opt1", default=None, tags="exclusive_group")
        @option("--opt2", default=None, tags="exclusive_group")
        @tag("exclusive_group")
        @exclusive()
        def cmd(opt1: str | None, opt2: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0
        assert "Success" in result.output


class TestExclusiveEdgeCases:
    """Test edge cases and error conditions."""

    def test_exclusive_with_nonexistent_parent(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive with non-existent parent name doesn't crash."""

        @command()
        @exclusive(with_parents="nonexistent")
        @option("--opt", default=None)
        def cmd(opt: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt", "value"])
        assert result.exit_code == 0

    def test_exclusive_with_empty_tag(self, cli_runner: CliRunner) -> None:
        """Test exclusive with tag that has no parents."""

        @command()
        @tag("empty_tag")
        @exclusive()
        @option("--opt", default=None)
        def cmd(opt: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt", "value"])
        assert result.exit_code == 0

    def test_exclusive_with_defaults_not_triggered(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that exclusive only checks provided values, not defaults."""

        @command()
        @option("--format", default="xml")
        @exclusive(with_parents="format")
        @option("--json", is_flag=True, default=False)
        def cmd(format: str, json: bool) -> None:
            click.echo(f"Format: {format}, JSON: {json}")

        # Both have defaults but neither explicitly provided
        result = cli_runner.invoke(cmd, [])
        assert result.exit_code == 0

        # Only one explicitly provided
        result = cli_runner.invoke(cmd, ["--json"])
        assert result.exit_code == 0

    def test_exclusive_string_normalized_to_list(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that string parameters are normalized to lists."""

        @command()
        @option("--opt1", default=None)
        @exclusive(with_parents="opt1")
        @option("--opt2", default=None)
        def cmd(opt1: str | None, opt2: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 1


class TestExclusiveErrorMessages:
    """Test error message formatting."""

    def test_error_message_includes_parent_type(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message includes parent node type."""

        @command()
        @option("--format", default=None)
        @exclusive(with_parents="format")
        @option("--json", is_flag=True, default=False)
        def cmd(format: str | None, json: bool) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1
        assert "Option" in result.output  # Shows parent type

    def test_error_message_includes_parent_name(
        self, cli_runner: CliRunner
    ) -> None:
        """Test error message includes parent node name."""

        @command()
        @option("--format", default=None)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents="format")
        def cmd(format: str | None, json: bool) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--format", "xml", "--json"])
        assert result.exit_code == 1
        assert "'json'" in result.output  # Shows current parent name

    def test_tag_error_message_shows_count(self, cli_runner: CliRunner) -> None:
        """Test tag exclusive error shows how many were provided."""

        @command()
        @option("--opt1", default=None, tags="group")
        @option("--opt2", default=None, tags="group")
        @option("--opt3", default=None, tags="group")
        @tag("group")
        @exclusive()
        def cmd(opt1: str | None, opt2: str | None, opt3: str | None) -> None:
            click.echo("Success")

        result = cli_runner.invoke(cmd, ["--opt1", "a", "--opt2", "b"])
        assert result.exit_code == 1
        assert "got 2" in result.output or "2" in result.output


class TestExclusivePractical:
    """Test practical use cases."""

    def test_output_format_exclusive(self, cli_runner: CliRunner) -> None:
        """Test exclusive output formats (json vs xml vs yaml)."""

        @command()
        @option("--xml", is_flag=True, default=False)
        @option("--yaml", is_flag=True, default=False)
        @option("--json", is_flag=True, default=False)
        @exclusive(with_parents=["xml", "yaml"])
        def cmd(xml: bool, yaml: bool, json: bool) -> None:
            if json:
                click.echo("Output: JSON")
            elif xml:
                click.echo("Output: XML")
            elif yaml:
                click.echo("Output: YAML")
            else:
                click.echo("Output: Default")

        # Each format alone should work
        assert cli_runner.invoke(cmd, ["--json"]).exit_code == 0
        assert cli_runner.invoke(cmd, ["--xml"]).exit_code == 0
        assert cli_runner.invoke(cmd, ["--yaml"]).exit_code == 0

        # Conflicts should fail
        assert cli_runner.invoke(cmd, ["--json", "--xml"]).exit_code == 1
        assert cli_runner.invoke(cmd, ["--json", "--yaml"]).exit_code == 1

    def test_authentication_methods_exclusive(
        self, cli_runner: CliRunner
    ) -> None:
        """Test exclusive authentication methods."""

        @command()
        @option("--token", default=None, tags="auth")
        @option("--api-key", default=None, tags="auth")
        @option("--oauth", default=None, tags="auth")
        @tag("auth")
        @exclusive()
        def cmd(
            token: str | None, api_key: str | None, oauth: str | None
        ) -> None:
            if token:
                click.echo(f"Using token: {token}")
            elif api_key:
                click.echo(f"Using API key: {api_key}")
            elif oauth:
                click.echo(f"Using OAuth: {oauth}")

        # Single auth method should work
        result = cli_runner.invoke(cmd, ["--token", "abc123"])
        assert result.exit_code == 0
        assert "Using token" in result.output

        # Multiple auth methods should fail
        result = cli_runner.invoke(cmd, ["--token", "abc", "--api-key", "xyz"])
        assert result.exit_code == 1
        assert "only one" in result.output.lower()

    def test_verbosity_levels_exclusive(self, cli_runner: CliRunner) -> None:
        """Test exclusive verbosity levels."""

        @command()
        @option("--quiet", is_flag=True, default=False)
        @option("--debug", is_flag=True, default=False)
        @option("--verbose", is_flag=True, default=False)
        @exclusive(with_parents=["quiet", "debug"])
        def cmd(quiet: bool, debug: bool, verbose: bool) -> None:
            if quiet:
                click.echo("Mode: Quiet")
            elif verbose:
                click.echo("Mode: Verbose")
            elif debug:
                click.echo("Mode: Debug")
            else:
                click.echo("Mode: Normal")

        # Each mode alone should work
        assert cli_runner.invoke(cmd, ["--verbose"]).exit_code == 0
        assert cli_runner.invoke(cmd, ["--quiet"]).exit_code == 0
        assert cli_runner.invoke(cmd, ["--debug"]).exit_code == 0

        # Conflicting modes should fail
        result = cli_runner.invoke(cmd, ["--verbose", "--quiet"])
        assert result.exit_code == 1

        result = cli_runner.invoke(cmd, ["--verbose", "--debug"])
        assert result.exit_code == 1
