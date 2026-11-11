"""Mesh modeling operations using bmesh on Blender's main thread."""

import math
from typing import Any, Dict, List, Optional
from ..bridge.serializers import serialize_blender_value
from .registry import register_operation

try:
    import bmesh
    import bpy
    import mathutils
except ImportError:
    bmesh = None
    bpy = None
    mathutils = None


def _get_mesh_object(name: str):
    if bpy is None:
        raise RuntimeError("bpy module is not available")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")
    if obj.type != "MESH" or not obj.data:
        raise ValueError(f"Object '{name}' is not a mesh object (type: {obj.type})")
    return obj


@register_operation("mesh.inspect")
def inspect_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect detailed mesh topology, geometry statistics, and UV layers."""
    obj = _get_mesh_object(args["name"])

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
    non_manifold_verts = sum(1 for v in bm.verts if not v.is_manifold)
    loose_verts = sum(1 for v in bm.verts if not v.link_edges)
    loose_edges = sum(1 for e in bm.edges if not e.link_faces)

    uv_layers = [layer.name for layer in bm.loops.layers.uv.values()]
    color_layers = [layer.name for layer in bm.loops.layers.color.values()]

    info = {
        "name": obj.name,
        "vertex_count": len(bm.verts),
        "edge_count": len(bm.edges),
        "polygon_count": len(bm.faces),
        "non_manifold_edges": non_manifold_edges,
        "non_manifold_verts": non_manifold_verts,
        "loose_verts": loose_verts,
        "loose_edges": loose_edges,
        "is_watertight": (non_manifold_edges == 0 and loose_verts == 0 and len(bm.faces) > 0),
        "uv_layers": uv_layers,
        "has_uvs": len(uv_layers) > 0,
        "color_layers": color_layers,
    }
    bm.free()
    return info


@register_operation("mesh.subdivide")
def subdivide_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Subdivide mesh edges/faces."""
    obj = _get_mesh_object(args["name"])
    cuts = int(args.get("cuts", 1))
    smoothness = float(args.get("smoothness", 0.0))

    if cuts < 1:
        raise ValueError("Parameter 'cuts' must be at least 1")

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    bmesh.ops.subdivide_edges(
        bm,
        edges=list(bm.edges),
        cuts=cuts,
        smooth=smoothness,
        use_grid_fill=True,
    )

    bm.to_mesh(obj.data)
    obj.data.update()

    result = {
        "name": obj.name,
        "vertex_count": len(bm.verts),
        "polygon_count": len(bm.faces),
        "cuts_applied": cuts,
    }
    bm.free()
    return result


@register_operation("mesh.bevel")
def bevel_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Bevel mesh edges or vertices."""
    obj = _get_mesh_object(args["name"])
    offset = float(args.get("offset", 0.1))
    segments = int(args.get("segments", 1))
    affect = str(args.get("affect", "EDGES")).upper()

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    geom = list(bm.verts) if affect == "VERTICES" else list(bm.edges)
    bmesh.ops.bevel(
        bm,
        geom=geom,
        offset=offset,
        segments=segments,
        affect=affect,
    )

    bm.to_mesh(obj.data)
    obj.data.update()

    result = {
        "name": obj.name,
        "vertex_count": len(bm.verts),
        "polygon_count": len(bm.faces),
        "offset": offset,
        "segments": segments,
        "affect": affect,
    }
    bm.free()
    return result


@register_operation("mesh.extrude")
def extrude_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Extrude faces along normal or specific vector."""
    obj = _get_mesh_object(args["name"])
    direction = tuple(args.get("direction", [0.0, 0.0, 1.0]))
    distance = float(args.get("distance", 1.0))
    face_indices = args.get("face_indices")

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    if face_indices is not None and len(face_indices) > 0:
        target_faces = [bm.faces[i] for i in face_indices if i < len(bm.faces)]
    else:
        target_faces = list(bm.faces)

    if not target_faces:
        bm.free()
        raise ValueError("No target faces found for extrusion")

    res = bmesh.ops.extrude_face_region(bm, geom=target_faces)
    extruded_verts = [elem for elem in res["geom"] if isinstance(elem, bmesh.types.BMVert)]

    norm = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2) or 1.0
    vec = mathutils.Vector((
        (direction[0] / norm) * distance,
        (direction[1] / norm) * distance,
        (direction[2] / norm) * distance,
    ))

    bmesh.ops.translate(bm, vec=vec, verts=extruded_verts)

    bm.to_mesh(obj.data)
    obj.data.update()

    result = {
        "name": obj.name,
        "vertex_count": len(bm.verts),
        "polygon_count": len(bm.faces),
        "extruded_faces_count": len(target_faces),
        "translation": list(vec),
    }
    bm.free()
    return result


@register_operation("mesh.merge")
def merge_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Merge vertices by distance (remove doubles)."""
    obj = _get_mesh_object(args["name"])
    distance = float(args.get("distance", 0.0001))

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    initial_verts = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=distance)

    bm.to_mesh(obj.data)
    obj.data.update()

    removed = initial_verts - len(bm.verts)
    result = {
        "name": obj.name,
        "initial_vertices": initial_verts,
        "current_vertices": len(bm.verts),
        "removed_vertices": removed,
        "distance": distance,
    }
    bm.free()
    return result


@register_operation("mesh.recalculate_normals")
def recalculate_normals_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Recalculate face normals outward or inward."""
    obj = _get_mesh_object(args["name"])
    inside = bool(args.get("inside", False))

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if inside:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))

    bm.to_mesh(obj.data)
    obj.data.update()

    result = {
        "name": obj.name,
        "faces_count": len(bm.faces),
        "inside": inside,
    }
    bm.free()
    return result


@register_operation("mesh.shade_smooth")
def shade_smooth_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set smooth or flat shading on mesh polygons."""
    obj = _get_mesh_object(args["name"])
    smooth = bool(args.get("smooth", True))

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    for poly in obj.data.polygons:
        poly.use_smooth = smooth
    obj.data.update()

    return {
        "name": obj.name,
        "smooth": smooth,
        "polygon_count": len(obj.data.polygons),
    }


@register_operation("mesh.validate")
def validate_mesh_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate mesh for 3D printing, rendering, and export readiness."""
    obj = _get_mesh_object(args["name"])

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
    non_manifold_verts = sum(1 for v in bm.verts if not v.is_manifold)
    loose_verts = sum(1 for v in bm.verts if not v.link_edges)
    loose_edges = sum(1 for e in bm.edges if not e.link_faces)
    zero_area_faces = sum(1 for f in bm.faces if f.calc_area() <= 1e-7)

    is_watertight = (non_manifold_edges == 0 and loose_verts == 0 and len(bm.faces) > 0)
    is_valid = (non_manifold_edges == 0 and loose_verts == 0 and zero_area_faces == 0)

    issues = []
    if non_manifold_edges > 0:
        issues.append(f"{non_manifold_edges} non-manifold edges detected")
    if non_manifold_verts > 0:
        issues.append(f"{non_manifold_verts} non-manifold vertices detected")
    if loose_verts > 0:
        issues.append(f"{loose_verts} loose vertices detected")
    if loose_edges > 0:
        issues.append(f"{loose_edges} loose edges detected")
    if zero_area_faces > 0:
        issues.append(f"{zero_area_faces} zero-area faces detected")

    result = {
        "name": obj.name,
        "is_valid": is_valid,
        "is_watertight": is_watertight,
        "vertex_count": len(bm.verts),
        "polygon_count": len(bm.faces),
        "non_manifold_edges": non_manifold_edges,
        "loose_verts": loose_verts,
        "zero_area_faces": zero_area_faces,
        "issues": issues,
    }
    bm.free()
    return result
