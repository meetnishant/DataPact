import pytest
from fastapi.testclient import TestClient
from datapact.reporting_dashboard import app, DashboardServer

def test_dashboard_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_dashboard_metrics_and_errors():
    client = TestClient(app)
    # Push some metrics and errors
    DashboardServer.push_metrics({"timestamp": "2026-02-24T12:00:00", "contract": "c1", "dataset": "d1", "passed": True, "error_count": 0, "warning_count": 1})
    DashboardServer.push_error({"timestamp": "2026-02-24T12:00:00", "contract": "c1", "dataset": "d1", "field": "f1", "message": "msg", "severity": "ERROR"})
    metrics = client.get("/metrics").json()
    errors = client.get("/errors").json()
    assert isinstance(metrics, list)
    assert isinstance(errors, list)
    assert metrics[-1]["contract"] == "c1"
    assert errors[-1]["field"] == "f1"

def test_dashboard_index_serves_html():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<html" in resp.text.lower()
