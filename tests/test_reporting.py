from datetime import datetime
from unittest import mock

from datapact.reporting import (
    ErrorRecord,
    FileReportSink,
    ReportContext,
    StdoutReportSink,
    ValidationReport,
    WebhookReportSink,
    write_report_sinks,
)
from urllib.error import URLError


def _sample_report() -> ValidationReport:
    return ValidationReport(
        passed=True,
        contract_name="sample",
        contract_version="2.0.0",
        dataset_name="demo",
        timestamp=datetime.now().isoformat(),
        tool_version="0.2.0",
        error_count=0,
        warning_count=0,
        errors=[
            ErrorRecord(
                code="QUALITY",
                field="",
                message="WARN: example",
                severity="WARN",
            )
        ],
        compatibility_warnings=[],
    )


def test_file_report_sink_writes_json(tmp_path):
    report = _sample_report()
    sink = FileReportSink(str(tmp_path))
    messages = write_report_sinks(
        report, [sink], ReportContext(output_dir=str(tmp_path))
    )

    assert len(messages) == 1
    assert messages[0].startswith("JSON report saved to: ")


def test_stdout_report_sink_prints_json(capsys):
    report = _sample_report()
    sink = StdoutReportSink()
    messages = write_report_sinks(report, [sink])

    captured = capsys.readouterr()
    assert '"contract"' in captured.out
    assert messages == ["Report JSON printed to stdout"]


def test_webhook_report_sink_posts_json():
    report = _sample_report()
    sink = WebhookReportSink("https://example.test/hook", headers={"X-Test": "1"})

    mock_response = mock.MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.__enter__.return_value = mock_response

    with mock.patch("urllib.request.urlopen", return_value=mock_response) as mocked:
        messages = write_report_sinks(report, [sink])

    assert messages == ["Webhook report sent (status 200)"]
    assert mocked.call_count == 1


def test_webhook_report_sink_failure():
    report = _sample_report()
    sink = WebhookReportSink("https://example.test/hook")

    with mock.patch("urllib.request.urlopen", side_effect=URLError("down")):
        messages = write_report_sinks(report, [sink])

    assert any("Report sink 'webhook' failed" in msg for msg in messages)


def test_error_record_with_logical_path() -> None:
    """Test ErrorRecord with logical_path and actual_column fields."""
    err = ErrorRecord(
        code="QUALITY",
        field="user_id",
        message="Field has null values",
        severity="ERROR",
        logical_path="user.id",
        actual_column="user__id",
    )

    assert err.logical_path == "user.id"
    assert err.actual_column == "user__id"


def test_error_record_to_dict_includes_lineage() -> None:
    """Test that to_dict includes lineage information."""
    report = ValidationReport(
        passed=False,
        contract_name="customer",
        contract_version="2.0.0",
        dataset_name="input",
        timestamp=datetime.now().isoformat(),
        tool_version="0.2.0",
        error_count=1,
        warning_count=0,
        errors=[
            ErrorRecord(
                code="QUALITY",
                field="user_id",
                message="Field has null values",
                severity="ERROR",
                logical_path="user.id",
                actual_column="user__id",
            )
        ],
    )

    report_dict = report.to_dict()
    err_dict = report_dict["errors"][0]

    assert err_dict["logical_path"] == "user.id"
    assert err_dict["actual_column"] == "user__id"


def test_print_summary_with_flattened_column(capsys) -> None:
    """Test that print_summary shows flattened column information."""
    report = ValidationReport(
        passed=False,
        contract_name="customer",
        contract_version="2.0.0",
        dataset_name="input",
        timestamp=datetime.now().isoformat(),
        tool_version="0.2.0",
        error_count=1,
        warning_count=0,
        errors=[
            ErrorRecord(
                code="SCHEMA",
                field="user_id",
                message="Required field missing",
                severity="ERROR",
                logical_path="user.id",
                actual_column="user__id",
            )
        ],
    )

    report.print_summary()
    captured = capsys.readouterr()

    # Verify lineage info is shown
    assert "path: user.id" in captured.out
    assert "column: user__id" in captured.out


def test_print_summary_without_lineage(capsys) -> None:
    """Test that print_summary works without lineage fields."""
    report = ValidationReport(
        passed=False,
        contract_name="customer",
        contract_version="2.0.0",
        dataset_name="input",
        timestamp=datetime.now().isoformat(),
        tool_version="0.2.0",
        error_count=1,
        warning_count=0,
        errors=[
            ErrorRecord(
                code="QUALITY",
                field="email",
                message="Regex validation failed",
                severity="ERROR",
            )
        ],
    )

    report.print_summary()
    captured = capsys.readouterr()

    # Verify field is shown without extra lineage info
    assert "[ERROR] email:" in captured.out
    assert "path:" not in captured.out
