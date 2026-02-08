"""Contract parsing and validation module."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import yaml
import json
from data_contract_validator.versioning import (
    validate_version,
    is_version_deprecated,
    get_deprecation_message,
    VersionMigration,
    VersionError,
    LATEST_VERSION,
)


@dataclass
class FieldRule:
    """Represents validation rules for a field."""
    not_null: bool = False
    unique: bool = False
    min: Optional[float] = None
    max: Optional[float] = None
    regex: Optional[str] = None
    enum: Optional[List[Any]] = None
    max_null_ratio: Optional[float] = None


@dataclass
class DistributionRule:
    """Distribution-level validation rules."""
    mean: Optional[float] = None
    std: Optional[float] = None
    max_drift_pct: Optional[float] = None
    max_z_score: Optional[float] = None


@dataclass
class Field:
    """Represents a field in the contract schema."""
    name: str
    type: str
    required: bool = False
    rules: Optional[FieldRule] = None
    distribution: Optional[DistributionRule] = None


@dataclass
class Dataset:
    """Dataset metadata in the contract."""
    name: str


@dataclass
class Contract:
    """Root contract object."""
    name: str
    version: str
    dataset: Dataset
    fields: List[Field]

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Contract":
        """Load and parse contract from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Contract":
        """Construct Contract from dictionary with validation."""
        contract_data = data.get("contract", {})
        version = contract_data.get("version")

        # Validate version
        if not version:
            raise ValueError("Contract must specify a 'version' field")

        if not validate_version(version):
            raise ValueError(
                f"Unknown contract version '{version}'. "
                f"Supported versions: {', '.join(['1.0.0', '1.1.0', '2.0.0'])}"
            )

        # Check for deprecation
        if is_version_deprecated(version):
            deprecation_msg = get_deprecation_message(version)
            print(f"WARNING: Contract version {version} is deprecated. {deprecation_msg}")

        # Auto-migrate to latest if needed
        if version != LATEST_VERSION:
            try:
                data = VersionMigration.migrate(data, version, LATEST_VERSION)
                print(f"INFO: Auto-migrated contract from v{version} to v{LATEST_VERSION}")
                contract_data = data.get("contract", {})
            except VersionError as e:
                raise ValueError(f"Failed to migrate contract: {e}")

        dataset_data = data.get("dataset", {})
        fields_data = data.get("fields", [])

        fields = [
            Field(
                name=f["name"],
                type=f["type"],
                required=f.get("required", False),
                rules=cls._parse_rules(f.get("rules", {})),
                distribution=cls._parse_distribution(f.get("distribution", {})),
            )
            for f in fields_data
        ]

        return cls(
            name=contract_data.get("name"),
            version=contract_data.get("version"),
            dataset=Dataset(name=dataset_data.get("name")),
            fields=fields,
        )

    @staticmethod
    def _parse_rules(rules_dict: Dict[str, Any]) -> Optional[FieldRule]:
        """Parse field validation rules."""
        if not rules_dict:
            return None
        return FieldRule(
            not_null=rules_dict.get("not_null", False),
            unique=rules_dict.get("unique", False),
            min=rules_dict.get("min"),
            max=rules_dict.get("max"),
            regex=rules_dict.get("regex"),
            enum=rules_dict.get("enum"),
            max_null_ratio=rules_dict.get("max_null_ratio"),
        )

    @staticmethod
    def _parse_distribution(dist_dict: Dict[str, Any]) -> Optional[DistributionRule]:
        """Parse distribution rules."""
        if not dist_dict:
            return None
        return DistributionRule(
            mean=dist_dict.get("mean"),
            std=dist_dict.get("std"),
            max_drift_pct=dist_dict.get("max_drift_pct"),
            max_z_score=dist_dict.get("max_z_score"),
        )
