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
    messages = write_report_sinks(report, [sink], ReportContext(output_dir=str(tmp_path)))

    assert len(messages) == 1
    assert messages[0].startswith("JSON report saved to: ")


def test_stdout_report_sink_prints_json(capsys):
    report = _sample_report()
    sink = StdoutReportSink()
    messages = write_report_sinks(report, [sink])

    captured = capsys.readouterr()
    assert "\"contract\"" in captured.out
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
