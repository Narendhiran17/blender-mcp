"""System and status operations executing on Blender's main thread."""

import sys
from typing import Any, Dict
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None

_SHUTDOWN_REQUESTED = False


def is_shutdown_requested() -> bool:
    return _SHUTDOWN_REQUESTED


@register_operation("system.health")
def health_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Check health and connectivity of Blender main thread."""
    if bpy is None:
        return {
            "status": "warning",
            "blender_connected": False,
            "message": "bpy module not found (running in mock or external environment)",
        }

    return {
        "status": "ok",
        "blender_connected": True,
        "blender_version": list(bpy.app.version),
        "blender_version_string": bpy.app.version_string,
        "python_version": sys.version,
    }


@register_operation("system.status")
def status_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return detailed status of the active Blender project and scene."""
    if bpy is None:
        return {
            "blender_connected": False,
            "error": "bpy not available",
        }

    scene = bpy.context.scene
    active_obj = bpy.context.active_object
    selected_objects = [obj.name for obj in bpy.context.selected_objects]

    return {
        "blender_connected": True,
        "blender_version": list(bpy.app.version),
        "blender_version_string": bpy.app.version_string,
        "project_filepath": bpy.data.filepath or None,
        "is_saved": bool(bpy.data.filepath),
        "is_dirty": bpy.data.is_dirty,
        "active_scene": scene.name if scene else None,
        "objects_count": len(bpy.data.objects),
        "active_object": active_obj.name if active_obj else None,
        "selected_objects": selected_objects,
        "render_engine": scene.render.engine if scene else None,
    }


@register_operation("system.version")
def version_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return version metadata."""
    if bpy is None:
        return {"version": [0, 0, 0], "version_string": "unknown"}

    return {
        "version": list(bpy.app.version),
        "version_string": bpy.app.version_string,
        "build_date": getattr(bpy.app, "build_date", "unknown"),
        "build_platform": sys.platform,
    }


@register_operation("system.shutdown")
def shutdown_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Signal background test runner to exit cleanly."""
    global _SHUTDOWN_REQUESTED
    _SHUTDOWN_REQUESTED = True
    return {"status": "shutdown_requested"}
