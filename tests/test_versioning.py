"""Tests for contract versioning and compatibility."""

import pytest
from pathlib import Path

from datapact.versioning import (
    validate_version,
    is_version_deprecated,
    VersionMigration,
    check_tool_compatibility,
    get_breaking_changes,
    get_latest_version,
    VersionError,
)
from datapact.contracts import Contract


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVersionValidation:
    """Tests for version validation."""

    def test_valid_version(self):
        """Test valid version is recognized."""
        # All registered versions should be accepted
        assert validate_version("1.0.0")
        assert validate_version("1.1.0")
        assert validate_version("2.0.0")

    def test_invalid_version(self):
        """Test invalid version is rejected."""
        # Unknown or malformed versions are rejected
        assert not validate_version("0.1.0")
        assert not validate_version("3.0.0")
        assert not validate_version("1.2.3")

    def test_deprecated_version(self):
        """Test deprecation checking."""
        # Current versions should not be deprecated
        assert not is_version_deprecated("1.0.0")
        assert not is_version_deprecated("1.1.0")
        assert not is_version_deprecated("2.0.0")

    def test_breaking_changes(self):
        """Test getting breaking changes for a version."""
        # Ensure breaking change metadata is present for newer versions
        changes_110 = get_breaking_changes("1.1.0")
        assert len(changes_110) > 0
        assert any("max_z_score" in str(c) for c in changes_110)

        changes_200 = get_breaking_changes("2.0.0")
        assert len(changes_200) > 0
        assert any("max_null_ratio" in str(c) for c in changes_200)


class TestToolCompatibility:
    """Tests for tool and contract version compatibility."""

    def test_compatible_versions(self):
        """Test compatible tool and contract versions."""
        # Tool 0.2.0 supports all registered contract versions
        is_compat, msg = check_tool_compatibility("0.2.0", "1.0.0")
        assert is_compat
        assert msg == ""

        is_compat, msg = check_tool_compatibility("0.2.0", "2.0.0")
        assert is_compat
        assert msg == ""

    def test_incompatible_versions(self):
        """Test incompatible tool and contract versions."""
        # Older tool versions should reject newer contracts
        is_compat, msg = check_tool_compatibility("0.1.0", "2.0.0")
        assert not is_compat
        assert "not support" in msg.lower()

    def test_unknown_contract_version(self):
        """Test unknown contract version."""
        # Unknown contract versions must be rejected explicitly
        is_compat, msg = check_tool_compatibility("0.2.0", "99.0.0")
        assert not is_compat
        assert "unknown" in msg.lower()

    def test_tool_2_0_0_compatibility(self):
        """Test DataPact 2.0.0 tool supports all contract versions."""
        # DataPact 2.0.0 (current release) should support all contract versions
        assert check_tool_compatibility("2.0.0", "1.0.0")[0]
        assert check_tool_compatibility("2.0.0", "1.1.0")[0]
        assert check_tool_compatibility("2.0.0", "2.0.0")[0]


class TestVersionMigration:
    """Tests for contract migration between versions."""

    def test_no_migration_same_version(self):
        """Test that same version returns unchanged contract."""
        contract_dict = {
            "contract": {"name": "test", "version": "1.0.0"},
            "fields": [],
        }
        result = VersionMigration.migrate(contract_dict, "1.0.0", "1.0.0")
        assert result == contract_dict

    def test_migrate_1_0_to_1_1(self):
        """Test migration from 1.0.0 to 1.1.0."""
        # Migration should add default max_z_score
        contract_dict = {
            "contract": {"name": "test", "version": "1.0.0"},
            "fields": [
                {
                    "name": "score",
                    "type": "float",
                    "distribution": {"mean": 50.0, "std": 15.0},
                }
            ],
        }
        result = VersionMigration.migrate(contract_dict, "1.0.0", "1.1.0")

        # Check version was updated
        assert result["contract"]["version"] == "1.1.0"

        # Check max_z_score was added
        dist = result["fields"][0]["distribution"]
        assert "max_z_score" in dist
        assert dist["max_z_score"] == 3.0

    def test_migrate_1_1_to_2_0(self):
        """Test migration from 1.1.0 to 2.0.0."""
        # Migration should rename and convert null percentage to ratio
        contract_dict = {
            "contract": {"name": "test", "version": "1.1.0"},
            "fields": [
                {
                    "name": "age",
                    "type": "integer",
                    "rules": {"max_null_pct": 5},
                }
            ],
        }
        result = VersionMigration.migrate(contract_dict, "1.1.0", "2.0.0")

        # Check version was updated
        assert result["contract"]["version"] == "2.0.0"

        # Check max_null_pct was renamed and converted
        rules = result["fields"][0]["rules"]
        assert "max_null_pct" not in rules
        assert "max_null_ratio" in rules
        assert rules["max_null_ratio"] == 0.05

    def test_multi_step_migration(self):
        """Test migration across multiple versions."""
        # Multi-step migration should apply all intermediate changes
        contract_dict = {
            "contract": {"name": "test", "version": "1.0.0"},
            "fields": [
                {
                    "name": "score",
                    "type": "float",
                    "distribution": {"mean": 50.0},
                },
                {"name": "age", "type": "integer", "rules": {}},
            ],
        }
        result = VersionMigration.migrate(contract_dict, "1.0.0", "2.0.0")

        # Should have all updates from both migrations
        assert result["contract"]["version"] == "2.0.0"
        assert "max_z_score" in result["fields"][0]["distribution"]

    def test_unsupported_downgrade(self):
        """Test that downgrade migrations fail."""
        # Downgrades must raise to avoid data loss
        contract_dict = {
            "contract": {"name": "test", "version": "2.0.0"},
            "fields": [],
        }
        # Should raise error for downgrade
        with pytest.raises(VersionError):
            VersionMigration.migrate(contract_dict, "2.0.0", "1.0.0")


class TestContractVersionLoading:
    """Tests for loading contracts with version validation."""

    def test_load_v1_contract(self):
        """Test loading a v1.0.0 contract."""
        # Loader should auto-migrate to latest version
        contract = Contract.from_yaml(str(FIXTURES_DIR / "customer_contract_v1.yaml"))
        # Should auto-migrate to latest
        assert contract.version == "2.0.0"

    def test_load_v2_contract(self):
        """Test loading a v2.0.0 contract."""
        contract = Contract.from_yaml(str(FIXTURES_DIR / "customer_contract_v2.yaml"))
        assert contract.version == "2.0.0"

    def test_load_contract_without_version(self):
        """Test that loading contract without version fails."""
        # Missing version should raise a validation error
        import tempfile
        import yaml

        bad_contract = {"dataset": {"name": "test"}, "fields": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_contract, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="must specify"):
                Contract.from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_contract_with_unknown_version(self):
        """Test that loading contract with unknown version fails."""
        # Unknown versions should raise with a clear error
        import tempfile
        import yaml

        bad_contract = {
            "contract": {"name": "test", "version": "99.0.0"},
            "dataset": {"name": "test"},
            "fields": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_contract, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unknown contract version"):
                Contract.from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()


class TestVersionInfo:
    """Tests for version registry and info."""

    def test_latest_version(self):
        """Test getting latest version."""
        latest = get_latest_version()
        assert latest == "2.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
