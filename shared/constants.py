"""Shared constants across the Blender AI Control MCP project."""

PROTOCOL_VERSION = "1"

DEFAULT_BRIDGE_HOST = "127.0.0.1"
DEFAULT_BRIDGE_PORT = 8765
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30.0

# Task and Operation statuses
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_CANCEL_REQUESTED = "cancel_requested"
STATUS_CANCELLED = "cancelled"
STATUS_TIMED_OUT = "timed_out"

# Standard Operation Names
OP_HEALTH = "system.health"
OP_STATUS = "system.status"
OP_VERSION = "system.version"

OP_CREATE_PRIMITIVE = "object.create_primitive"
OP_INSPECT_OBJECT = "object.inspect"
OP_LIST_OBJECTS = "object.list"
OP_RENAME_OBJECT = "object.rename"
OP_TRANSFORM_OBJECT = "object.transform"
OP_DUPLICATE_OBJECT = "object.duplicate"
OP_DELETE_OBJECT = "object.delete"
OP_SET_PARENT = "object.set_parent"
OP_SET_VISIBILITY = "object.set_visibility"
OP_SELECT_OBJECT = "object.select"

OP_SCENE_LIST = "scene.list"
OP_SCENE_INSPECT = "scene.inspect"
OP_SCENE_CREATE = "scene.create"
OP_SCENE_SET_ACTIVE = "scene.set_active"
OP_SCENE_SAVE = "scene.save"

OP_COLLECTION_LIST = "collection.list"
OP_COLLECTION_CREATE = "collection.create"
OP_COLLECTION_LINK = "collection.link_object"

# Phase 3 Modeling Operations
OP_MESH_INSPECT = "mesh.inspect"
OP_MESH_SUBDIVIDE = "mesh.subdivide"
OP_MESH_BEVEL = "mesh.bevel"
OP_MESH_EXTRUDE = "mesh.extrude"
OP_MESH_MERGE = "mesh.merge"
OP_MESH_RECALCULATE_NORMALS = "mesh.recalculate_normals"
OP_MESH_SHADE_SMOOTH = "mesh.shade_smooth"
OP_MESH_VALIDATE = "mesh.validate"

OP_MODIFIER_LIST = "modifier.list"
OP_MODIFIER_ADD = "modifier.add"
OP_MODIFIER_CONFIGURE = "modifier.configure"
OP_MODIFIER_APPLY = "modifier.apply"
OP_MODIFIER_REMOVE = "modifier.remove"
OP_MODIFIER_REORDER = "modifier.reorder"
