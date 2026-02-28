# DataPact Streaming Metrics Dashboard

DataPact now supports a real-time streaming metrics dashboard for streaming validation jobs.

## How to Use

1. **Install dashboard dependencies:**
   ```bash
   pip install fastapi uvicorn
   ```
   (Or add to your `pyproject.toml`/`requirements.txt`)

2. **Run validation with dashboard enabled:**
   ```bash
   datapact validate --dashboard
   # or for streaming
   datapact stream-validate --dashboard
   ```
   - The dashboard server will start automatically on http://localhost:8088 (default).
   - Use `--dashboard-port` to change the port.

3. **Open the dashboard:**
   - Visit [http://localhost:8088/](http://localhost:8088/) in your browser.
   - See live metrics, error counts, and recent error details as validation runs.

## Features
- Live metrics for each validation window (row rate, error/warning counts, pass/fail)
- Recent error log with field, severity, and message
- Auto-refreshes every 2 seconds
- Works with both batch and streaming validation

## Configuration
- `--dashboard`: Enable the dashboard server and sink
- `--dashboard-port`: Set the port (default: 8088)
- `--report-sink dashboard`: Add dashboard sink explicitly (optional)

## Implementation Notes
- The dashboard is served by a FastAPI server embedded in DataPact.
- Metrics/errors are stored in memory for the current process.
- The dashboard is optional and does not affect file/webhook sinks.

## Example
```bash
datapact stream-validate --contract my_stream_contract.yaml --bootstrap-servers localhost:9092 --topic mytopic --group-id mygroup --dashboard
```

## Troubleshooting
- If you see connection errors, ensure `fastapi` and `uvicorn` are installed in your environment.
- The dashboard only shows metrics/errors for the current validation run.
- For production, consider securing the dashboard endpoint.
