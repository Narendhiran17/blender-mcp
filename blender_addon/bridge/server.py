"""Localhost HTTP bridge server running inside Blender."""

import http.server
import json
import logging
import threading
import uuid
from typing import Any, Dict, Optional, Tuple

from .auth import get_active_token, validate_token
from .request_queue import QueuedRequest, global_queue

logger = logging.getLogger("blender_ai_control.bridge")

_SERVER_INSTANCE: Optional["BridgeServer"] = None
_SERVER_THREAD: Optional[threading.Thread] = None


class BridgeRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for local Blender bridge."""

    def log_message(self, format: str, *args: Any) -> None:
        logger.debug(f"{self.address_string()} - {format % args}")

    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.end_headers()
        self.wfile.write(payload)

    def _extract_token(self) -> Optional[str]:
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        custom_header = self.headers.get("X-Blender-Bridge-Token", "")
        if custom_header:
            return custom_header.strip()
        return None

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Blender-Bridge-Token")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0].rstrip("/")

        if path == "/health":
            self._send_json_response(200, {
                "status": "ok",
                "blender_connected": True,
                "protocol_version": "1",
            })
            return

        if path == "/status":
            token = self._extract_token()
            if not validate_token(token):
                self._send_json_response(401, {
                    "protocol_version": "1",
                    "status": "failed",
                    "error": {
                        "code": "AUTHENTICATION_FAILED",
                        "message": "Missing or invalid authentication token",
                    },
                })
                return

            req = QueuedRequest(
                request_id=f"status_{uuid.uuid4().hex[:8]}",
                operation="system.status",
                arguments={},
                timeout_seconds=5.0,
            )
            global_queue.enqueue(req)
            done = req.completion_event.wait(timeout=5.0)
            if not done:
                self._send_json_response(504, {
                    "protocol_version": "1",
                    "request_id": req.request_id,
                    "status": "failed",
                    "error": {
                        "code": "TASK_TIMEOUT",
                        "message": "Status operation timed out waiting for Blender main thread",
                    },
                })
                return

            self._send_json_response(200, {
                "protocol_version": "1",
                "request_id": req.request_id,
                "status": req.status,
                "result": req.result,
                "error": req.error,
            })
            return

        self._send_json_response(404, {
            "error": {"code": "NOT_FOUND", "message": f"Endpoint '{self.path}' not found"}
        })

    def do_POST(self) -> None:
        path = self.path.split("?")[0].rstrip("/")

        if path != "/execute":
            self._send_json_response(404, {
                "error": {"code": "NOT_FOUND", "message": f"Endpoint '{self.path}' not found"}
            })
            return

        token = self._extract_token()
        if not validate_token(token):
            self._send_json_response(401, {
                "protocol_version": "1",
                "request_id": "unknown",
                "status": "failed",
                "error": {
                    "code": "AUTHENTICATION_FAILED",
                    "message": "Missing or invalid authentication token",
                },
            })
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 10 * 1024 * 1024:
            self._send_json_response(413, {
                "error": {"code": "PAYLOAD_TOO_LARGE", "message": "Payload exceeds 10MB limit"}
            })
            return

        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            body = json.loads(raw_body)
        except Exception as exc:
            self._send_json_response(400, {
                "protocol_version": "1",
                "request_id": "unknown",
                "status": "failed",
                "error": {"code": "INVALID_ARGUMENT", "message": f"Invalid JSON payload: {exc}"},
            })
            return

        req_id = str(body.get("request_id") or f"req_{uuid.uuid4().hex[:8]}")
        operation = body.get("operation")
        if not operation or not isinstance(operation, str):
            self._send_json_response(400, {
                "protocol_version": "1",
                "request_id": req_id,
                "status": "failed",
                "error": {"code": "INVALID_ARGUMENT", "message": "Missing or invalid 'operation'"},
            })
            return

        args = body.get("arguments") or {}
        timeout_seconds = float(body.get("timeout_seconds") or 30.0)

        req = QueuedRequest(
            request_id=req_id,
            operation=operation,
            arguments=args,
            timeout_seconds=timeout_seconds,
        )
        global_queue.enqueue(req)

        done = req.completion_event.wait(timeout=timeout_seconds)
        if not done:
            req.mark_failed("TASK_TIMEOUT", f"Operation '{operation}' timed out after {timeout_seconds}s")
            self._send_json_response(504, {
                "protocol_version": "1",
                "request_id": req.request_id,
                "status": "failed",
                "result": None,
                "error": req.error,
            })
            return

        self._send_json_response(200, {
            "protocol_version": "1",
            "request_id": req.request_id,
            "status": req.status,
            "result": req.result,
            "error": req.error,
        })


class BridgeServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_bridge(host: str = "127.0.0.1", port: int = 8765, token: Optional[str] = None) -> Tuple[str, int]:
    global _SERVER_INSTANCE, _SERVER_THREAD

    if _SERVER_INSTANCE is not None:
        return _SERVER_INSTANCE.server_address

    from .auth import initialize_token
    initialize_token(token)

    server_address = (host, port)
    _SERVER_INSTANCE = BridgeServer(server_address, BridgeRequestHandler)

    _SERVER_THREAD = threading.Thread(
        target=_SERVER_INSTANCE.serve_forever,
        name="BlenderAIBridgeServerThread",
        daemon=True,
    )
    _SERVER_THREAD.start()

    logger.info(f"Blender AI Control Bridge server listening on http://{host}:{port}")
    return _SERVER_INSTANCE.server_address


def stop_bridge() -> None:
    global _SERVER_INSTANCE, _SERVER_THREAD

    if _SERVER_INSTANCE is not None:
        logger.info("Stopping Blender AI Control Bridge server...")
        _SERVER_INSTANCE.shutdown()
        _SERVER_INSTANCE.server_close()
        _SERVER_INSTANCE = None

    if _SERVER_THREAD is not None:
        _SERVER_THREAD.join(timeout=2.0)
        _SERVER_THREAD = None

    global_queue.clear()
    logger.info("Blender AI Control Bridge server stopped.")
