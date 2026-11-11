"""Unit tests for thread-safe request queue."""

from blender_addon.bridge.request_queue import QueuedRequest, RequestQueue


def test_queue_enqueue_and_get():
    q = RequestQueue()
    req = QueuedRequest(
        request_id="req_001",
        operation="object.create_primitive",
        arguments={"primitive_type": "CUBE"},
    )
    q.enqueue(req)

    retrieved = q.get_pending(block=False)
    assert retrieved is not None
    assert retrieved.request_id == "req_001"
    assert retrieved.operation == "object.create_primitive"
    assert retrieved.status == "queued"

    retrieved.mark_completed({"name": "Cube"})
    assert retrieved.status == "completed"
    assert retrieved.result == {"name": "Cube"}
    assert retrieved.completion_event.is_set()


def test_queue_mark_failed():
    req = QueuedRequest(
        request_id="req_002",
        operation="bad.op",
        arguments={},
    )
    req.mark_failed("UNSUPPORTED_OPERATION", "Not supported")
    assert req.status == "failed"
    assert req.error == {
        "code": "UNSUPPORTED_OPERATION",
        "message": "Not supported",
        "details": {},
    }
    assert req.completion_event.is_set()
