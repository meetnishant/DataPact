"""
Command-line interface for data contract validation.
Provides 'validate' and 'init' commands for working with data contracts.
"""


# Standard library imports
import argparse  # For parsing CLI arguments
import sys  # For exit codes and script control
from pathlib import Path  # For file path manipulations
from datetime import datetime  # For timestamping reports

import yaml


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
from datapact.profiling import profile_dataframe  # Profiling utilities



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
        choices=["validate", "init", "profile"],
        help="Command to execute",
    )
    parser.add_argument(
        "--contract",
        help="Path to contract YAML file",
    )
    parser.add_argument(
        "--contract-name",
        help="Contract name for init/profile output",
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
    parser.add_argument(
        "--severity-override",
        action="append",
        default=[],
        help="Override rule severity (format: field.rule=warn)",
    )
    parser.add_argument(
        "--max-enum-size",
        type=int,
        default=20,
        help="Max enum size for profiling",
    )
    parser.add_argument(
        "--max-enum-ratio",
        type=float,
        default=0.2,
        help="Max enum ratio for profiling",
    )
    parser.add_argument(
        "--unique-threshold",
        type=float,
        default=0.99,
        help="Unique threshold for profiling",
    )
    parser.add_argument(
        "--null-ratio-buffer",
        type=float,
        default=0.01,
        help="Null ratio buffer for profiling",
    )
    parser.add_argument(
        "--range-buffer-pct",
        type=float,
        default=0.05,
        help="Range buffer percent for profiling",
    )
    parser.add_argument(
        "--max-drift-pct",
        type=float,
        default=10.0,
        help="Max drift percent for profiling",
    )
    parser.add_argument(
        "--max-z-score",
        type=float,
        default=3.0,
        help="Max z-score for profiling",
    )
    parser.add_argument(
        "--no-distribution",
        action="store_true",
        help="Disable distribution profiling",
    )
    parser.add_argument(
        "--no-date-regex",
        action="store_true",
        help="Disable date regex profiling",
    )

    args = parser.parse_args()

    # Dispatch to the correct command handler
    if args.command == "validate":
        return validate_command(args)
    elif args.command == "init":
        return init_command(args)
    elif args.command == "profile":
        return profile_command(args)

    return 0



def validate_command(args) -> int:
    """
    Execute the 'validate' command: validate a dataset against a contract.
    Returns exit code 0 if validation passes, 1 if errors are found or on failure.
    """
    if not args.contract:
        print("ERROR: --contract is required for validate command")
        return 1

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

        severity_overrides = _parse_severity_overrides(args.severity_override)

        # Run quality validation (non-blocking: collect errors)
        quality_validator = QualityValidator(
            contract,
            df,
            severity_overrides=severity_overrides,
        )
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

        contract_name = args.contract_name or "my_contract"
        contract_data = {
            "contract": {
                "name": contract_name,
                "version": "1.0.0",
            },
            "dataset": {
                "name": Path(args.data).stem,
            },
            "fields": [],
        }

        for col_name, col_type in schema.items():
            contract_data["fields"].append(
                {
                    "name": col_name,
                    "type": col_type,
                    "required": False,
                    "rules": {},
                }
            )

        _write_contract_yaml(contract_data, args.contract)

        return 0

    except Exception as e:
        # Print any unexpected errors
        print(f"ERROR: {e}")
        return 1


def profile_command(args) -> int:
    """
    Execute the 'profile' command: infer rules from a data file.
    Writes YAML to stdout or to --contract path if provided.
    Returns 0 on success, 1 on failure.
    """
    if not args.data:
        print("ERROR: --data is required for profile command")
        return 1

    try:
        format_arg = None if args.format == "auto" else args.format
        datasource = DataSource(args.data, format=format_arg)
        df = datasource.load()

        contract_name = args.contract_name or f"{Path(args.data).stem}_profile"
        contract_data = profile_dataframe(
            df,
            dataset_name=Path(args.data).stem,
            contract_name=contract_name,
            max_enum_size=args.max_enum_size,
            max_enum_ratio=args.max_enum_ratio,
            unique_threshold=args.unique_threshold,
            null_ratio_buffer=args.null_ratio_buffer,
            range_buffer_pct=args.range_buffer_pct,
            include_distribution=not args.no_distribution,
            max_drift_pct=args.max_drift_pct,
            max_z_score=args.max_z_score,
            infer_date_regex=not args.no_date_regex,
        )

        _write_contract_yaml(contract_data, args.contract)
        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def _write_contract_yaml(contract_data, output_path: str) -> None:
    yaml_text = yaml.safe_dump(contract_data, sort_keys=False)
    if output_path:
        Path(output_path).write_text(yaml_text)
        print(f"Contract saved to: {output_path}")
        return

    print(yaml_text)


def _parse_severity_overrides(overrides) -> dict:
    parsed = {}
    for item in overrides:
        if "=" not in item or "." not in item.split("=")[0]:
            raise ValueError(
                "Invalid severity override. Use field.rule=warn or field.rule=error"
            )
        left, severity = item.split("=", 1)
        field_name, rule_name = left.split(".", 1)
        parsed[f"{field_name}.{rule_name}".lower()] = severity
    return parsed



# Entry point for CLI usage
if __name__ == "__main__":
    sys.exit(main())
