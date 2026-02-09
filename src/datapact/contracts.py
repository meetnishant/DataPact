"""
Contract parsing and validation module.
Defines dataclasses for contract, field, rules, and distribution, and provides
YAML parsing and migration logic.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import yaml
from datapact.policies import apply_policy_packs
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
    freshness_max_age_hours: Optional[float] = None
    custom: Dict[str, Any] = field(default_factory=dict)
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
class SchemaPolicy:
    """
    Schema drift handling configuration.
    """
    extra_columns_severity: str = "WARN"


@dataclass
class SLA:
    """
    Service-level agreement checks for datasets.
    """
    min_rows: Optional[int] = None
    max_rows: Optional[int] = None
    min_rows_severity: str = "ERROR"
    max_rows_severity: str = "ERROR"


@dataclass
class Contract:
    """
    Root contract object. Contains contract metadata, dataset, and fields.
    """
    name: str
    version: str
    dataset: Dataset
    fields: List[Field]
    schema_policy: SchemaPolicy = field(default_factory=SchemaPolicy)
    sla: SLA = field(default_factory=SLA)
    custom_rules: List[Dict[str, Any]] = field(default_factory=list)

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

        data = apply_policy_packs(data)

        dataset_data = data.get("dataset", {})
        schema_policy = cls._parse_schema_policy(data.get("schema", {}))
        sla = cls._parse_sla(data.get("sla", {}))
        custom_rules = cls._parse_custom_rules(data.get("custom_rules", []))
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
            schema_policy=schema_policy,
            sla=sla,
            custom_rules=custom_rules,
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

        custom_rules = rules_dict.get("custom", {})
        if custom_rules and not isinstance(custom_rules, dict):
            raise ValueError("rules.custom must be a mapping of rule_name to config")

        return FieldRule(
            not_null=read_rule("not_null", False, boolean_default=True),
            unique=read_rule("unique", False, boolean_default=True),
            min=read_rule("min"),
            max=read_rule("max"),
            regex=read_rule("regex"),
            enum=read_rule("enum"),
            max_null_ratio=read_rule("max_null_ratio"),
            freshness_max_age_hours=read_rule("freshness_max_age_hours"),
            custom=custom_rules or {},
            severities=severities,
        )

    @staticmethod
    def _parse_custom_rules(custom_rules: Any) -> List[Dict[str, Any]]:
        if not custom_rules:
            return []
        if not isinstance(custom_rules, list):
            raise ValueError("custom_rules must be a list")
        for idx, rule in enumerate(custom_rules):
            if not isinstance(rule, dict):
                raise ValueError(
                    f"custom_rules entry at index {idx} must be a mapping"
                )
            if "name" not in rule:
                raise ValueError(
                    f"custom_rules entry at index {idx} must include 'name'"
                )
        return custom_rules

    @staticmethod
    def _parse_schema_policy(schema_dict: Dict[str, Any]) -> SchemaPolicy:
        if not schema_dict:
            return SchemaPolicy()

        def normalize_severity(value: Optional[str]) -> str:
            if value is None:
                return "WARN"
            normalized = str(value).upper()
            if normalized not in {"ERROR", "WARN"}:
                raise ValueError(
                    f"Unsupported schema severity '{value}'. Use ERROR or WARN."
                )
            return normalized

        raw_extra = schema_dict.get("extra_columns")
        if isinstance(raw_extra, dict):
            extra_severity = normalize_severity(raw_extra.get("severity"))
        else:
            extra_severity = normalize_severity(raw_extra)

        return SchemaPolicy(extra_columns_severity=extra_severity)

    @staticmethod
    def _parse_sla(sla_dict: Dict[str, Any]) -> SLA:
        if not sla_dict:
            return SLA()

        def read_sla(key: str) -> Optional[int]:
            raw = sla_dict.get(key)
            if isinstance(raw, dict):
                return raw.get("value")
            return raw

        def read_severity(key: str, default: str = "ERROR") -> str:
            raw = sla_dict.get(key)
            if isinstance(raw, dict):
                severity = raw.get("severity", default)
            else:
                severity = default
            normalized = str(severity).upper()
            if normalized not in {"ERROR", "WARN"}:
                raise ValueError(
                    f"Unsupported SLA severity '{severity}'. Use ERROR or WARN."
                )
            return normalized

        return SLA(
            min_rows=read_sla("min_rows"),
            max_rows=read_sla("max_rows"),
            min_rows_severity=read_severity("min_rows"),
            max_rows_severity=read_severity("max_rows"),
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
