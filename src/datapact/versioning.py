"""
Contract versioning and compatibility management.
Handles version registry, migration, compatibility checks, and breaking changes.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class VersionInfo:
    """
    Information about a contract version (metadata, deprecation, breaking changes).
    """
    version: str
    released: str  # ISO date
    is_deprecated: bool = False
    deprecation_message: str = ""
    breaking_changes: List[str] = None

    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []


# Define supported contract versions and their compatibility
VERSION_REGISTRY = {
    "1.0.0": VersionInfo(
        version="1.0.0",
        released="2026-01-01",
        is_deprecated=False,
        breaking_changes=[],
    ),
    "1.1.0": VersionInfo(
        version="1.1.0",
        released="2026-02-01",
        is_deprecated=False,
        breaking_changes=[
            "Added 'max_z_score' distribution rule",
            "Added 'max_null_ratio' quality rule",
        ],
    ),
    "2.0.0": VersionInfo(
        version="2.0.0",
        released="2026-03-01",
        is_deprecated=False,
        breaking_changes=[
            "Removed support for 'max_null_pct' (use 'max_null_ratio' instead)",
            "Changed distribution rule syntax",
        ],
    ),
}

# Current/latest version
LATEST_VERSION = "2.0.0"

# Define backward compatibility: key = tool version,
# value = contract versions it supports
TOOL_COMPATIBILITY = {
    "0.1.0": ["1.0.0", "1.1.0"],  # Initial release supports v1.0 and v1.1
    "0.2.0": ["1.0.0", "1.1.0", "2.0.0"],  # Adds v2.0 support
}

ODCS_SUPPORTED_VERSIONS = ["v3.1.0"]


class VersionError(Exception):
    """Raised when a version-related error occurs."""
    pass


class VersionMigration:
    """
    Handles contract schema migration between versions.
    Provides migration logic for each version step.
    """

    @staticmethod
    def migrate(contract_dict: Dict, from_version: str, to_version: str) -> Dict:
        """
        Migrate contract from one version to another.
        Args:
            contract_dict: Contract data as dictionary
            from_version: Current contract version
            to_version: Target contract version
        Returns:
            Migrated contract dictionary
        Raises:
            VersionError: If migration is not supported
        """
        if from_version == to_version:
            return contract_dict

        # Get migration path (ordered list of version steps)
        path = VersionMigration._get_migration_path(from_version, to_version)
        if not path:
            raise VersionError(
                f"Cannot migrate from {from_version} to {to_version}"
            )

        # Apply migrations step by step
        current = contract_dict.copy()
        for src_ver, dst_ver in path:
            current = VersionMigration._migrate_step(current, src_ver, dst_ver)

        return current

    @staticmethod
    def _get_migration_path(
        from_version: str, to_version: str
    ) -> List[Tuple[str, str]]:
        """
        Get the migration path between two versions.
        Returns list of (from, to) version tuples.
        """
        versions = list(VERSION_REGISTRY.keys())
        try:
            from_idx = versions.index(from_version)
            to_idx = versions.index(to_version)
        except ValueError:
            return []

        # Downgrades are not supported
        if from_idx > to_idx:
            return []  # No downgrade migrations

        return [(versions[i], versions[i + 1]) for i in range(from_idx, to_idx)]

    @staticmethod
    def _migrate_step(contract_dict: Dict, from_ver: str, to_ver: str) -> Dict:
        """
        Apply migration for a single version step.
        Modifies contract dict in-place for each version upgrade.
        """
        contract = contract_dict.copy()

        if from_ver == "1.0.0" and to_ver == "1.1.0":
            # Migration 1.0.0 → 1.1.0
            # Add new optional fields with defaults
            fields = contract.get("fields", [])
            for field in fields:
                if "distribution" in field:
                    dist = field["distribution"]
                    # Add max_z_score if not present
                    if "max_z_score" not in dist:
                        dist["max_z_score"] = 3.0  # Default z-score

        elif from_ver == "1.1.0" and to_ver == "2.0.0":
            # Migration 1.1.0 → 2.0.0
            # Rename max_null_pct to max_null_ratio and convert percentage to ratio
            fields = contract.get("fields", [])
            for field in fields:
                if "rules" in field:
                    rules = field["rules"]
                    if "max_null_pct" in rules:
                        # Convert percentage (0-100) to ratio (0-1)
                        pct = rules.pop("max_null_pct")
                        rules["max_null_ratio"] = pct / 100.0

        contract["contract"]["version"] = to_ver
        return contract


def validate_version(version: str) -> bool:
    """
    Check if version is registered in the version registry.
    """
    return version in VERSION_REGISTRY


def is_version_deprecated(version: str) -> bool:
    """
    Check if version is deprecated in the version registry.
    """
    if version not in VERSION_REGISTRY:
        return False
    return VERSION_REGISTRY[version].is_deprecated


def get_deprecation_message(version: str) -> str:
    """
    Get deprecation message for a version from the registry.
    """
    if version not in VERSION_REGISTRY:
        return ""
    return VERSION_REGISTRY[version].deprecation_message


def get_breaking_changes(version: str) -> List[str]:
    """
    Get breaking changes introduced in this version from the registry.
    """
    if version not in VERSION_REGISTRY:
        return []
    return VERSION_REGISTRY[version].breaking_changes


def check_tool_compatibility(
    tool_version: str, contract_version: str
) -> Tuple[bool, str]:
    """
    Check if tool can handle contract version.
    Returns (is_compatible, message).
    """
    if contract_version not in VERSION_REGISTRY:
        return False, f"Unknown contract version: {contract_version}"

    if tool_version not in TOOL_COMPATIBILITY:
        return False, f"Unknown tool version: {tool_version}"

    supported = TOOL_COMPATIBILITY[tool_version]
    if contract_version in supported:
        return True, ""

    return False, (
        f"Tool v{tool_version} does not support contract v{contract_version}. "
        f"Supported versions: {', '.join(supported)}"
    )


def check_odcs_compatibility(api_version: str) -> Tuple[bool, str]:
    if api_version in ODCS_SUPPORTED_VERSIONS:
        return True, ""
    return False, (
        f"Unsupported ODCS apiVersion '{api_version}'. "
        f"Supported versions: {', '.join(ODCS_SUPPORTED_VERSIONS)}"
    )


def get_all_versions() -> List[str]:
    """
    Get all registered contract versions.
    """
    return sorted(VERSION_REGISTRY.keys())


def get_latest_version() -> str:
    """
    Get the latest contract version from the registry.
    """
    return LATEST_VERSION
