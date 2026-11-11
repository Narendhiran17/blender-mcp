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
