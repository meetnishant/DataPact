"""
Validation reporting - summary, errors, warnings, and JSON export.
Defines ErrorRecord and ValidationReport for aggregating and outputting
validation results.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from datapact.versioning import (
    get_breaking_changes,
)


@dataclass
class ErrorRecord:
    """
    Individual validation error or warning.
    code: error type (e.g., SCHEMA, QUALITY, DISTRIBUTION)
    field: field name (if applicable)
    message: error/warning message
    severity: "ERROR" or "WARN"
    """
    code: str
    field: str
    message: str
    severity: str  # "ERROR" or "WARN"


@dataclass
class ValidationReport:
    """
    Complete validation report for a validation run.
    Includes summary, errors, warnings, and compatibility info.
    """
    passed: bool
    contract_name: str
    contract_version: str
    dataset_name: str
    timestamp: str
    tool_version: str
    error_count: int
    warning_count: int
    errors: List[ErrorRecord]
    compatibility_warnings: Optional[List[str]] = None

    def __post_init__(self):
        """
        Initialize compatibility warnings if not provided.
        """
        if self.compatibility_warnings is None:
            self.compatibility_warnings = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary for JSON serialization.
        Includes contract, dataset, metadata, summary, errors, and version info.
        """
        result = {
            "passed": self.passed,
            "contract": {
                "name": self.contract_name,
                "version": self.contract_version,
            },
            "dataset": {"name": self.dataset_name},
            "metadata": {
                "timestamp": self.timestamp,
                "tool_version": self.tool_version,
            },
            "summary": {
                "error_count": self.error_count,
                "warning_count": self.warning_count,
            },
            "errors": [asdict(e) for e in self.errors],
        }

        # Add version information when breaking changes exist
        breaking_changes = get_breaking_changes(self.contract_version)
        if breaking_changes:
            result["version_info"] = {
                "breaking_changes": breaking_changes,
                "migration_available": True,
            }

        # Add compatibility warnings if any
        if self.compatibility_warnings:
            result["compatibility_warnings"] = self.compatibility_warnings

        return result

    def save_json(self, output_dir: str = "./reports") -> str:
        """
        Save report to JSON file in the specified output directory.
        Returns the file path of the saved report.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_path / f"{timestamp}.json"

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return str(filepath)

    def print_summary(self) -> None:
        """
        Print human-readable summary of the validation report to the console.
        """
        status = "PASS" if self.passed else "FAIL"
        print(f"\n{'='*60}")
        print("DataPact Validation Report")
        print(f"{'='*60}")
        print(f"Status: {status}")
        print(f"Contract: {self.contract_name} (v{self.contract_version})")
        print(f"Dataset: {self.dataset_name}")
        print(f"Timestamp: {self.timestamp}")
        print("\nSummary:")
        print(f"  Errors: {self.error_count}")
        print(f"  Warnings: {self.warning_count}")

        if self.errors:
            print("\nDetails:")
            for err in self.errors:
                print(f"  [{err.severity}] {err.field}: {err.message}")
        print(f"{'='*60}\n")
