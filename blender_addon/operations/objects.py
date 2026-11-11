"""Object operations executing on Blender's main thread."""

import math
from typing import Any, Dict, List, Optional
from ..bridge.serializers import serialize_blender_value
from .registry import register_operation

try:
    import bpy
    import mathutils
except ImportError:
    bpy = None
    mathutils = None


@register_operation("object.create_primitive")
def create_primitive_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a 3D primitive mesh object in Blender."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    primitive_type = args.get("primitive_type", "CUBE").upper()
    name = args.get("name")
    location = tuple(args.get("location", [0.0, 0.0, 0.0]))
    rotation = tuple(args.get("rotation", [0.0, 0.0, 0.0]))
    scale = tuple(args.get("scale", [1.0, 1.0, 1.0]))
    size = float(args.get("size", 2.0))

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    if primitive_type == "CUBE":
        bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
    elif primitive_type in ("UV_SPHERE", "SPHERE"):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size / 2.0, location=location, rotation=rotation)
    elif primitive_type == "CYLINDER":
        bpy.ops.mesh.primitive_cylinder_add(radius=size / 2.0, depth=size, location=location, rotation=rotation)
    elif primitive_type == "PLANE":
        bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
    elif primitive_type == "CONE":
        bpy.ops.mesh.primitive_cone_add(radius1=size / 2.0, depth=size, location=location, rotation=rotation)
    elif primitive_type == "TORUS":
        bpy.ops.mesh.primitive_torus_add(major_radius=size / 2.0, minor_radius=size / 8.0, location=location, rotation=rotation)
    else:
        raise ValueError(
            f"Unsupported primitive type: '{primitive_type}'. Allowed: CUBE, UV_SPHERE, CYLINDER, PLANE, CONE, TORUS"
        )

    obj = bpy.context.active_object
    if not obj:
        raise RuntimeError("Failed to retrieve created primitive object")

    if name:
        obj.name = name

    obj.scale = scale

    return {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
    }


@register_operation("object.inspect")
def inspect_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect an existing object in Blender."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found in active project")

    info: Dict[str, Any] = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
        "visible_viewport": not obj.hide_viewport,
        "visible_render": not obj.hide_render,
        "parent": obj.parent.name if obj.parent else None,
        "children": [child.name for child in obj.children],
        "collections": [c.name for c in obj.users_collection],
        "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        "modifiers": [m.name for m in obj.modifiers],
    }

    if obj.type == "MESH" and obj.data:
        info["vertex_count"] = len(obj.data.vertices)
        info["polygon_count"] = len(obj.data.polygons)
        info["edge_count"] = len(obj.data.edges)

    return info


@register_operation("object.list")
def list_objects_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List objects in the active scene or project."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_type = args.get("type")
    collection_name = args.get("collection")

    source_objects = bpy.context.scene.objects
    if collection_name:
        col = bpy.data.collections.get(collection_name)
        if not col:
            raise KeyError(f"Collection '{collection_name}' not found")
        source_objects = col.objects

    objects = []
    for obj in source_objects:
        if obj_type and obj.type != obj_type.upper():
            continue
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "visible": not obj.hide_viewport,
            "parent": obj.parent.name if obj.parent else None,
        })

    return {
        "total": len(objects),
        "objects": objects,
    }


@register_operation("object.rename")
def rename_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Rename an existing object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    old_name = args.get("old_name") or args.get("name")
    new_name = args.get("new_name")

    if not old_name or not new_name:
        raise ValueError("Both 'old_name' and 'new_name' are required")

    obj = bpy.data.objects.get(old_name)
    if not obj:
        raise KeyError(f"Object '{old_name}' not found")

    obj.name = new_name
    return {
        "old_name": old_name,
        "new_name": obj.name,
    }


@register_operation("object.transform")
def transform_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Apply translation, rotation, or scale to an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")

    relative = bool(args.get("relative", False))

    if "location" in args and args["location"] is not None:
        loc = args["location"]
        if relative:
            obj.location[0] += loc[0]
            obj.location[1] += loc[1]
            obj.location[2] += loc[2]
        else:
            obj.location = tuple(loc)

    if "rotation" in args and args["rotation"] is not None:
        rot = args["rotation"]
        if relative:
            obj.rotation_euler[0] += rot[0]
            obj.rotation_euler[1] += rot[1]
            obj.rotation_euler[2] += rot[2]
        else:
            obj.rotation_euler = tuple(rot)

    if "scale" in args and args["scale"] is not None:
        sc = args["scale"]
        if relative:
            obj.scale[0] *= sc[0]
            obj.scale[1] *= sc[1]
            obj.scale[2] *= sc[2]
        else:
            obj.scale = tuple(sc)

    return {
        "name": obj.name,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
    }


@register_operation("object.duplicate")
def duplicate_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Duplicate an object (linked or unlinked/deep copy) with optional offset."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")

    linked = bool(args.get("linked", False))
    new_name = args.get("new_name")
    offset = args.get("offset")

    new_obj = obj.copy()
    if not linked and obj.data:
        new_obj.data = obj.data.copy()

    if new_name:
        new_obj.name = new_name

    if offset:
        new_obj.location[0] += offset[0]
        new_obj.location[1] += offset[1]
        new_obj.location[2] += offset[2]

    col = obj.users_collection[0] if obj.users_collection else bpy.context.scene.collection
    col.objects.link(new_obj)

    return {
        "original_name": obj.name,
        "name": new_obj.name,
        "type": new_obj.type,
        "linked": linked,
        "location": list(new_obj.location),
        "scale": list(new_obj.scale),
    }


@register_operation("object.delete")
def delete_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete an object from Blender and optionally clean its data block."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")

    delete_data = bool(args.get("delete_data", True))
    data_block = obj.data if delete_data else None

    for col in list(obj.users_collection):
        col.objects.unlink(obj)

    bpy.data.objects.remove(obj, do_unlink=True)

    if data_block and data_block.users == 0:
        if hasattr(bpy.data, "meshes") and data_block in bpy.data.meshes.values():
            bpy.data.meshes.remove(data_block)

    return {
        "deleted": True,
        "name": name,
    }


@register_operation("object.set_parent")
def set_parent_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Parent or unparent an object with transform preservation."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    child_name = args.get("child_name")
    parent_name = args.get("parent_name")
    keep_transform = bool(args.get("keep_transform", True))

    if not child_name:
        raise ValueError("Missing required argument: 'child_name'")

    child = bpy.data.objects.get(child_name)
    if not child:
        raise KeyError(f"Child object '{child_name}' not found")

    if not parent_name:
        if keep_transform and child.parent:
            child.matrix_world = child.matrix_world.copy()
        child.parent = None
        return {
            "child": child.name,
            "parent": None,
        }

    parent = bpy.data.objects.get(parent_name)
    if not parent:
        raise KeyError(f"Parent object '{parent_name}' not found")

    if child == parent:
        raise ValueError("An object cannot be parented to itself")

    if keep_transform and mathutils is not None:
        matrix_world = child.matrix_world.copy()
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()
        child.matrix_world = matrix_world
    else:
        child.parent = parent

    return {
        "child": child.name,
        "parent": parent.name,
        "location": list(child.location),
    }


@register_operation("object.set_visibility")
def set_visibility_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set object visibility in viewport and render."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")

    if "hide_viewport" in args and args["hide_viewport"] is not None:
        obj.hide_viewport = bool(args["hide_viewport"])

    if "hide_render" in args and args["hide_render"] is not None:
        obj.hide_render = bool(args["hide_render"])

    return {
        "name": obj.name,
        "visible_viewport": not obj.hide_viewport,
        "visible_render": not obj.hide_render,
    }


@register_operation("object.select")
def select_object_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Select or deselect objects and set active object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    select_state = bool(args.get("select", True))
    deselect_others = bool(args.get("deselect_others", False))
    set_active = bool(args.get("set_active", True))

    if deselect_others:
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

    target_obj = None
    if name:
        target_obj = bpy.data.objects.get(name)
        if not target_obj:
            raise KeyError(f"Object '{name}' not found")

        # If user explicitly asks to select an object, make sure it is unhidden in viewport
        if select_state and target_obj.hide_viewport:
            target_obj.hide_viewport = False

        target_obj.select_set(select_state)
        if set_active and select_state:
            bpy.context.view_layer.objects.active = target_obj

    selected_names = [o.name for o in bpy.context.selected_objects]
    active_name = bpy.context.active_object.name if bpy.context.active_object else None

    return {
        "active_object": active_name,
        "selected_objects": selected_names,
    }
