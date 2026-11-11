"""Main-thread dispatcher for executing queued operations inside Blender."""

import logging
import traceback
from typing import Optional
from .request_queue import global_queue
from ..operations.registry import get_operation

try:
    import bpy
except ImportError:
    bpy = None

logger = logging.getLogger("blender_ai_control.dispatcher")

_IS_REGISTERED = False


def process_queue() -> Optional[float]:
    """Blender timer callback executing queued requests on Blender's main thread."""
    processed_count = 0
    while processed_count < 5:
        req = global_queue.get_pending(block=False)
        if req is None:
            break

        processed_count += 1
        handler = get_operation(req.operation)
        if not handler:
            req.mark_failed(
                "UNSUPPORTED_OPERATION",
                f"Operation '{req.operation}' is not registered or supported",
            )
            continue

        try:
            req.status = "running"
            result = handler(req.arguments)
            req.mark_completed(result)
        except Exception as exc:
            trace = traceback.format_exc()
            logger.error(f"Error executing operation '{req.operation}': {exc}\n{trace}")
            req.mark_failed(
                "OPERATION_FAILED",
                str(exc),
                {"exception": type(exc).__name__, "traceback": trace},
            )

    return 0.02  # Call back every 20ms


def start_dispatcher() -> None:
    """Register the timer callback with Blender."""
    global _IS_REGISTERED
    if bpy is not None and not _IS_REGISTERED:
        if hasattr(bpy.app, "timers"):
            if not bpy.app.timers.is_registered(process_queue):
                bpy.app.timers.register(process_queue, persistent=True)
                _IS_REGISTERED = True
                logger.info("Blender AI Control main-thread dispatcher started.")


def stop_dispatcher() -> None:
    """Unregister the timer callback from Blender."""
    global _IS_REGISTERED
    if bpy is not None and _IS_REGISTERED:
        if hasattr(bpy.app, "timers"):
            if bpy.app.timers.is_registered(process_queue):
                bpy.app.timers.unregister(process_queue)
        _IS_REGISTERED = False
        logger.info("Blender AI Control main-thread dispatcher stopped.")
