"""
Command-line interface for data contract validation.
Provides 'validate' and 'init' commands for working with data contracts.
"""

# Standard library imports
import argparse  # For parsing CLI arguments
import sys  # For exit codes and script control
from pathlib import Path  # For file path manipulations
from datetime import datetime  # For timestamping reports
from typing import Any, Dict, List, Optional, Tuple

import yaml


# Project imports
from datapact.contracts import Contract  # Contract model and parsing
from datapact.datasource import (
    DataSource,
    DatabaseSource,
    DatabaseConfig,
)  # Data loading and schema inference
from datapact.validators import (
    SchemaValidator,  # Validates schema (columns, types, required)
    QualityValidator,  # Validates quality rules (nulls, unique, etc.)
    DistributionValidator,  # Validates distribution/drift rules
    SLAValidator,  # Validates SLA checks (row count thresholds)
    CustomRuleValidator,  # Validates custom plugin rules
)
from datapact.validators.quality_validator import ChunkedQualityValidator
from datapact.validators.distribution_validator import DistributionAccumulator
from datapact.reporting import (
    ValidationReport,
    ErrorRecord,
    FileReportSink,
    StdoutReportSink,
    WebhookReportSink,
    ReportContext,
    write_report_sinks,
)
from datapact.providers import DataPactProvider, OdcsProvider
from datapact.providers.base import ContractProvider
from datapact.normalization import NormalizationConfig, normalize_dataframe
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
        "--contract-format",
        choices=["auto", "datapact", "odcs"],
        default="auto",
        help="Contract format (default: auto-detect)",
    )
    parser.add_argument(
        "--odcs-object",
        help="ODCS schema object name or id to validate",
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
        "--db-type",
        choices=["postgres", "mysql", "sqlite"],
        help="Database type for DB sources",
    )
    parser.add_argument(
        "--db-host",
        help="Database host",
    )
    parser.add_argument(
        "--db-port",
        type=int,
        help="Database port",
    )
    parser.add_argument(
        "--db-user",
        help="Database user",
    )
    parser.add_argument(
        "--db-password",
        help="Database password",
    )
    parser.add_argument(
        "--db-name",
        help="Database name",
    )
    parser.add_argument(
        "--db-table",
        help="Database table to read",
    )
    parser.add_argument(
        "--db-query",
        help="SQL query to read (overrides --db-table)",
    )
    parser.add_argument(
        "--db-path",
        help="SQLite database file path",
    )
    parser.add_argument(
        "--db-connect-timeout",
        type=int,
        default=10,
        help="DB connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--db-chunksize",
        type=int,
        help="Chunk size for DB streaming validation",
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
        "--report-sink",
        action="append",
        default=None,
        help="Report sink (file, stdout, webhook). Repeatable.",
    )
    parser.add_argument(
        "--report-webhook-url",
        help="Webhook URL for report sink 'webhook'",
    )
    parser.add_argument(
        "--report-webhook-header",
        action="append",
        default=[],
        help="Webhook header (format: Key: Value). Repeatable.",
    )
    parser.add_argument(
        "--report-webhook-timeout",
        type=int,
        default=5,
        help="Webhook timeout in seconds (default: 5)",
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

    if not args.data and not _using_db(args):
        print("ERROR: --data is required for validate command")
        return 1

    try:
        contract_data = yaml.safe_load(Path(args.contract).read_text())
        tool_version = "0.2.0"  # Update as needed for tool releases
        compatibility_warnings: List[str] = []
        odcs_metadata = None

        provider = _resolve_contract_provider(
            args.contract_format,
            contract_data,
            args.odcs_object,
        )
        contract = provider.load_from_dict(contract_data)

        if isinstance(provider, OdcsProvider):
            compatibility_warnings.extend(provider.odcs_warnings)
            odcs_metadata = provider.odcs_metadata
        else:
            # Check contract version compatibility with tool version
            is_compatible, compat_msg = check_tool_compatibility(
                tool_version, contract.version
            )
            if not is_compatible:
                print(f"ERROR: {compat_msg}")
                return 1

            normalization_config = _build_normalization_config(contract)

        # Load data file or database source into DataFrame
        datasource = _build_datasource(args)

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
                    normalization_config,
                )
            )
            custom_errors = _validate_custom_rules_streaming(
                contract,
                datasource,
                args,
                normalization_config,
            )
        else:
            df = datasource.load()
            df = normalize_dataframe(df, normalization_config)

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
            odcs_metadata=odcs_metadata,
            odcs_warnings=compatibility_warnings if odcs_metadata else None,
        )

        # Print summary to console and write report sinks
        report.print_summary()
        webhook_headers = _parse_webhook_headers(args.report_webhook_header)
        sinks = _build_report_sinks(args, webhook_headers)
        context = ReportContext(
            output_dir=args.output_dir,
            webhook_url=args.report_webhook_url,
            webhook_headers=webhook_headers,
            webhook_timeout=args.report_webhook_timeout,
        )
        for message in write_report_sinks(report, sinks, context):
            print(message)

        # Exit code: 0 if passed, 1 if any errors
        return 0 if passed else 1

    except Exception as e:
        # Print any unexpected errors
        print(f"ERROR: {e}")
        return 1


def _resolve_contract_provider(
    contract_format: str,
    contract_data: Dict[str, Any],
    odcs_object: Optional[str],
) -> ContractProvider:
    providers = {
        "datapact": DataPactProvider(),
        "odcs": OdcsProvider(odcs_object=odcs_object),
    }

    if contract_format == "auto":
        for provider in (providers["odcs"], providers["datapact"]):
            if provider.can_load(contract_data):
                return provider
        raise ValueError(
            "Unable to detect contract format. Use --contract-format to set one."
        )

    provider = providers.get(contract_format)
    if provider is None:
        raise ValueError(f"Unsupported contract format '{contract_format}'.")
    if not provider.can_load(contract_data):
        raise ValueError(
            f"Contract format '{contract_format}' does not match the contract."
        )
    return provider


def init_command(args) -> int:
    """
    Execute the 'init' command: infer a contract template from a data file.
    Prints a YAML contract template to stdout.
    Returns 0 on success, 1 on failure.
    """
    if not args.data and not _using_db(args):
        print("ERROR: --data is required for init command")
        return 1

    try:
        # Load data and infer schema
        datasource = _build_datasource(args)
        schema = datasource.infer_schema()

        contract_name = args.contract_name or "my_contract"
        contract_data = {
            "contract": {
                "name": contract_name,
                "version": "1.0.0",
            },
            "dataset": {
                "name": _resolve_dataset_name(args),
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
    if not args.data and not _using_db(args):
        print("ERROR: --data is required for profile command")
        return 1

    try:
        datasource = _build_datasource(args)
        df = datasource.load()

        dataset_name = _resolve_dataset_name(args)
        contract_name = args.contract_name or f"{dataset_name}_profile"
        contract_data = profile_dataframe(
            df,
            dataset_name=dataset_name,
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


def _parse_webhook_headers(headers: List[str]) -> dict:
    parsed: dict = {}
    for header in headers:
        if ":" not in header:
            raise ValueError("Invalid webhook header. Use 'Key: Value'.")
        key, value = header.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _build_report_sinks(args, webhook_headers: dict) -> List:
    sinks = []
    sink_names = args.report_sink or ["file"]
    for raw in sink_names:
        name = raw.strip().lower()
        if name == "file":
            sinks.append(FileReportSink(args.output_dir))
        elif name == "stdout":
            sinks.append(StdoutReportSink())
        elif name == "webhook":
            if not args.report_webhook_url:
                raise ValueError("--report-webhook-url is required for webhook sink")
            sinks.append(
                WebhookReportSink(
                    args.report_webhook_url,
                    headers=webhook_headers,
                    timeout=args.report_webhook_timeout,
                )
            )
        else:
            raise ValueError("Invalid report sink. Use file, stdout, or webhook.")
    return sinks


def _use_streaming(args) -> bool:
    return any(
        value is not None
        for value in (
            args.chunksize,
            args.db_chunksize,
            args.sample_rows,
            args.sample_frac,
        )
    )


def _validate_streaming(
    contract: Contract,
    datasource,
    args,
    severity_overrides: dict,
    normalization_config: NormalizationConfig,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    if args.sample_rows is not None and args.sample_rows <= 0:
        raise ValueError("--sample-rows must be > 0")
    if args.sample_frac is not None and not (0 < args.sample_frac <= 1):
        raise ValueError("--sample-frac must be between 0 and 1")
    if args.sample_rows is not None and args.sample_frac is not None:
        raise ValueError("Specify only one of --sample-rows or --sample-frac")
    if isinstance(datasource, DataSource):
        if args.chunksize and datasource.format not in {"csv", "jsonl"}:
            raise ValueError("--chunksize is supported for CSV and JSONL only")

    chunksize = args.db_chunksize or args.chunksize or 10000
    schema_errors: set = set()
    total_rows = 0
    sample_mode = args.sample_rows is not None or args.sample_frac is not None

    chunked_quality = ChunkedQualityValidator(contract, severity_overrides)
    dist_accumulator = DistributionAccumulator(contract)

    if isinstance(datasource, DataSource) and datasource.format in {"csv", "jsonl"}:
        for chunk in datasource.iter_chunks(chunksize):
            chunk = normalize_dataframe(chunk, normalization_config)
            total_rows += len(chunk)

            schema_validator = SchemaValidator(contract, chunk)
            _, chunk_schema_errors = schema_validator.validate()
            schema_errors.update(chunk_schema_errors)

            if not sample_mode:
                chunked_quality.process_chunk(chunk)
                dist_accumulator.process_chunk(chunk)
    elif isinstance(datasource, DataSource):
        df = datasource.load()
        df = normalize_dataframe(df, normalization_config)
        total_rows = len(df)
        schema_validator = SchemaValidator(contract, df)
        _, chunk_schema_errors = schema_validator.validate()
        schema_errors.update(chunk_schema_errors)

        if not sample_mode:
            chunked_quality.process_chunk(df)
            dist_accumulator.process_chunk(df)
    else:
        for chunk in datasource.iter_chunks(chunksize):
            chunk = normalize_dataframe(chunk, normalization_config)
            total_rows += len(chunk)

            schema_validator = SchemaValidator(contract, chunk)
            _, chunk_schema_errors = schema_validator.validate()
            schema_errors.update(chunk_schema_errors)

            if not sample_mode:
                chunked_quality.process_chunk(chunk)
                dist_accumulator.process_chunk(chunk)

    quality_errors: List[str]
    dist_warnings: List[str]

    if sample_mode:
        sample_df = datasource.sample_dataframe(
            sample_rows=args.sample_rows,
            sample_frac=args.sample_frac,
            seed=args.sample_seed,
            chunksize=chunksize,
        )
        sample_df = normalize_dataframe(sample_df, normalization_config)
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
            if isinstance(datasource, DataSource):
                if datasource.format in {"csv", "jsonl"}:
                    dist_warnings += dist_accumulator.count_outliers(
                        datasource.iter_chunks(chunksize)
                    )
            else:
                dist_warnings += dist_accumulator.count_outliers(
                    datasource.iter_chunks(chunksize)
                )

    sla_errors = _evaluate_sla(contract, total_rows)

    return list(schema_errors), quality_errors, dist_warnings, sla_errors


def _validate_custom_rules_streaming(
    contract: Contract,
    datasource,
    args,
    normalization_config: NormalizationConfig,
) -> List[str]:
    if not args.plugin:
        return []

    if args.sample_rows is None and args.sample_frac is None:
        return ["WARN: Custom rules skipped in streaming mode without sampling"]

    sample_df = datasource.sample_dataframe(
        sample_rows=args.sample_rows,
        sample_frac=args.sample_frac,
        seed=args.sample_seed,
        chunksize=args.chunksize or 10000,
    )
    sample_df = normalize_dataframe(sample_df, normalization_config)
    validator = CustomRuleValidator(contract, sample_df, args.plugin)
    _, errors = validator.validate()
    return errors


def _build_normalization_config(contract: Contract) -> NormalizationConfig:
    if contract.flatten.enabled:
        return NormalizationConfig(
            mode="flatten",
            flatten_separator=contract.flatten.separator,
        )
    return NormalizationConfig()


def _using_db(args) -> bool:
    return args.db_type is not None


def _build_datasource(args):
    if _using_db(args):
        config = _build_db_config(args)
        return DatabaseSource(config)

    format_arg = None if args.format == "auto" else args.format
    return DataSource(args.data, format=format_arg)


def _build_db_config(args) -> DatabaseConfig:
    if args.db_type is None:
        raise ValueError("--db-type is required for database sources")

    db_type = args.db_type
    if db_type == "sqlite":
        if not args.db_path:
            raise ValueError("--db-path is required for sqlite")
    else:
        if not args.db_host:
            raise ValueError("--db-host is required for database sources")
        if not args.db_user:
            raise ValueError("--db-user is required for database sources")
        if not args.db_name:
            raise ValueError("--db-name is required for database sources")

    if not args.db_query and not args.db_table:
        raise ValueError("--db-table or --db-query is required for database sources")

    default_port = None
    if db_type == "postgres":
        default_port = 5432
    if db_type == "mysql":
        default_port = 3306

    return DatabaseConfig(
        db_type=db_type,
        host=args.db_host,
        port=args.db_port or default_port,
        user=args.db_user,
        password=args.db_password,
        name=args.db_name,
        table=args.db_table,
        query=args.db_query,
        path=args.db_path,
        connect_timeout=args.db_connect_timeout,
    )


def _resolve_dataset_name(args) -> str:
    if _using_db(args):
        return args.db_table or "query"
    return Path(args.data).stem


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
