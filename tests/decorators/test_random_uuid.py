"""Tests for random_uuid decorator."""

from uuid import (
    NAMESPACE_DNS,
    NAMESPACE_OID,
    NAMESPACE_URL,
    NAMESPACE_X500,
    UUID,
)

import click
import pytest
from click.testing import CliRunner

from click_extended.core.command import command
from click_extended.core.option import option
from click_extended.decorators.random_uuid import random_uuid


class TestRandomUUIDVersion1:
    """Test UUID version 1 (time-based)."""

    def test_generates_version_1(self, cli_runner: CliRunner) -> None:
        """Test that version 1 UUID is generated correctly."""

        @command()
        @random_uuid("uuid", version=1)
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 1" in result.output

    def test_version_1_is_valid_uuid(self, cli_runner: CliRunner) -> None:
        """Test that version 1 generates a valid UUID object."""

        @command()
        @random_uuid("uuid", version=1)
        def cmd(uuid: UUID) -> None:
            click.echo(f"Type: {type(uuid).__name__}")
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Type: UUID" in result.output
        # Verify it's a valid UUID format
        uuid_str = result.output.split("UUID: ")[1].strip()
        assert len(uuid_str) == 36  # Standard UUID string length
        assert uuid_str.count("-") == 4

    def test_version_1_different_on_multiple_calls(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that version 1 generates different UUIDs (time-based)."""
        results = []

        for _ in range(3):

            @command()
            @random_uuid("uuid", version=1)
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be different due to time component
        assert len(set(results)) == 3


class TestRandomUUIDVersion3:
    """Test UUID version 3 (MD5 hash-based)."""

    def test_generates_version_3(self, cli_runner: CliRunner) -> None:
        """Test that version 3 UUID is generated correctly."""

        @command()
        @random_uuid(
            "uuid", version=3, namespace=NAMESPACE_DNS, uuid_name="example.com"
        )
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 3" in result.output

    def test_version_3_is_deterministic(self, cli_runner: CliRunner) -> None:
        """Test that same namespace and name produce same UUID."""
        results = []

        for _ in range(3):

            @command()
            @random_uuid(
                "uuid",
                version=3,
                namespace=NAMESPACE_DNS,
                uuid_name="test.example",
            )
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be identical (deterministic)
        assert len(set(results)) == 1

    def test_version_3_different_names_different_uuids(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different names produce different UUIDs."""
        results = []
        names = ["name1", "name2", "name3"]

        for name in names:

            @command()
            @random_uuid(
                "uuid", version=3, namespace=NAMESPACE_DNS, uuid_name=name
            )
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be different (different names)
        assert len(set(results)) == 3

    def test_version_3_different_namespaces_different_uuids(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different namespaces produce different UUIDs."""
        results = []
        namespaces = [NAMESPACE_DNS, NAMESPACE_URL, NAMESPACE_OID]

        for ns in namespaces:

            @command()
            @random_uuid("uuid", version=3, namespace=ns, uuid_name="test")
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be different (different namespaces)
        assert len(set(results)) == 3

    def test_version_3_with_string_namespace(
        self, cli_runner: CliRunner
    ) -> None:
        """Test version 3 with string UUID namespace."""
        namespace_str = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"

        @command()
        @random_uuid(
            "uuid", version=3, namespace=namespace_str, uuid_name="test"
        )
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 3" in result.output

    def test_version_3_invalid_namespace_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that invalid namespace string raises helpful error."""

        @command()
        @random_uuid("uuid", version=3, namespace="invalid", uuid_name="test")
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "Invalid namespace UUID format" in result.output
        assert "invalid" in result.output
        assert "NAMESPACE_DNS" in result.output

    def test_version_3_missing_namespace(self, cli_runner: CliRunner) -> None:
        """Test that missing namespace raises error."""

        @command()
        @random_uuid("uuid", version=3, uuid_name="test")
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "namespace is required for UUID version 3" in result.output

    def test_version_3_missing_name(self, cli_runner: CliRunner) -> None:
        """Test that missing uuid_name raises error."""

        @command()
        @random_uuid("uuid", version=3, namespace=NAMESPACE_DNS)
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "uuid_name is required for UUID version 3" in result.output


class TestRandomUUIDVersion4:
    """Test UUID version 4 (random)."""

    def test_generates_version_4_default(self, cli_runner: CliRunner) -> None:
        """Test that version 4 is the default."""

        @command()
        @random_uuid("uuid", seed=42)
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 4" in result.output

    def test_generates_version_4_explicit(self, cli_runner: CliRunner) -> None:
        """Test explicit version 4 specification."""

        @command()
        @random_uuid("uuid", version=4, seed=100)
        def cmd(uuid: UUID) -> None:
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 4" in result.output

    def test_version_4_with_seed_is_deterministic(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that same seed produces same UUID."""
        results = []

        for _ in range(3):

            @command()
            @random_uuid("uuid", version=4, seed=200)
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be identical (same seed)
        assert len(set(results)) == 1

    def test_version_4_different_seeds_different_uuids(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that different seeds produce different UUIDs."""
        results = []

        for seed in [300, 301, 302]:

            @command()
            @random_uuid("uuid", version=4, seed=seed)
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be different (different seeds)
        assert len(set(results)) == 3

    def test_version_4_without_seed(self, cli_runner: CliRunner) -> None:
        """Test that version 4 without seed generates random UUIDs."""
        results = []

        for _ in range(3):

            @command()
            @random_uuid("uuid", version=4)
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # Should be different (no seed, random)
        assert len(set(results)) == 3


class TestRandomUUIDVersion5:
    """Test UUID version 5 (SHA-1 hash-based)."""

    def test_generates_version_5(self, cli_runner: CliRunner) -> None:
        """Test that version 5 UUID is generated correctly."""

        @command()
        @random_uuid(
            "uuid", version=5, namespace=NAMESPACE_DNS, uuid_name="example.com"
        )
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Version: {uuid.version}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Version: 5" in result.output

    def test_version_5_is_deterministic(self, cli_runner: CliRunner) -> None:
        """Test that same namespace and name produce same UUID."""
        results = []

        for _ in range(3):

            @command()
            @random_uuid(
                "uuid",
                version=5,
                namespace=NAMESPACE_URL,
                uuid_name="https://example.com",
            )
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # All should be identical (deterministic)
        assert len(set(results)) == 1

    def test_version_5_different_from_version_3(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that version 5 produces different UUID than version 3 with same inputs."""
        results = []

        for version in [3, 5]:

            @command()
            @random_uuid(
                "uuid",
                version=version,  # type: ignore[arg-type]
                namespace=NAMESPACE_DNS,
                uuid_name="test",
            )
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results.append(result.output)

        # Should be different (different hash algorithms)
        assert len(set(results)) == 2

    def test_version_5_with_all_namespace_constants(
        self, cli_runner: CliRunner
    ) -> None:
        """Test version 5 with all predefined namespaces."""
        namespaces = [
            (NAMESPACE_DNS, "dns"),
            (NAMESPACE_URL, "url"),
            (NAMESPACE_OID, "oid"),
            (NAMESPACE_X500, "x500"),
        ]

        for ns, name in namespaces:

            @command()
            @random_uuid("uuid", version=5, namespace=ns, uuid_name="test")
            def cmd(uuid: UUID) -> None:
                click.echo(f"Namespace: {name}")
                click.echo(f"Version: {uuid.version}")

            result = cli_runner.invoke(cmd)
            assert result.exit_code == 0
            assert f"Namespace: {name}" in result.output
            assert "Version: 5" in result.output

    def test_version_5_invalid_namespace_string(
        self, cli_runner: CliRunner
    ) -> None:
        """Test that invalid namespace string raises helpful error."""

        @command()
        @random_uuid(
            "uuid", version=5, namespace="not-a-uuid", uuid_name="test"
        )
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "Invalid namespace UUID format" in result.output
        assert "not-a-uuid" in result.output

    def test_version_5_missing_namespace(self, cli_runner: CliRunner) -> None:
        """Test that missing namespace raises error."""

        @command()
        @random_uuid("uuid", version=5, uuid_name="test")
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "namespace is required for UUID version 5" in result.output

    def test_version_5_missing_name(self, cli_runner: CliRunner) -> None:
        """Test that missing uuid_name raises error."""

        @command()
        @random_uuid("uuid", version=5, namespace=NAMESPACE_DNS)
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code != 0
        assert "uuid_name is required for UUID version 5" in result.output


class TestRandomUUIDEdgeCases:
    """Test edge cases and error conditions."""

    def test_unsupported_version(self, cli_runner: CliRunner) -> None:
        """Test that unsupported version raises error."""

        from click_extended.decorators.random_uuid import RandomUUID

        node = RandomUUID(name="test_uuid")
        with pytest.raises(ValueError, match="Unsupported UUID version"):
            node.load(None, version=2)  # type: ignore[arg-type]

    def test_uuid_object_type(self, cli_runner: CliRunner) -> None:
        """Test that the returned object is a UUID instance."""

        @command()
        @random_uuid("uuid", version=4, seed=42)
        def cmd(uuid: UUID) -> None:
            click.echo(f"IsUUID: {isinstance(uuid, UUID)}")
            click.echo(f"HasHex: {hasattr(uuid, 'hex')}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "IsUUID: True" in result.output
        assert "HasHex: True" in result.output

    def test_uuid_string_representation(self, cli_runner: CliRunner) -> None:
        """Test UUID string representation format."""

        @command()
        @random_uuid("uuid", version=4, seed=999)
        def cmd(uuid: UUID) -> None:
            uuid_str = str(uuid)
            click.echo(f"Length: {len(uuid_str)}")
            click.echo(f"Dashes: {uuid_str.count('-')}")
            click.echo(f"Format: {uuid_str}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Length: 36" in result.output
        assert "Dashes: 4" in result.output

    def test_seed_affects_only_version_4(self, cli_runner: CliRunner) -> None:
        """Test that seed parameter only affects version 4."""
        # Version 1 should be different even with same seed
        results_v1 = []
        for _ in range(2):

            @command()
            @random_uuid("uuid", version=1, seed=42)
            def cmd(uuid: UUID) -> None:
                click.echo(f"UUID: {uuid}")

            result = cli_runner.invoke(cmd)
            results_v1.append(result.output)

        # Version 1 should differ (time-based, seed doesn't affect it)
        assert len(set(results_v1)) == 2


class TestRandomUUIDIntegration:
    """Test random_uuid integration with other decorators."""

    def test_multiple_random_uuids(self, cli_runner: CliRunner) -> None:
        """Test multiple random_uuid decorators on same command."""

        @command()
        @random_uuid("id1", version=4, seed=100)
        @random_uuid("id2", version=4, seed=200)
        def cmd(id1: UUID, id2: UUID) -> None:
            click.echo(f"ID1: {id1}")
            click.echo(f"ID2: {id2}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0

        id1 = result.output.split("ID1: ")[1].split("\n")[0].strip()
        id2 = result.output.split("ID2: ")[1].strip()

        assert id1 != id2
        assert len(id1) == 36
        assert len(id2) == 36

    def test_mixed_versions(self, cli_runner: CliRunner) -> None:
        """Test mixing different UUID versions."""

        @command()
        @random_uuid("random_id", version=4, seed=300)
        @random_uuid(
            "deterministic_id",
            version=5,
            namespace=NAMESPACE_DNS,
            uuid_name="test",
        )
        def cmd(random_id: UUID, deterministic_id: UUID) -> None:
            click.echo(f"Random: {random_id}")
            click.echo(f"Deterministic: {deterministic_id}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Random:" in result.output
        assert "Deterministic:" in result.output

    def test_respects_default_none(self, cli_runner: CliRunner) -> None:
        """Test that decorator generates UUID when no option is defined."""

        @command()
        @random_uuid("uuid", version=4, seed=400)
        def cmd(uuid: UUID) -> None:
            click.echo(f"UUID: {uuid}")
            click.echo(f"Type: {type(uuid).__name__}")

        result = cli_runner.invoke(cmd)
        assert result.exit_code == 0
        assert "Type: UUID" in result.output
        # Verify the UUID was generated (36 characters including dashes)
        uuid_str = result.output.split("UUID: ")[1].split("\n")[0].strip()
        assert len(uuid_str) == 36
