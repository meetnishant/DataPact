"""
Quality validation - nulls, uniqueness, ranges, regex, enums.
Checks field-level quality rules and produces errors for violations.
"""

from typing import Dict, List, Tuple
import re
import pandas as pd
from datapact.contracts import Contract, Field


def resolve_rule_severity(
    contract: Contract,
    overrides: dict,
    field_name: str,
    rule_name: str,
) -> str:
    override_key = f"{field_name}.{rule_name}".lower()
    if override_key in overrides:
        return _normalize_severity(overrides[override_key])

    for field in contract.fields:
        if field.name == field_name and field.rules:
            severities = getattr(field.rules, "severities", {})
            if rule_name in severities:
                return _normalize_severity(severities[rule_name])

    return "ERROR"


def _normalize_severity(value) -> str:
    if value is None:
        return "ERROR"
    normalized = str(value).upper()
    if normalized not in {"ERROR", "WARN"}:
        return "ERROR"
    return normalized


class QualityValidator:
    """
    Validate data quality against field rules
    (not_null, unique, min/max, regex, enum, max_null_ratio).
    Produces errors for violations of quality rules.
    """

    def __init__(
        self,
        contract: Contract,
        df: pd.DataFrame,
        severity_overrides: dict = None,
    ):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []
        self.severity_overrides = {
            k.lower(): _normalize_severity(v)
            for k, v in (severity_overrides or {}).items()
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate data quality for all fields with rules.
        Returns (is_valid, error_messages).
        """
        self.errors = []

        for field in self.contract.fields:
            col_name = self.contract.resolve_column_name(field.name)
            if col_name not in self.df.columns:
                continue

            column = self.df[col_name]
            if field.rules:
                self._validate_field_rules(field, column)

        has_errors = any(err.startswith("ERROR") for err in self.errors)
        return not has_errors, self.errors

    def _validate_field_rules(self, field: Field, column: pd.Series) -> None:
        """
        Apply all quality rules for a field to the given column.
        Appends errors to self.errors for any violations found.
        """
        rules = field.rules
        if not rules:
            return

        # not_null constraint
        if rules.not_null:
            null_count = column.isna().sum()
            if null_count > 0:
                self._record(
                    field.name,
                    "not_null",
                    f"Field '{field.name}' has {null_count} null values, "
                    "but not_null=true",
                )

        # max_null_ratio constraint
        if rules.max_null_ratio is not None:
            if len(column) == 0:
                self._record(
                    field.name,
                    "max_null_ratio",
                    f"Field '{field.name}' has no rows; "
                    "cannot evaluate max_null_ratio",
                )
            else:
                null_ratio = column.isna().sum() / len(column)
                if null_ratio > rules.max_null_ratio:
                    self._record(
                        field.name,
                        "max_null_ratio",
                        f"Field '{field.name}' null ratio ({null_ratio:.2%}) "
                        f"exceeds max_null_ratio={rules.max_null_ratio}",
                    )

        # unique constraint
        if rules.unique:
            non_null = column.dropna()
            duplicates = non_null.duplicated().sum()
            if duplicates > 0:
                self._record(
                    field.name,
                    "unique",
                    f"Field '{field.name}' has {duplicates} duplicate values, "
                    "but unique=true",
                )

        # min/max range constraints
        non_null = column.dropna()
        if len(non_null) > 0:
            if rules.min is not None:
                violations = (non_null < rules.min).sum()
                if violations > 0:
                    self._record(
                        field.name,
                        "min",
                        f"Field '{field.name}' has {violations} values "
                        f"< min ({rules.min})",
                    )

            if rules.max is not None:
                violations = (non_null > rules.max).sum()
                if violations > 0:
                    self._record(
                        field.name,
                        "max",
                        f"Field '{field.name}' has {violations} values "
                        f"> max ({rules.max})",
                    )

        # regex constraint
        if rules.regex:
            # Use fullmatch for full-string regex validation
            pattern = rules.regex
            non_null = column.dropna().astype(str).str.strip()
            try:
                violations = (~non_null.str.fullmatch(pattern)).sum()
            except re.error as exc:
                self._record(
                    field.name,
                    "regex",
                    f"Field '{field.name}' has invalid regex '{rules.regex}': "
                    f"{exc}",
                )
            else:
                if violations > 0:
                    self._record(
                        field.name,
                        "regex",
                        f"Field '{field.name}' has {violations} values "
                        f"not matching regex '{rules.regex}'",
                    )

        # freshness constraint
        if rules.freshness_max_age_hours is not None:
            parsed = pd.to_datetime(column, errors="coerce", utc=True)
            max_ts = parsed.max()
            if pd.isna(max_ts):
                self._record(
                    field.name,
                    "freshness_max_age_hours",
                    f"Field '{field.name}' has no parsable timestamps",
                )
            else:
                now = pd.Timestamp.utcnow()
                age_hours = (now - max_ts).total_seconds() / 3600
                if age_hours > rules.freshness_max_age_hours:
                    self._record(
                        field.name,
                        "freshness_max_age_hours",
                        f"Field '{field.name}' freshness age {age_hours:.2f}h "
                        f"exceeds max_age_hours={rules.freshness_max_age_hours}",
                    )

        # enum constraint
        if rules.enum:
            try:
                valid_set = set(rules.enum)
            except TypeError:
                self._record(
                    field.name,
                    "enum",
                    f"Field '{field.name}' enum contains unhashable values",
                )
                return
            non_null = column.dropna()
            violations = (~non_null.isin(valid_set)).sum()
            if violations > 0:
                self._record(
                    field.name,
                    "enum",
                    f"Field '{field.name}' has {violations} values "
                    f"not in enum {valid_set}",
                )

    def _record(self, field_name: str, rule_name: str, message: str) -> None:
        severity = resolve_rule_severity(
            self.contract,
            self.severity_overrides,
            field_name,
            rule_name,
        )
        self.errors.append(f"{severity}: {message}")


class ChunkedQualityValidator:
    """
    Accumulate quality rule violations across chunks.
    """

    def __init__(self, contract: Contract, severity_overrides: dict = None):
        self.contract = contract
        self.severity_overrides = {
            k.lower(): _normalize_severity(v)
            for k, v in (severity_overrides or {}).items()
        }
        self.stats: Dict[str, dict] = {}
        self.invalid_regex: Dict[str, str] = {}
        self.enum_invalid: Dict[str, bool] = {}
        self.enum_sets: Dict[str, set] = {}
        self.seen_values: Dict[str, set] = {}
        self.column_map: Dict[str, str] = {}

        for field in contract.fields:
            if not field.rules:
                continue
            self.column_map[field.name] = contract.resolve_column_name(field.name)
            self.stats[field.name] = {
                "total": 0,
                "nulls": 0,
                "min_violations": 0,
                "max_violations": 0,
                "regex_violations": 0,
                "enum_violations": 0,
                "duplicates": 0,
                "max_ts": None,
                "has_ts": False,
            }
            if field.rules.unique:
                self.seen_values[field.name] = set()
            if field.rules.enum:
                try:
                    self.enum_sets[field.name] = set(field.rules.enum)
                except TypeError:
                    self.enum_invalid[field.name] = True

    def process_chunk(self, df: pd.DataFrame) -> None:
        for field in self.contract.fields:
            if not field.rules:
                continue
            col_name = self.column_map.get(field.name, field.name)
            if col_name not in df.columns:
                continue

            rules = field.rules
            stats = self.stats.get(field.name)
            if stats is None:
                continue

            column = df[col_name]
            stats["total"] += len(column)
            stats["nulls"] += column.isna().sum()

            non_null = column.dropna()

            if rules.unique:
                seen = self.seen_values[field.name]
                in_seen = non_null.isin(seen)
                cross_dupes = in_seen.sum()
                new_values = non_null[~in_seen]
                duplicates_within = new_values.duplicated().sum()
                stats["duplicates"] += cross_dupes + duplicates_within
                seen.update(new_values.unique())

            if rules.min is not None or rules.max is not None:
                numeric = pd.to_numeric(non_null, errors="coerce").dropna()
                if len(numeric) > 0:
                    if rules.min is not None:
                        stats["min_violations"] += (numeric < rules.min).sum()
                    if rules.max is not None:
                        stats["max_violations"] += (numeric > rules.max).sum()

            if rules.regex:
                if field.name not in self.invalid_regex:
                    try:
                        matches = (
                            non_null.astype(str).str.strip().str.fullmatch(rules.regex)
                        )
                        stats["regex_violations"] += (~matches).sum()
                    except re.error as exc:
                        self.invalid_regex[field.name] = str(exc)

            if rules.enum:
                if self.enum_invalid.get(field.name):
                    continue
                valid_set = self.enum_sets.get(field.name)
                if valid_set is not None:
                    stats["enum_violations"] += (~non_null.isin(valid_set)).sum()

            if rules.freshness_max_age_hours is not None:
                parsed = pd.to_datetime(column, errors="coerce", utc=True)
                max_ts = parsed.max()
                if not pd.isna(max_ts):
                    stats["has_ts"] = True
                    if stats["max_ts"] is None or max_ts > stats["max_ts"]:
                        stats["max_ts"] = max_ts

    def finalize(self) -> List[str]:
        errors: List[str] = []
        for field in self.contract.fields:
            rules = field.rules
            if not rules:
                continue

            stats = self.stats.get(field.name, {})
            total = stats.get("total", 0)
            nulls = stats.get("nulls", 0)

            if rules.not_null and nulls > 0:
                errors.append(
                    self._format(
                        field.name,
                        "not_null",
                        f"Field '{field.name}' has {nulls} null values, "
                        "but not_null=true",
                    )
                )

            if rules.max_null_ratio is not None:
                if total == 0:
                    errors.append(
                        self._format(
                            field.name,
                            "max_null_ratio",
                            f"Field '{field.name}' has no rows; "
                            "cannot evaluate max_null_ratio",
                        )
                    )
                else:
                    null_ratio = nulls / total
                    if null_ratio > rules.max_null_ratio:
                        errors.append(
                            self._format(
                                field.name,
                                "max_null_ratio",
                                f"Field '{field.name}' null ratio ({null_ratio:.2%}) "
                                f"exceeds max_null_ratio={rules.max_null_ratio}",
                            )
                        )

            duplicates = stats.get("duplicates", 0)
            if rules.unique and duplicates > 0:
                errors.append(
                    self._format(
                        field.name,
                        "unique",
                        f"Field '{field.name}' has {duplicates} duplicate values, "
                        "but unique=true",
                    )
                )

            min_violations = stats.get("min_violations", 0)
            if rules.min is not None and min_violations > 0:
                errors.append(
                    self._format(
                        field.name,
                        "min",
                        f"Field '{field.name}' has {min_violations} values "
                        f"< min ({rules.min})",
                    )
                )

            max_violations = stats.get("max_violations", 0)
            if rules.max is not None and max_violations > 0:
                errors.append(
                    self._format(
                        field.name,
                        "max",
                        f"Field '{field.name}' has {max_violations} values "
                        f"> max ({rules.max})",
                    )
                )

            if field.name in self.invalid_regex:
                errors.append(
                    self._format(
                        field.name,
                        "regex",
                        f"Field '{field.name}' has invalid regex '{rules.regex}': "
                        f"{self.invalid_regex[field.name]}",
                    )
                )
            else:
                regex_violations = stats.get("regex_violations", 0)
                if rules.regex and regex_violations > 0:
                    errors.append(
                        self._format(
                            field.name,
                            "regex",
                            f"Field '{field.name}' has {regex_violations} values "
                            f"not matching regex '{rules.regex}'",
                        )
                    )

            if self.enum_invalid.get(field.name):
                errors.append(
                    self._format(
                        field.name,
                        "enum",
                        f"Field '{field.name}' enum contains unhashable values",
                    )
                )
            else:
                enum_violations = stats.get("enum_violations", 0)
                if rules.enum and enum_violations > 0:
                    errors.append(
                        self._format(
                            field.name,
                            "enum",
                            f"Field '{field.name}' has {enum_violations} values "
                            f"not in enum {self.enum_sets.get(field.name)}",
                        )
                    )

            if rules.freshness_max_age_hours is not None:
                if not stats.get("has_ts"):
                    errors.append(
                        self._format(
                            field.name,
                            "freshness_max_age_hours",
                            f"Field '{field.name}' has no parsable timestamps",
                        )
                    )
                else:
                    now = pd.Timestamp.utcnow()
                    age_hours = (now - stats.get("max_ts")).total_seconds() / 3600
                    if age_hours > rules.freshness_max_age_hours:
                        error_msg = (
                            f"Field '{field.name}' freshness age {age_hours:.2f}h "
                            f"exceeds max_age_hours={rules.freshness_max_age_hours}"
                        )
                        errors.append(
                            self._format(
                                field.name, "freshness_max_age_hours", error_msg
                            )
                        )

        return errors

    def _format(self, field_name: str, rule_name: str, message: str) -> str:
        severity = resolve_rule_severity(
            self.contract,
            self.severity_overrides,
            field_name,
            rule_name,
        )
        return f"{severity}: {message}"
