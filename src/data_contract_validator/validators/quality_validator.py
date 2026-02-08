"""Quality validation - nulls, uniqueness, ranges, regex, enums."""

from typing import List, Tuple, Optional
import re
import pandas as pd
from data_contract_validator.contracts import Contract, Field, FieldRule


class QualityValidator:
    """Validate data quality against field rules."""

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate data quality. Returns (is_valid, error_messages)."""
        self.errors = []

        for field in self.contract.fields:
            if field.name not in self.df.columns:
                continue

            column = self.df[field.name]
            if field.rules:
                self._validate_field_rules(field, column)

        return len(self.errors) == 0, self.errors

    def _validate_field_rules(self, field: Field, column: pd.Series) -> None:
        """Apply all rules for a field."""
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
            pattern = re.compile(rules.regex)
            non_null = column.dropna().astype(str)
            violations = (~non_null.str.match(pattern)).sum()
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
