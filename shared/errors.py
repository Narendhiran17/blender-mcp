"""Standard error codes and exception classes for Blender AI Control MCP."""

from typing import Any, Dict, Optional


class ErrorCode:
    BLENDER_NOT_RUNNING = "BLENDER_NOT_RUNNING"
    BRIDGE_UNAVAILABLE = "BRIDGE_UNAVAILABLE"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    OBJECT_NOT_FOUND = "OBJECT_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    OPERATION_FAILED = "OPERATION_FAILED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_TIMEOUT = "TASK_TIMEOUT"
    TASK_CANCELLED = "TASK_CANCELLED"
    FILE_ACCESS_DENIED = "FILE_ACCESS_DENIED"
    BLENDER_VERSION_UNSUPPORTED = "BLENDER_VERSION_UNSUPPORTED"


class BlenderControlError(Exception):
    """Base exception for Blender AI Control operations."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
