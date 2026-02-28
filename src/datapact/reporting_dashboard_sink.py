from .reporting_dashboard import DashboardServer
from .reporting import ReportSink, ValidationReport, ReportContext
from typing import Optional

class DashboardReportSink(ReportSink):
    """
    Pushes metrics and errors to the FastAPI dashboard server in real time.
    """
    name = "dashboard"

    def __init__(self, host: str = "127.0.0.1", port: int = 8088):
        self.server = DashboardServer(host=host, port=port)
        self.started = False

    def start(self):
        if not self.started:
            self.server.start()
            self.started = True

    def write(self, report: ValidationReport, context: ReportContext) -> Optional[str]:
        # Push summary metrics and errors to dashboard
        metrics = {
            "timestamp": report.timestamp,
            "contract": report.contract_name,
            "dataset": report.dataset_name,
            "passed": report.passed,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
        }
        DashboardServer.push_metrics(metrics)
        for err in report.errors:
            DashboardServer.push_error({
                "timestamp": report.timestamp,
                "contract": report.contract_name,
                "dataset": report.dataset_name,
                "field": err.field,
                "message": err.message,
                "severity": err.severity,
            })
        return f"Dashboard updated at http://{self.server.host}:{self.server.port}"
