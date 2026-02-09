"""
Quality validation - nulls, uniqueness, ranges, regex, enums.
Checks field-level quality rules and produces errors for violations.
"""

from typing import List, Tuple
import re
import pandas as pd
from datapact.contracts import Contract, Field


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
            k.lower(): self._normalize_severity(v)
            for k, v in (severity_overrides or {}).items()
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate data quality for all fields with rules.
        Returns (is_valid, error_messages).
        """
        self.errors = []

        for field in self.contract.fields:
            if field.name not in self.df.columns:
                continue

            column = self.df[field.name]
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
            # Debug: print actual values being checked for regex
            if field.name in ("date", "origination_date"):
                print(f"[DEBUG] Regex check for field '{field.name}':", list(non_null))
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
        severity = self._rule_severity(field_name, rule_name)
        self.errors.append(f"{severity}: {message}")

    def _rule_severity(self, field_name: str, rule_name: str) -> str:
        override_key = f"{field_name}.{rule_name}".lower()
        if override_key in self.severity_overrides:
            return self.severity_overrides[override_key]

        severities = getattr(self.contract_field_rules(field_name), "severities", {})
        if rule_name in severities:
            return self._normalize_severity(severities[rule_name])

        return "ERROR"

    def contract_field_rules(self, field_name: str):
        for field in self.contract.fields:
            if field.name == field_name:
                return field.rules
        return None

    @staticmethod
    def _normalize_severity(value) -> str:
        if value is None:
            return "ERROR"
        normalized = str(value).upper()
        if normalized not in {"ERROR", "WARN"}:
            return "ERROR"
        return normalized
