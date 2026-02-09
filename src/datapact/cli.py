"""
Command-line interface for data contract validation.
Provides 'validate' and 'init' commands for working with data contracts.
"""


# Standard library imports
import argparse  # For parsing CLI arguments
import sys  # For exit codes and script control
from pathlib import Path  # For file path manipulations
from datetime import datetime  # For timestamping reports


# Project imports
from datapact.contracts import Contract  # Contract model and parsing
from datapact.datasource import DataSource  # Data loading and schema inference
from datapact.validators import (
    SchemaValidator,  # Validates schema (columns, types, required)
    QualityValidator,  # Validates quality rules (nulls, unique, etc.)
    DistributionValidator,  # Validates distribution/drift rules
)
from datapact.reporting import ValidationReport, ErrorRecord  # Reporting utilities
from datapact.versioning import check_tool_compatibility  # Version compatibility check



def main() -> int:
    """
    Main CLI entry point. Parses arguments and dispatches to the appropriate command.
    Returns exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Validate datasets against data contracts"
    )
    # Add subcommands and arguments
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

    # Dispatch to the correct command handler
    if args.command == "validate":
        return validate_command(args)
    elif args.command == "init":
        return init_command(args)

    return 0



def validate_command(args) -> int:
    """
    Execute the 'validate' command: validate a dataset against a contract.
    Returns exit code 0 if validation passes, 1 if errors are found or on failure.
    """
    if not args.data:
        print("ERROR: --data is required for validate command")
        return 1

    try:
        # Load contract from YAML file (includes version checks/migration)
        contract = Contract.from_yaml(args.contract)

        # Check contract version compatibility with tool version
        tool_version = "0.2.0"  # Update as needed for tool releases
        is_compatible, compat_msg = check_tool_compatibility(
            tool_version, contract.version
        )
        compatibility_warnings = []
        if not is_compatible:
            print(f"ERROR: {compat_msg}")
            return 1

        # Load data file into DataFrame (auto-detect or use specified format)
        format_arg = None if args.format == "auto" else args.format
        datasource = DataSource(args.data, format=format_arg)
        df = datasource.load()

        # Run schema validation (blocking: must pass to continue)
        schema_validator = SchemaValidator(contract, df)
        schema_pass, schema_errors = schema_validator.validate()

        # Run quality validation (non-blocking: collect errors)
        quality_validator = QualityValidator(contract, df)
        quality_pass, quality_errors = quality_validator.validate()

        # Run distribution validation (non-blocking: collect warnings)
        dist_validator = DistributionValidator(contract, df)
        dist_pass, dist_warnings = dist_validator.validate()

        # Collect all errors and warnings as ErrorRecord objects
        all_errors = []
        for err in schema_errors:
            # Parse severity from message prefix
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
            # Distribution validator only returns warnings
            msg = warn.replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="DISTRIBUTION", field="", message=msg, severity="WARN")
            )

        # Count errors and warnings for reporting
        error_count = sum(1 for e in all_errors if e.severity == "ERROR")
        warning_count = sum(1 for e in all_errors if e.severity == "WARN")
        passed = error_count == 0

        # Create validation report object
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

        # Print summary to console and save JSON report
        report.print_summary()
        json_path = report.save_json(args.output_dir)
        print(f"JSON report saved to: {json_path}")

        # Exit code: 0 if passed, 1 if any errors
        return 0 if passed else 1

    except Exception as e:
        # Print any unexpected errors
        print(f"ERROR: {e}")
        return 1



def init_command(args) -> int:
    """
    Execute the 'init' command: infer a contract template from a data file.
    Prints a YAML contract template to stdout.
    Returns 0 on success, 1 on failure.
    """
    if not args.data:
        print("ERROR: --data is required for init command")
        return 1

    try:
        # Load data and infer schema
        format_arg = None if args.format == "auto" else args.format
        datasource = DataSource(args.data, format=format_arg)
        schema = datasource.infer_schema()

        # Print inferred contract YAML template to stdout
        print("\nInferred schema from data:")
        print("contract:")
        print("  name: my_contract")
        print("  version: 1.0.0")
        print("dataset:")
        print(f"  name: {Path(args.data).stem}")
        print("fields:")
        for col_name, col_type in schema.items():
            # Each field with inferred type, not required by default, empty rules
            print(f"  - name: {col_name}")
            print(f"    type: {col_type}")
            print("    required: false")
            print("    rules: {}")

        return 0

    except Exception as e:
        # Print any unexpected errors
        print(f"ERROR: {e}")
        return 1



# Entry point for CLI usage
if __name__ == "__main__":
    sys.exit(main())
