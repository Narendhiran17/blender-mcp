"""Pydantic data models for request and response envelopes."""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from shared.constants import (
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    PROTOCOL_VERSION,
    STATUS_COMPLETED,
    STATUS_FAILED,
)


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class RequestEnvelope(BaseModel):
    protocol_version: str = Field(default=PROTOCOL_VERSION)
    request_id: str
    operation: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = Field(default=DEFAULT_REQUEST_TIMEOUT_SECONDS)


class ResponseEnvelope(BaseModel):
    protocol_version: str = Field(default=PROTOCOL_VERSION)
    request_id: str
    status: str = Field(default=STATUS_COMPLETED)
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorPayload] = None

    @classmethod
    def success(cls, request_id: str, result: Dict[str, Any]) -> "ResponseEnvelope":
        return cls(
            request_id=request_id,
            status=STATUS_COMPLETED,
            result=result,
            error=None,
        )

    @classmethod
    def failure(
        cls, request_id: str, code: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> "ResponseEnvelope":
        return cls(
            request_id=request_id,
            status=STATUS_FAILED,
            result=None,
            error=ErrorPayload(code=code, message=message, details=details),
        )


class CreatePrimitiveArgs(BaseModel):
    primitive_type: str = Field(
        default="CUBE",
        description="Type of primitive: CUBE, UV_SPHERE, CYLINDER, PLANE, CONE, TORUS",
    )
    name: Optional[str] = Field(default=None, description="Name for the newly created object")
    location: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0), description="[X, Y, Z] world location"
    )
    rotation: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0), description="[X, Y, Z] Euler rotation in radians"
    )
    scale: Tuple[float, float, float] = Field(
        default=(1.0, 1.0, 1.0), description="[X, Y, Z] scale multipliers"
    )
    size: Optional[float] = Field(default=2.0, description="Overall size or radius if applicable")
