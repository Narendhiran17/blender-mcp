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


class TransformObjectArgs(BaseModel):
    name: str = Field(description="Name of object to transform")
    location: Optional[Tuple[float, float, float]] = Field(default=None, description="New [X, Y, Z] location")
    rotation: Optional[Tuple[float, float, float]] = Field(default=None, description="New [X, Y, Z] Euler rotation in radians")
    scale: Optional[Tuple[float, float, float]] = Field(default=None, description="New [X, Y, Z] scale")
    relative: bool = Field(default=False, description="If True, transforms are applied relative to current values")


class RenameObjectArgs(BaseModel):
    old_name: str = Field(description="Current name of the object")
    new_name: str = Field(description="New target name for the object")


class DuplicateObjectArgs(BaseModel):
    name: str = Field(description="Name of object to duplicate")
    new_name: Optional[str] = Field(default=None, description="Optional new name for duplicate")
    linked: bool = Field(default=False, description="Whether to create a linked duplicate (sharing mesh data)")
    offset: Optional[Tuple[float, float, float]] = Field(default=None, description="Optional [X, Y, Z] offset")


class DeleteObjectArgs(BaseModel):
    name: str = Field(description="Name of object to delete")
    delete_data: bool = Field(default=True, description="Whether to delete unused underlying mesh data")


class SetParentArgs(BaseModel):
    child_name: str = Field(description="Name of child object")
    parent_name: Optional[str] = Field(default=None, description="Name of parent object (None to clear parent)")
    keep_transform: bool = Field(default=True, description="Whether to preserve world transform")


class SetVisibilityArgs(BaseModel):
    name: str = Field(description="Name of object")
    hide_viewport: Optional[bool] = Field(default=None, description="Hide or unhide in 3D viewport")
    hide_render: Optional[bool] = Field(default=None, description="Hide or unhide in final render")


class SelectObjectArgs(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of object to select or activate")
    select: bool = Field(default=True, description="Select (True) or deselect (False)")
    deselect_others: bool = Field(default=False, description="Whether to deselect all other objects")
    set_active: bool = Field(default=True, description="Whether to make this object the active object")


class SaveSceneArgs(BaseModel):
    filepath: Optional[str] = Field(default=None, description="Target .blend filepath (required if project is unsaved)")


class CreateSceneArgs(BaseModel):
    name: str = Field(default="New Scene", description="Name of scene to create")
    setup_mode: str = Field(default="NEW", description="Creation mode: NEW, LINK_COPY, FULL_COPY")


class CreateCollectionArgs(BaseModel):
    name: str = Field(description="Name of new collection")
    parent_collection: Optional[str] = Field(default=None, description="Parent collection name (defaults to scene root)")


class LinkCollectionArgs(BaseModel):
    object_name: str = Field(description="Name of object to link")
    collection_name: str = Field(description="Target collection name")
    unlink_from_others: bool = Field(default=False, description="Whether to remove object from all other collections")
