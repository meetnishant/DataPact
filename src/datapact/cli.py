"""
Command-line interface for data contract validation.
Provides 'validate' and 'init' commands for working with data contracts.
"""


# Standard library imports
import argparse  # For parsing CLI arguments
import sys  # For exit codes and script control
from pathlib import Path  # For file path manipulations
from datetime import datetime  # For timestamping reports
from typing import List, Tuple

import yaml


# Project imports
from datapact.contracts import Contract  # Contract model and parsing
from datapact.datasource import DataSource  # Data loading and schema inference
from datapact.validators import (
    SchemaValidator,  # Validates schema (columns, types, required)
    QualityValidator,  # Validates quality rules (nulls, unique, etc.)
    DistributionValidator,  # Validates distribution/drift rules
    SLAValidator,  # Validates SLA checks (row count thresholds)
    CustomRuleValidator,  # Validates custom plugin rules
)
from datapact.validators.quality_validator import ChunkedQualityValidator
from datapact.validators.distribution_validator import DistributionAccumulator
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
        "--chunksize",
        type=int,
        help="Chunk size for streaming validation (CSV/JSONL only)",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        help="Sample N rows for validation",
    )
    parser.add_argument(
        "--sample-frac",
        type=float,
        help="Sample fraction for validation",
    )
    parser.add_argument(
        "--sample-seed",
        type=int,
        help="Random seed for sampling",
    )
    parser.add_argument(
        "--severity-override",
        action="append",
        default=[],
        help="Override rule severity (format: field.rule=warn)",
    )
    parser.add_argument(
        "--plugin",
        action="append",
        default=[],
        help="Plugin module path for custom rules (repeatable)",
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

        severity_overrides = _parse_severity_overrides(args.severity_override)

        schema_errors: List[str]
        quality_errors: List[str]
        dist_warnings: List[str]
        sla_errors: List[str]

        custom_errors: List[str] = []

        if _use_streaming(args):
            schema_errors, quality_errors, dist_warnings, sla_errors = (
                _validate_streaming(
                    contract,
                    datasource,
                    args,
                    severity_overrides,
                )
            )
            custom_errors = _validate_custom_rules_streaming(
                contract,
                datasource,
                args,
            )
        else:
            df = datasource.load()

            # Run schema validation (blocking: must pass to continue)
            schema_validator = SchemaValidator(contract, df)
            _, schema_errors = schema_validator.validate()

            # Run quality validation (non-blocking: collect errors)
            quality_validator = QualityValidator(
                contract,
                df,
                severity_overrides=severity_overrides,
            )
            _, quality_errors = quality_validator.validate()

            # Run distribution validation (non-blocking: collect warnings)
            dist_validator = DistributionValidator(contract, df)
            _, dist_warnings = dist_validator.validate()

            # Run SLA validation (non-blocking: collect errors/warnings)
            sla_validator = SLAValidator(contract, df)
            _, sla_errors = sla_validator.validate()

            # Run custom rule validation (non-blocking: collect errors/warnings)
            custom_validator = CustomRuleValidator(
                contract,
                df,
                args.plugin,
            )
            _, custom_errors = custom_validator.validate()

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

        for err in sla_errors:
            severity = "ERROR" if err.startswith("ERROR") else "WARN"
            msg = err.replace("ERROR: ", "").replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="SLA", field="", message=msg, severity=severity)
            )

        for err in custom_errors:
            severity = "ERROR" if err.startswith("ERROR") else "WARN"
            msg = err.replace("ERROR: ", "").replace("WARN: ", "")
            all_errors.append(
                ErrorRecord(code="CUSTOM", field="", message=msg, severity=severity)
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


def _use_streaming(args) -> bool:
    return any(
        value is not None
        for value in (args.chunksize, args.sample_rows, args.sample_frac)
    )


def _validate_streaming(
    contract: Contract,
    datasource: DataSource,
    args,
    severity_overrides: dict,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    if args.sample_rows is not None and args.sample_rows <= 0:
        raise ValueError("--sample-rows must be > 0")
    if args.sample_frac is not None and not (0 < args.sample_frac <= 1):
        raise ValueError("--sample-frac must be between 0 and 1")
    if args.sample_rows is not None and args.sample_frac is not None:
        raise ValueError("Specify only one of --sample-rows or --sample-frac")
    if args.chunksize and datasource.format not in {"csv", "jsonl"}:
        raise ValueError("--chunksize is supported for CSV and JSONL only")

    chunksize = args.chunksize or 10000
    schema_errors: set = set()
    total_rows = 0
    sample_mode = args.sample_rows is not None or args.sample_frac is not None

    chunked_quality = ChunkedQualityValidator(contract, severity_overrides)
    dist_accumulator = DistributionAccumulator(contract)

    if datasource.format in {"csv", "jsonl"}:
        for chunk in datasource.iter_chunks(chunksize):
            total_rows += len(chunk)

            schema_validator = SchemaValidator(contract, chunk)
            _, chunk_schema_errors = schema_validator.validate()
            schema_errors.update(chunk_schema_errors)

            if not sample_mode:
                chunked_quality.process_chunk(chunk)
                dist_accumulator.process_chunk(chunk)
    else:
        df = datasource.load()
        total_rows = len(df)
        schema_validator = SchemaValidator(contract, df)
        _, chunk_schema_errors = schema_validator.validate()
        schema_errors.update(chunk_schema_errors)

        if not sample_mode:
            chunked_quality.process_chunk(df)
            dist_accumulator.process_chunk(df)

    quality_errors: List[str]
    dist_warnings: List[str]

    if sample_mode:
        sample_df = datasource.sample_dataframe(
            sample_rows=args.sample_rows,
            sample_frac=args.sample_frac,
            seed=args.sample_seed,
            chunksize=chunksize,
        )
        quality_validator = QualityValidator(
            contract,
            sample_df,
            severity_overrides=severity_overrides,
        )
        _, quality_errors = quality_validator.validate()

        dist_validator = DistributionValidator(contract, sample_df)
        _, dist_warnings = dist_validator.validate()
    else:
        quality_errors = chunked_quality.finalize()
        dist_warnings = dist_accumulator.finalize_drift()

        if dist_accumulator.needs_outlier_pass():
            if datasource.format in {"csv", "jsonl"}:
                dist_warnings += dist_accumulator.count_outliers(
                    datasource.iter_chunks(chunksize)
                )

    sla_errors = _evaluate_sla(contract, total_rows)

    return list(schema_errors), quality_errors, dist_warnings, sla_errors


def _validate_custom_rules_streaming(
    contract: Contract,
    datasource: DataSource,
    args,
) -> List[str]:
    if not args.plugin:
        return []

    if args.sample_rows is None and args.sample_frac is None:
        return [
            "WARN: Custom rules skipped in streaming mode without sampling"
        ]

    sample_df = datasource.sample_dataframe(
        sample_rows=args.sample_rows,
        sample_frac=args.sample_frac,
        seed=args.sample_seed,
        chunksize=args.chunksize or 10000,
    )
    validator = CustomRuleValidator(contract, sample_df, args.plugin)
    _, errors = validator.validate()
    return errors


def _evaluate_sla(contract: Contract, total_rows: int) -> List[str]:
    sla = contract.sla
    errors: List[str] = []

    if sla.min_rows is not None and total_rows < sla.min_rows:
        errors.append(
            f"{sla.min_rows_severity}: SLA min_rows={sla.min_rows} "
            f"violated (found {total_rows})"
        )

    if sla.max_rows is not None and total_rows > sla.max_rows:
        errors.append(
            f"{sla.max_rows_severity}: SLA max_rows={sla.max_rows} "
            f"violated (found {total_rows})"
        )

    return errors



# Entry point for CLI usage
if __name__ == "__main__":
    sys.exit(main())
