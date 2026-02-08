"""Command-line interface for data contract validation."""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from data_contract_validator.contracts import Contract
from data_contract_validator.datasource import DataSource
from data_contract_validator.validators import (
    SchemaValidator,
    QualityValidator,
    DistributionValidator,
)
from data_contract_validator.reporting import ValidationReport, ErrorRecord
from data_contract_validator.versioning import check_tool_compatibility


def main() -> int:
    """Main CLI entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Validate datasets against data contracts"
    )
    parser.add_argument(
        "command",
        choices=["validate", "init"],
        help="Command to execute",
    )
    parser.add_argument(
        "--contract",
        required=True,
        help="Path to contract YAML file",
    )
    parser.add_argument(
        "--data",
        help="Path to data file (CSV, Parquet, JSON)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "parquet", "jsonl", "auto"],
        default="auto",
        help="Data format (default: auto-detect)",
    )
    parser.add_argument(
        "--output-dir",
        default="./reports",
        help="Directory for JSON report output",
    )

    args = parser.parse_args()

    if args.command == "validate":
        return validate_command(args)
    elif args.command == "init":
        return init_command(args)

    return 0


def validate_command(args) -> int:
    """Execute validation command."""
    if not args.data:
        print("ERROR: --data is required for validate command")
        return 1

    try:
        # Load contract
        contract = Contract.from_yaml(args.contract)

        # Check version compatibility
        tool_version = "0.2.0"  # Updated to support v2.0
        is_compatible, compat_msg = check_tool_compatibility(
            tool_version, contract.version
        )
        compatibility_warnings = []
        if not is_compatible:
            print(f"ERROR: {compat_msg}")
            return 1
        
        # Load data
        format_arg = None if args.format == "auto" else args.format
        datasource = DataSource(args.data, format=format_arg)
        df = datasource.load()

        # Run validators
        schema_validator = SchemaValidator(contract, df)
        schema_pass, schema_errors = schema_validator.validate()

        quality_validator = QualityValidator(contract, df)
        quality_pass, quality_errors = quality_validator.validate()

        dist_validator = DistributionValidator(contract, df)
        dist_pass, dist_warnings = dist_validator.validate()

        # Collect all errors
        all_errors = []
        for err in schema_errors:
            severity = "ERROR" if err.startswith("ERROR") else "WARN"
            msg = err.replace("ERROR: ", "").replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="SCHEMA", field="", message=msg, severity=severity)
            )

        for err in quality_errors:
            severity = "ERROR" if err.startswith("ERROR") else "WARN"
            msg = err.replace("ERROR: ", "").replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="QUALITY", field="", message=msg, severity=severity)
            )

        for warn in dist_warnings:
            msg = warn.replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="DISTRIBUTION", field="", message=msg, severity="WARN")
            )

        # Create report
        error_count = sum(1 for e in all_errors if e.severity == "ERROR")
        warning_count = sum(1 for e in all_errors if e.severity == "WARN")
        passed = error_count == 0

        report = ValidationReport(
            passed=passed,
            contract_name=contract.name,
            contract_version=contract.version,
            dataset_name=contract.dataset.name,
            timestamp=datetime.now().isoformat(),
            tool_version=tool_version,
            error_count=error_count,
            warning_count=warning_count,
            errors=all_errors,
            compatibility_warnings=compatibility_warnings,
        )

        # Output report
        report.print_summary()
        json_path = report.save_json(args.output_dir)
        print(f"JSON report saved to: {json_path}")

        return 0 if passed else 1

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def init_command(args) -> int:
    """Execute init command (infer contract from data)."""
    if not args.data:
        print("ERROR: --data is required for init command")
        return 1

    try:
        format_arg = None if args.format == "auto" else args.format
        datasource = DataSource(args.data, format=format_arg)
        schema = datasource.infer_schema()

        print("\nInferred schema from data:")
        print("contract:")
        print("  name: my_contract")
        print("  version: 1.0.0")
        print("dataset:")
        print(f"  name: {Path(args.data).stem}")
        print("fields:")
        for col_name, col_type in schema.items():
            print(f"  - name: {col_name}")
            print(f"    type: {col_type}")
            print(f"    required: false")
            print(f"    rules: {{}}")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
