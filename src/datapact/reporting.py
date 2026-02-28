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
import urllib.request
import urllib.error
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
    logical_path: logical field path for nested/flattened fields (e.g., "user.id")
    actual_column: actual dataframe column name after normalization (e.g., "user__id")
    """

    code: str
    field: str
    message: str
    severity: str  # "ERROR" or "WARN"
    logical_path: Optional[str] = None
    actual_column: Optional[str] = None


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
    odcs_metadata: Optional[Dict[str, Any]] = None
    odcs_warnings: Optional[List[str]] = None

    def __post_init__(self):
        """
        Initialize compatibility warnings if not provided.
        """
        if self.compatibility_warnings is None:
            self.compatibility_warnings = []
        if self.odcs_warnings is None:
            self.odcs_warnings = []

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

        if self.odcs_metadata:
            result["odcs"] = self.odcs_metadata
        if self.odcs_warnings:
            result["odcs_warnings"] = self.odcs_warnings

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
        if self.odcs_warnings:
            print(f"  ODCS warnings: {len(self.odcs_warnings)}")

        if self.errors:
            print("\nDetails:")
            for err in self.errors:
                # Show logical path if available (for flattened fields)
                field_info = err.field
                if err.logical_path and err.logical_path != err.field:
                    field_info = f"{err.field} (path: {err.logical_path}"
                    if err.actual_column:
                        field_info += f", column: {err.actual_column}"
                    field_info += ")"
                elif err.actual_column and err.actual_column != err.field:
                    field_info = f"{err.field} (column: {err.actual_column})"
                print(f"  [{err.severity}] {field_info}: {err.message}")
        print(f"{'='*60}\n")


@dataclass
class ReportContext:
    """
    Context for report sinks (output paths, webhook config, etc.).
    """

    output_dir: str = "./reports"
    webhook_url: Optional[str] = None
    webhook_headers: Optional[Dict[str, str]] = None
    webhook_timeout: int = 5


class ReportSink:
    """
    Base class for report sinks.
    """

    name = "base"

    def write(self, report: ValidationReport, context: ReportContext) -> Optional[str]:
        raise NotImplementedError("ReportSink.write must be implemented")


class FileReportSink(ReportSink):
    """
    Write report JSON to a local file.
    """

    name = "file"

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def write(self, report: ValidationReport, context: ReportContext) -> Optional[str]:
        path = report.save_json(self.output_dir)
        return f"JSON report saved to: {path}"


class StdoutReportSink(ReportSink):
    """
    Print report JSON to stdout.
    """

    name = "stdout"

    def write(self, report: ValidationReport, context: ReportContext) -> Optional[str]:
        print(json.dumps(report.to_dict(), indent=2))
        return "Report JSON printed to stdout"


class WebhookReportSink(ReportSink):
    """
    Send report JSON to a webhook endpoint.
    """

    name = "webhook"

    def __init__(
        self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 5
    ):
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    def write(self, report: ValidationReport, context: ReportContext) -> Optional[str]:
        payload = json.dumps(report.to_dict()).encode("utf-8")
        headers = {"Content-Type": "application/json", **self.headers}
        request = urllib.request.Request(
            self.url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status = response.getcode()
            return f"Webhook report sent (status {status})"
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"Webhook endpoint returned HTTP {exc.code}: {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Webhook connection failed: {exc.reason}"
            ) from exc


def write_report_sinks(
    report: ValidationReport,
    sinks: List[ReportSink],
    context: Optional[ReportContext] = None,
) -> List[str]:
    """
    Write the report to configured sinks and return user-facing messages.
    """
    messages: List[str] = []
    context = context or ReportContext()

    for sink in sinks:
        try:
            result = sink.write(report, context)
            if result:
                messages.append(result)
        except Exception as exc:
            messages.append(f"WARN: Report sink '{sink.name}' failed: {exc}")

    return messages
