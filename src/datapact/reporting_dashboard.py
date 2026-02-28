"""
FastAPI server for real-time streaming metrics dashboard in DataPact/StreamPact.
Exposes REST endpoints for current metrics, errors, and health.
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import threading


from fastapi.responses import FileResponse
import os

app = FastAPI()

# Allow CORS for local dev dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory store for metrics and errors (windowed)
metrics_store: List[Dict[str, Any]] = []
errors_store: List[Dict[str, Any]] = []

# Serve the dashboard static HTML at root
@app.get("/")
def dashboard_index():
    static_path = os.path.join(os.path.dirname(__file__), "dashboard_static", "index.html")
    return FileResponse(static_path, media_type="text/html")

@app.get("/metrics")
def get_metrics():
    """Return the latest N window metrics."""
    return JSONResponse(metrics_store[-20:])

@app.get("/errors")
def get_errors():
    """Return the latest N error events."""
    return JSONResponse(errors_store[-50:])

@app.get("/health")
def health():
    return {"status": "ok"}

# Optional: WebSocket for live updates (future extension)
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         # Example: send latest metrics/errors every second
#         await websocket.send_json({
#             "metrics": metrics_store[-1] if metrics_store else {},
#             "errors": errors_store[-1] if errors_store else {},
#         })
#         await asyncio.sleep(1)

# Threaded server runner for integration with DataPact CLI
class DashboardServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8088):
        self.host = host
        self.port = port
        self.thread = None

    def start(self):
        import uvicorn
        def run():
            uvicorn.run(app, host=self.host, port=self.port, log_level="warning")
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        # Not implemented: for demo, rely on process exit
        pass

    @staticmethod
    def push_metrics(metrics: dict):
        metrics_store.append(metrics)
        if len(metrics_store) > 100:
            del metrics_store[:len(metrics_store)-100]

    @staticmethod
    def push_error(error: dict):
        errors_store.append(error)
        if len(errors_store) > 200:
            del errors_store[:len(errors_store)-200]
