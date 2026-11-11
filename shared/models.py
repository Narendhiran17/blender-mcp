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


# Phase 3 Models
class SubdivideMeshArgs(BaseModel):
    name: str = Field(description="Name of mesh object to subdivide")
    cuts: int = Field(default=1, ge=1, description="Number of cuts across edges")
    smoothness: float = Field(default=0.0, ge=0.0, le=1.0, description="Smoothness factor between 0.0 and 1.0")


class BevelMeshArgs(BaseModel):
    name: str = Field(description="Name of mesh object to bevel")
    offset: float = Field(default=0.1, gt=0.0, description="Bevel width/amount")
    segments: int = Field(default=1, ge=1, description="Number of bevel segments")
    affect: str = Field(default="EDGES", description="Whether to bevel EDGES or VERTICES")


class ExtrudeMeshArgs(BaseModel):
    name: str = Field(description="Name of mesh object to extrude")
    direction: Tuple[float, float, float] = Field(default=(0.0, 0.0, 1.0), description="[X, Y, Z] extrusion direction")
    distance: float = Field(default=1.0, description="Extrusion distance")
    face_indices: Optional[List[int]] = Field(default=None, description="Optional specific face indices to extrude")


class MergeMeshArgs(BaseModel):
    name: str = Field(description="Name of mesh object")
    distance: float = Field(default=0.0001, ge=0.0, description="Merge threshold distance")


class RecalculateNormalsArgs(BaseModel):
    name: str = Field(description="Name of mesh object")
    inside: bool = Field(default=False, description="Recalculate inward (True) or outward (False)")


class ShadeSmoothArgs(BaseModel):
    name: str = Field(description="Name of mesh object")
    smooth: bool = Field(default=True, description="Enable smooth shading (True) or flat shading (False)")


class AddModifierArgs(BaseModel):
    object_name: str = Field(description="Name of object")
    modifier_type: str = Field(description="Type of modifier (e.g. SUBSURF, BEVEL, SOLIDIFY, MIRROR, ARRAY, BOOLEAN)")
    name: Optional[str] = Field(default=None, description="Custom name for modifier")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Initial property values for the modifier")


class ConfigureModifierArgs(BaseModel):
    object_name: str = Field(description="Name of object")
    modifier_name: str = Field(description="Name of modifier to configure")
    properties: Dict[str, Any] = Field(description="Dictionary of property key-values to update")


class ApplyModifierArgs(BaseModel):
    object_name: str = Field(description="Name of object")
    modifier_name: str = Field(description="Name of modifier to apply")


# Phase 4 Models
class CreateMaterialArgs(BaseModel):
    name: str = Field(default="NewMaterial", description="Material name")
    base_color: Optional[Tuple[float, float, float]] = Field(default=None, description="[R, G, B] color (0.0 to 1.0)")
    roughness: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Roughness factor (0.0 to 1.0)")
    metallic: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Metallic factor (0.0 to 1.0)")
    specular: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Specular intensity")


class ConfigureMaterialArgs(BaseModel):
    name: str = Field(description="Name of material to configure")
    base_color: Optional[List[float]] = Field(default=None, description="[R, G, B] or [R, G, B, A] color")
    roughness: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metallic: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    specular: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    transmission: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    emission_color: Optional[List[float]] = Field(default=None)
    emission_strength: Optional[float] = Field(default=None, ge=0.0)
    alpha: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    ior: Optional[float] = Field(default=None, ge=0.0)


class AssignMaterialArgs(BaseModel):
    object_name: str = Field(description="Name of target object")
    material_name: str = Field(description="Name of material to assign")
    slot_index: Optional[int] = Field(default=None, ge=0, description="Material slot index (default: slot 0)")


class AssignImageTextureArgs(BaseModel):
    material_name: str = Field(description="Name of material")
    image_path: str = Field(description="Absolute path to image texture")
    target_socket: str = Field(default="Base Color", description="Target shader input socket")


class UnwrapUVArgs(BaseModel):
    name: str = Field(description="Name of mesh object to unwrap")
    method: str = Field(default="SMART", description="Unwrap method: SMART, CUBE, SPHERE, CYLINDER")
    island_margin: float = Field(default=0.01, ge=0.0, description="Space between UV islands")
    angle_limit: float = Field(default=66.0, description="Angle limit for Smart UV project")


class CreateLightArgs(BaseModel):
    light_type: str = Field(default="POINT", description="Light type: POINT, SUN, SPOT, AREA")
    name: Optional[str] = Field(default=None, description="Name for light object")
    location: Tuple[float, float, float] = Field(default=(0.0, 0.0, 5.0), description="[X, Y, Z] world location")
    rotation: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[X, Y, Z] Euler rotation")
    energy: float = Field(default=1000.0, description="Energy in Watts (or Sun lux)")
    color: Tuple[float, float, float] = Field(default=(1.0, 1.0, 1.0), description="[R, G, B] light color")


class ConfigureLightArgs(BaseModel):
    name: str = Field(description="Name of light object")
    energy: Optional[float] = Field(default=None, ge=0.0)
    color: Optional[List[float]] = Field(default=None)
    light_type: Optional[str] = Field(default=None)
    spot_size: Optional[float] = Field(default=None, description="Spot beam angle in degrees")


class CreateCameraArgs(BaseModel):
    name: str = Field(default="Camera", description="Name for camera object")
    location: Tuple[float, float, float] = Field(default=(0.0, -5.0, 2.0), description="[X, Y, Z] location")
    rotation: Tuple[float, float, float] = Field(default=(1.3, 0.0, 0.0), description="[X, Y, Z] Euler rotation in radians")
    focal_length: float = Field(default=50.0, gt=0.0, description="Focal length in mm")
    clip_start: float = Field(default=0.1, gt=0.0)
    clip_end: float = Field(default=1000.0, gt=0.0)
    set_active: bool = Field(default=True, description="Whether to make this the active scene camera")


class ConfigureCameraArgs(BaseModel):
    name: str = Field(description="Name of camera object")
    focal_length: Optional[float] = Field(default=None, gt=0.0)
    clip_start: Optional[float] = Field(default=None, gt=0.0)
    clip_end: Optional[float] = Field(default=None, gt=0.0)


class ConfigureWorldArgs(BaseModel):
    color: Optional[List[float]] = Field(default=None, description="[R, G, B] background illumination color")
    strength: Optional[float] = Field(default=None, ge=0.0, description="Background illumination intensity")
    hdri_path: Optional[str] = Field(default=None, description="Path to HDRI environment map")


# Phase 5: Geometry Nodes
class InspectGeometryNodesArgs(BaseModel):
    object_name: Optional[str] = Field(default=None, description="Optional name of object with GeometryNodes modifier")
    modifier_name: Optional[str] = Field(default="GeometryNodes", description="Modifier name on object")
    group_name: Optional[str] = Field(default=None, description="Direct name of node group to inspect")


class AssignGeometryNodesArgs(BaseModel):
    object_name: str = Field(description="Target object name")
    group_name: Optional[str] = Field(default=None, description="Existing or new node group name")
    modifier_name: str = Field(default="GeometryNodes", description="Name for the modifier")
    create_if_missing: bool = Field(default=True, description="Create a new GeometryNodeTree if group_name is not found")


class ConfigureGeometryNodesArgs(BaseModel):
    object_name: str = Field(description="Target object name")
    modifier_name: str = Field(default="GeometryNodes", description="Modifier name on object")
    inputs: Dict[str, Any] = Field(description="Dictionary of input socket names or identifiers and their values")


# Phase 5: Armatures & Rigging
class CreateArmatureArgs(BaseModel):
    name: str = Field(default="Armature", description="Name for the armature object")
    location: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[X, Y, Z] world location")
    rotation: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[X, Y, Z] Euler rotation in radians")
    scale: Tuple[float, float, float] = Field(default=(1.0, 1.0, 1.0), description="[X, Y, Z] scale multipliers")
    initial_bone_name: Optional[str] = Field(default="Root", description="Optional initial bone name")
    initial_bone_head: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[X, Y, Z] root bone head")
    initial_bone_tail: Tuple[float, float, float] = Field(default=(0.0, 0.0, 1.0), description="[X, Y, Z] root bone tail")


class InspectArmatureArgs(BaseModel):
    name: str = Field(description="Name of armature object to inspect")


class AddBoneArgs(BaseModel):
    armature_name: str = Field(description="Name of armature object")
    bone_name: str = Field(description="Name for new bone")
    head: Tuple[float, float, float] = Field(default=(0.0, 0.0, 0.0), description="[X, Y, Z] head position in local space")
    tail: Tuple[float, float, float] = Field(default=(0.0, 0.0, 1.0), description="[X, Y, Z] tail position in local space")
    parent_bone: Optional[str] = Field(default=None, description="Optional parent bone name")
    use_connect: bool = Field(default=False, description="Whether bone head is connected to parent tail")
    roll: float = Field(default=0.0, description="Bone roll angle in radians")


class ParentMeshToArmatureArgs(BaseModel):
    mesh_object_name: str = Field(description="Name of mesh object to parent")
    armature_object_name: str = Field(description="Name of armature object")
    parent_type: str = Field(
        default="ARMATURE_AUTO",
        description="Parenting type: ARMATURE_AUTO (with automatic weights), ARMATURE_ENVELOPE, ARMATURE",
    )


# Phase 5: Animation & Timeline
class CreateKeyframeArgs(BaseModel):
    object_name: str = Field(description="Target object name")
    data_path: str = Field(default="location", description="Animatable property path (e.g. location, rotation_euler, scale)")
    frame: float = Field(description="Timeline frame number for the keyframe")
    value: Optional[Any] = Field(default=None, description="Optional value to set before keyframing (float or list of floats)")
    index: int = Field(default=-1, description="Array index for vector properties (-1 for all axes, 0 for X, 1 for Y, 2 for Z)")


class InspectAnimationArgs(BaseModel):
    object_name: str = Field(description="Name of object to inspect animation data for")


class ConfigureAnimationArgs(BaseModel):
    object_name: str = Field(description="Target object name")
    data_path: Optional[str] = Field(default=None, description="Filter fcurves by data_path")
    interpolation: Optional[str] = Field(default=None, description="Interpolation mode: BEZIER, LINEAR, CONSTANT")
    clear_all: bool = Field(default=False, description="Clear all animation data from the object")
    delete_frame: Optional[float] = Field(default=None, description="Delete keyframes at specified frame number")


class PlaybackRangeArgs(BaseModel):
    frame_start: Optional[int] = Field(default=None, description="Start frame of playback")
    frame_end: Optional[int] = Field(default=None, description="End frame of playback")
    frame_current: Optional[int] = Field(default=None, description="Current playhead frame")
    fps: Optional[int] = Field(default=None, description="Playback frames per second")
