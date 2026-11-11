"""Serialization helpers for Blender types to plain JSON-compatible types."""

from typing import Any


def serialize_blender_value(val: Any) -> Any:
    """Recursively convert Blender / mathutils types into JSON-serializable types."""
    if val is None or isinstance(val, (bool, int, float, str)):
        return val

    # Handles mathutils.Vector, mathutils.Euler, mathutils.Color, tuples, lists
    if hasattr(val, "to_tuple"):
        return list(val.to_tuple())
    if hasattr(val, "to_list"):
        return val.to_list()
    if isinstance(val, (list, tuple, set)):
        return [serialize_blender_value(item) for item in val]
    if isinstance(val, dict):
        return {str(k): serialize_blender_value(v) for k, v in val.items()}

    # Handles bpy.types.Object reference
    if hasattr(val, "name") and hasattr(val, "type"):
        return {
            "name": val.name,
            "type": getattr(val, "type", "UNKNOWN"),
        }

    return str(val)
