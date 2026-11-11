"""Thread-safe request queue and task models for Blender main-thread dispatch."""

import queue
import threading
import time
from typing import Any, Dict, Optional


class QueuedRequest:
    def __init__(
        self,
        request_id: str,
        operation: str,
        arguments: Dict[str, Any],
        timeout_seconds: float = 30.0,
    ):
        self.request_id = request_id
        self.operation = operation
        self.arguments = arguments
        self.timeout_seconds = timeout_seconds
        self.created_at = time.time()
        self.status = "queued"
        self.completion_event = threading.Event()
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[Dict[str, Any]] = None

    def mark_completed(self, result: Dict[str, Any]) -> None:
        self.status = "completed"
        self.result = result
        self.error = None
        self.completion_event.set()

    def mark_failed(self, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.status = "failed"
        self.result = None
        self.error = {
            "code": code,
            "message": message,
            "details": details or {},
        }
        self.completion_event.set()


class RequestQueue:
    def __init__(self):
        self._queue: queue.Queue[QueuedRequest] = queue.Queue()
        self._requests: Dict[str, QueuedRequest] = {}
        self._lock = threading.Lock()

    def enqueue(self, req: QueuedRequest) -> None:
        with self._lock:
            self._requests[req.request_id] = req
        self._queue.put(req)

    def get_pending(self, block: bool = False, timeout: Optional[float] = None) -> Optional[QueuedRequest]:
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def get_request(self, request_id: str) -> Optional[QueuedRequest]:
        with self._lock:
            return self._requests.get(request_id)

    def clear(self) -> None:
        with self._lock:
            while not self._queue.empty():
                try:
                    item = self._queue.get_nowait()
                    item.mark_failed("TASK_CANCELLED", "Queue cleared on shutdown")
                except queue.Empty:
                    break
            self._requests.clear()


# Global request queue instance
global_queue = RequestQueue()
