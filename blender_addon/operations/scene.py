"""Scene and collection operations executing on Blender's main thread."""

import os
from typing import Any, Dict, List, Optional
from ..bridge.serializers import serialize_blender_value
from ..security.path_policy import is_safe_workspace_path
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


@register_operation("scene.list")
def list_scenes_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all scenes in the current project."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    active_scene = bpy.context.scene
    scenes_data = []

    for scn in bpy.data.scenes:
        scenes_data.append({
            "name": scn.name,
            "is_active": (scn == active_scene),
            "render_engine": scn.render.engine,
            "active_camera": scn.camera.name if scn.camera else None,
            "objects_count": len(scn.objects),
            "unit_system": scn.unit_settings.system,
        })

    return {
        "total": len(scenes_data),
        "scenes": scenes_data,
        "active_scene": active_scene.name if active_scene else None,
    }


@register_operation("scene.inspect")
def inspect_scene_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect detailed settings of a specific scene or active scene."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    scene = bpy.data.scenes.get(name) if name else bpy.context.scene

    if not scene:
        raise KeyError(f"Scene '{name}' not found")

    # Collect collection names
    collections = [col.name for col in scene.collection.children]

    return {
        "name": scene.name,
        "is_active": (scene == bpy.context.scene),
        "render_engine": scene.render.engine,
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "resolution_percentage": scene.render.resolution_percentage,
        "fps": scene.render.fps,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "active_camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "unit_system": scene.unit_settings.system,
        "unit_length": scene.unit_settings.length_unit,
        "objects_count": len(scene.objects),
        "root_collections": collections,
    }


@register_operation("scene.create")
def create_scene_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new scene."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name", "New Scene")
    setup_mode = args.get("setup_mode", "NEW").upper()

    if setup_mode in ("NEW", "EMPTY"):
        new_scene = bpy.data.scenes.new(name)
    elif setup_mode == "LINK_COPY":
        new_scene = bpy.context.scene.copy()
        new_scene.name = name
    elif setup_mode == "FULL_COPY":
        bpy.ops.scene.new(type="FULL_COPY")
        new_scene = bpy.context.scene
        new_scene.name = name
    else:
        new_scene = bpy.data.scenes.new(name)

    return {
        "name": new_scene.name,
        "objects_count": len(new_scene.objects),
        "render_engine": new_scene.render.engine,
    }


@register_operation("scene.set_active")
def set_active_scene_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set the active scene."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    scene = bpy.data.scenes.get(name)
    if not scene:
        raise KeyError(f"Scene '{name}' not found")

    if hasattr(bpy.context, "window") and bpy.context.window:
        bpy.context.window.scene = scene

    return {
        "active_scene": scene.name,
        "render_engine": scene.render.engine,
    }


@register_operation("scene.save")
def save_scene_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Save the Blender project file."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    filepath = args.get("filepath")
    workspace = os.environ.get("BLENDER_WORKSPACE_PATH")

    if filepath:
        if not is_safe_workspace_path(filepath, workspace):
            raise PermissionError(f"Filepath '{filepath}' is outside allowed workspace or in a restricted system directory")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
    else:
        if not bpy.data.filepath:
            raise ValueError("Project has never been saved. A 'filepath' must be provided for initial save.")
        bpy.ops.wm.save_mainfile()

    return {
        "filepath": bpy.data.filepath,
        "is_saved": True,
        "is_dirty": bpy.data.is_dirty,
    }


@register_operation("collection.list")
def list_collections_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all collections in the active scene or project."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    collections_data = []

    def scan_collection(col, parent_name=None):
        collections_data.append({
            "name": col.name,
            "parent": parent_name,
            "objects_count": len(col.objects),
            "objects": [obj.name for obj in col.objects],
        })
        for child in col.children:
            scan_collection(child, col.name)

    scan_collection(scene.collection, parent_name=None)

    return {
        "total": len(collections_data),
        "collections": collections_data,
    }


@register_operation("collection.create")
def create_collection_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new collection and link it to the scene or parent collection."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    parent_name = args.get("parent_collection")
    if parent_name:
        parent_col = bpy.data.collections.get(parent_name)
        if not parent_col:
            raise KeyError(f"Parent collection '{parent_name}' not found")
    else:
        parent_col = bpy.context.scene.collection

    new_col = bpy.data.collections.new(name)
    parent_col.children.link(new_col)

    return {
        "name": new_col.name,
        "parent": parent_col.name,
    }


@register_operation("collection.link_object")
def link_object_to_collection_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Link an object to a collection, with optional unlinking from other collections."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    object_name = args.get("object_name")
    collection_name = args.get("collection_name")
    unlink_from_others = bool(args.get("unlink_from_others", False))

    if not object_name or not collection_name:
        raise ValueError("Arguments 'object_name' and 'collection_name' are required")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise KeyError(f"Object '{object_name}' not found")

    target_col = bpy.data.collections.get(collection_name)
    if not target_col:
        raise KeyError(f"Collection '{collection_name}' not found")

    if target_col not in obj.users_collection:
        target_col.objects.link(obj)

    if unlink_from_others:
        for col in list(obj.users_collection):
            if col != target_col:
                col.objects.unlink(obj)

    return {
        "object_name": obj.name,
        "collection": target_col.name,
        "current_collections": [c.name for c in obj.users_collection],
    }
