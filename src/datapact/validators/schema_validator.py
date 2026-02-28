"""
Schema validation - columns, types, required fields.
Checks that dataset matches contract schema (required fields, types, extra columns).
"""

from typing import List, Tuple
import pandas as pd
from datapact.contracts import Contract


class SchemaValidator:
    """
    Validate dataset schema against contract (required fields, types, extra columns).
    Produces errors for missing/invalid fields and warnings for extra columns.
    """

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate schema: required fields, extra columns, type mismatches.
        Returns (is_valid, error_messages).
        """
        self.errors = []

        # Check for missing required fields
        for field in self.contract.fields:
            col_name = self.contract.resolve_column_name(field.name)
            if field.required and col_name not in self.df.columns:
                expected = (
                    f" (expected column '{col_name}')" if col_name != field.name else ""
                )
                self.errors.append(
                    f"ERROR: Required field '{field.name}' not found in dataset"
                    f"{expected}"
                )

        # Track contract-defined fields for extra-column warnings
        extra_severity = self.contract.schema_policy.extra_columns_severity
        contract_fields = {
            self.contract.resolve_column_name(f.name) for f in self.contract.fields
        }
        for col in self.df.columns:
            if col not in contract_fields:
                self.errors.append(
                    f"{extra_severity}: Column '{col}' not in contract schema"
                )

        # Check type mismatches between pandas dtypes and contract types
        for field in self.contract.fields:
            col_name = self.contract.resolve_column_name(field.name)
            if col_name in self.df.columns:
                actual_type = str(self.df[col_name].dtype)
                if not self._type_matches(actual_type, field.type):
                    self.errors.append(
                        f"ERROR: Column '{field.name}' type mismatch. "
                        f"Expected {field.type}, got {actual_type}"
                    )

        has_errors = any(err.startswith("ERROR") for err in self.errors)
        return not has_errors, self.errors

    @staticmethod
    def _type_matches(actual: str, expected: str) -> bool:
        """
        Check if actual pandas dtype matches contract type
        (integer, float, string, boolean, datetime).
        Uses startswith matching to avoid false positives from substring overlap
        (e.g. "int" must not match "datetime64[ns]").
        """
        type_map = {
            "integer": ["int", "uint"],
            "float": ["float"],
            "string": ["object", "string"],
            "boolean": ["bool"],
            "datetime": ["datetime"],
        }
        expected_types = type_map.get(expected, [])
        return any(actual.startswith(t) for t in expected_types)
