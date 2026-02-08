"""Schema validation - columns, types, required fields."""

from typing import List, Tuple
import pandas as pd
from data_contract_validator.contracts import Contract


class SchemaValidator:
    """Validate dataset schema against contract."""

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate schema. Returns (is_valid, error_messages)."""
        self.errors = []
        
        # Check for missing required fields
        for field in self.contract.fields:
            if field.required and field.name not in self.df.columns:
                self.errors.append(
                    f"ERROR: Required field '{field.name}' not found in dataset"
                )

        # Check for missing columns (not in contract)
        contract_fields = {f.name for f in self.contract.fields}
        for col in self.df.columns:
            if col not in contract_fields:
                self.errors.append(
                    f"WARN: Column '{col}' not in contract schema"
                )

        # Check type mismatches
        for field in self.contract.fields:
            if field.name in self.df.columns:
                actual_type = str(self.df[field.name].dtype)
                if not self._type_matches(actual_type, field.type):
                    self.errors.append(
                        f"ERROR: Column '{field.name}' type mismatch. "
                        f"Expected {field.type}, got {actual_type}"
                    )

        return len(self.errors) == 0, self.errors

    @staticmethod
    def _type_matches(actual: str, expected: str) -> bool:
        """Check if actual pandas dtype matches contract type."""
        type_map = {
            "integer": ["int", "int32", "int64"],
            "float": ["float", "float32", "float64"],
            "string": ["object", "string"],
            "boolean": ["bool"],
        }
        expected_types = type_map.get(expected, [])
        return any(t in actual for t in expected_types)
