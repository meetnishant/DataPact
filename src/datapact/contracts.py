"""
Contract parsing and validation module.
Defines dataclasses for contract, field, rules, and distribution, and provides
YAML parsing and migration logic.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import yaml
from datapact.versioning import (
    validate_version,
    is_version_deprecated,
    get_deprecation_message,
    VersionMigration,
    VersionError,
    LATEST_VERSION,
)


@dataclass
class FieldRule:
    """
    Represents validation rules for a field (quality constraints).
    Example: not_null, unique, min/max, regex, enum, max_null_ratio.
    """
    not_null: bool = False
    unique: bool = False
    min: Optional[float] = None
    max: Optional[float] = None
    regex: Optional[str] = None
    enum: Optional[List[Any]] = None
    max_null_ratio: Optional[float] = None
    severities: Dict[str, str] = field(default_factory=dict)


@dataclass
class DistributionRule:
    """
    Distribution-level validation rules for drift/outlier detection.
    Example: mean, std, max_drift_pct, max_z_score.
    """
    mean: Optional[float] = None
    std: Optional[float] = None
    max_drift_pct: Optional[float] = None
    max_z_score: Optional[float] = None


@dataclass
class Field:
    """
    Represents a field in the contract schema.
    Includes name, type, required, rules, and distribution.
    """
    name: str
    type: str
    required: bool = False
    rules: Optional[FieldRule] = None
    distribution: Optional[DistributionRule] = None


@dataclass
class Dataset:
    """
    Dataset metadata in the contract (e.g., source system name).
    """
    name: str


@dataclass
class Contract:
    """
    Root contract object. Contains contract metadata, dataset, and fields.
    """
    name: str
    version: str
    dataset: Dataset
    fields: List[Field]

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Contract":
        """
        Load and parse contract from YAML file.
        Handles version validation and migration if needed.
        """
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Contract":
        """
        Construct Contract from dictionary with validation and migration.
        Handles version checks, deprecation, and field parsing.
        """
        if not isinstance(data, dict):
            raise ValueError("Contract YAML must be a mapping with top-level keys")

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
            print(
                f"WARNING: Contract version {version} is deprecated."
                f" {deprecation_msg}"
            )

        # Auto-migrate to latest if needed
        if version != LATEST_VERSION:
            try:
                data = VersionMigration.migrate(data, version, LATEST_VERSION)
                print(
                    f"INFO: Auto-migrated contract from v{version} "
                    f"to v{LATEST_VERSION}"
                )
                contract_data = data.get("contract", {})
            except VersionError as e:
                raise ValueError(f"Failed to migrate contract: {e}")

        dataset_data = data.get("dataset", {})
        fields_data = data.get("fields", [])
        if not isinstance(fields_data, list):
            raise ValueError("Contract 'fields' must be a list")

        # Build field objects with parsed rules and distribution metadata
        fields: List[Field] = []
        for idx, field_data in enumerate(fields_data):
            if not isinstance(field_data, dict):
                raise ValueError(
                    f"Field entry at index {idx} must be a mapping"
                )
            if "name" not in field_data or "type" not in field_data:
                raise ValueError(
                    f"Field entry at index {idx} must include 'name' and 'type'"
                )

            fields.append(
                Field(
                    name=field_data["name"],
                    type=field_data["type"],
                    required=field_data.get("required", False),
                    rules=cls._parse_rules(field_data.get("rules", {})),
                    distribution=cls._parse_distribution(
                        field_data.get("distribution", {})
                    ),
                )
            )

        return cls(
            name=contract_data.get("name"),
            version=contract_data.get("version"),
            dataset=Dataset(name=dataset_data.get("name")),
            fields=fields,
        )

    @staticmethod
    def _parse_rules(rules_dict: Dict[str, Any]) -> Optional[FieldRule]:
        """
        Parse field validation rules from dict to FieldRule dataclass.
        """
        if not rules_dict:
            return None
        severities: Dict[str, str] = {}

        def read_rule(
            key: str,
            default: Any = None,
            boolean_default: bool = False,
        ) -> Any:
            raw = rules_dict.get(key, default)
            if isinstance(raw, dict):
                severity = raw.get("severity")
                value = raw.get("value") if "value" in raw else None
                if value is None and boolean_default:
                    value = True
                normalized = _normalize_severity(severity)
                if normalized:
                    severities[key] = normalized
                return value
            return raw

        def _normalize_severity(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            normalized = str(value).upper()
            if normalized not in {"ERROR", "WARN"}:
                raise ValueError(
                    f"Unsupported severity '{value}'. Use ERROR or WARN."
                )
            return normalized

        return FieldRule(
            not_null=read_rule("not_null", False, boolean_default=True),
            unique=read_rule("unique", False, boolean_default=True),
            min=read_rule("min"),
            max=read_rule("max"),
            regex=read_rule("regex"),
            enum=read_rule("enum"),
            max_null_ratio=read_rule("max_null_ratio"),
            severities=severities,
        )

    @staticmethod
    def _parse_distribution(dist_dict: Dict[str, Any]) -> Optional[DistributionRule]:
        """
        Parse distribution rules from dict to DistributionRule dataclass.
        """
        if not dist_dict:
            return None
        return DistributionRule(
            mean=dist_dict.get("mean"),
            std=dist_dict.get("std"),
            max_drift_pct=dist_dict.get("max_drift_pct"),
            max_z_score=dist_dict.get("max_z_score"),
        )
