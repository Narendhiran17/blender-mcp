"""Object operations executing on Blender's main thread."""

from typing import Any, Dict
from ..bridge.serializers import serialize_blender_value
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


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

    # Switch to object mode if not already in object mode
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
        raise ValueError(f"Unsupported primitive type: '{primitive_type}'. Allowed: CUBE, UV_SPHERE, CYLINDER, PLANE, CONE, TORUS")

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
        "visible": not obj.hide_viewport,
        "parent": obj.parent.name if obj.parent else None,
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
    objects = []
    for obj in bpy.context.scene.objects:
        if obj_type and obj.type != obj_type.upper():
            continue
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "visible": not obj.hide_viewport,
        })

    return {
        "total": len(objects),
        "objects": objects,
    }
