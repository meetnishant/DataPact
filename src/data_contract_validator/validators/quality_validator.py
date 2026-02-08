"""
Quality validation - nulls, uniqueness, ranges, regex, enums.
Checks field-level quality rules and produces errors for violations.
"""

from typing import List, Tuple, Optional
import re
import pandas as pd
from data_contract_validator.contracts import Contract, Field, FieldRule


class QualityValidator:
    """
    Validate data quality against field rules (not_null, unique, min/max, regex, enum, max_null_ratio).
    Produces errors for violations of quality rules.
    """

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []

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

        return len(self.errors) == 0, self.errors

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
                self.errors.append(
                    f"ERROR: Field '{field.name}' has {null_count} null values, "
                    f"but not_null=true"
                )

        # max_null_ratio constraint
        if rules.max_null_ratio is not None:
            null_ratio = column.isna().sum() / len(column)
            if null_ratio > rules.max_null_ratio:
                self.errors.append(
                    f"ERROR: Field '{field.name}' null ratio ({null_ratio:.2%}) "
                    f"exceeds max_null_ratio={rules.max_null_ratio}"
                )

        # unique constraint
        if rules.unique:
            non_null = column.dropna()
            duplicates = non_null.duplicated().sum()
            if duplicates > 0:
                self.errors.append(
                    f"ERROR: Field '{field.name}' has {duplicates} duplicate values, "
                    f"but unique=true"
                )

        # min/max range constraints
        non_null = column.dropna()
        if len(non_null) > 0:
            if rules.min is not None:
                violations = (non_null < rules.min).sum()
                if violations > 0:
                    self.errors.append(
                        f"ERROR: Field '{field.name}' has {violations} values < min ({rules.min})"
                    )

            if rules.max is not None:
                violations = (non_null > rules.max).sum()
                if violations > 0:
                    self.errors.append(
                        f"ERROR: Field '{field.name}' has {violations} values > max ({rules.max})"
                    )

        # regex constraint
        if rules.regex:
            # Use fullmatch for full-string regex validation
            pattern = rules.regex
            non_null = column.dropna().astype(str).str.strip()
            # Debug: print actual values being checked for regex
            if field.name in ("date", "origination_date"):
                print(f"[DEBUG] Regex check for field '{field.name}':", list(non_null))
            violations = (~non_null.str.fullmatch(pattern)).sum()
            if violations > 0:
                self.errors.append(
                    f"ERROR: Field '{field.name}' has {violations} values not matching regex '{rules.regex}'"
                )

        # enum constraint
        if rules.enum:
            valid_set = set(rules.enum)
            non_null = column.dropna()
            violations = (~non_null.isin(valid_set)).sum()
            if violations > 0:
                self.errors.append(
                    f"ERROR: Field '{field.name}' has {violations} values not in enum {valid_set}"
                )
