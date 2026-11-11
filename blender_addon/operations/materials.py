"""Material, texture, and UV operations executing on Blender's main thread."""

import math
import os
from typing import Any, Dict, List, Optional
from ..bridge.serializers import serialize_blender_value
from .registry import register_operation

try:
    import bmesh
    import bpy
except ImportError:
    bmesh = None
    bpy = None


def _get_bsdf_node(mat):
    if not mat.use_nodes or not mat.node_tree:
        return None
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    return None


def _set_bsdf_input(bsdf, socket_names: List[str], value: Any) -> bool:
    for name in socket_names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return True
    return False


def _get_bsdf_input(bsdf, socket_names: List[str]) -> Any:
    for name in socket_names:
        if name in bsdf.inputs:
            val = bsdf.inputs[name].default_value
            if isinstance(val, float):
                return round(val, 4)
            if hasattr(val, "__iter__") and not isinstance(val, (str, bytes)):
                return [round(x, 4) if isinstance(x, float) else x for x in val]
            return val
    return None


@register_operation("material.list")
def list_materials_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List materials in the project or on a specific object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    object_name = args.get("object_name")
    if object_name:
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise KeyError(f"Object '{object_name}' not found")
        materials = [
            {"slot": idx, "name": slot.material.name}
            for idx, slot in enumerate(obj.material_slots)
            if slot.material
        ]
        return {"object_name": obj.name, "materials": materials}

    all_mats = [{"name": m.name, "users": m.users} for m in bpy.data.materials]
    return {"total": len(all_mats), "materials": all_mats}


@register_operation("material.create")
def create_material_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Principled BSDF material with optional initial color and properties."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name", "NewMaterial")
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    bsdf = _get_bsdf_node(mat)
    if bsdf:
        base_color = args.get("base_color")
        if base_color:
            if len(base_color) == 3:
                base_color = [*base_color, 1.0]
            _set_bsdf_input(bsdf, ["Base Color"], tuple(base_color))

        if "roughness" in args and args["roughness"] is not None:
            _set_bsdf_input(bsdf, ["Roughness"], float(args["roughness"]))
        if "metallic" in args and args["metallic"] is not None:
            _set_bsdf_input(bsdf, ["Metallic"], float(args["metallic"]))
        if "specular" in args and args["specular"] is not None:
            _set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], float(args["specular"]))

    return {
        "name": mat.name,
        "use_nodes": mat.use_nodes,
    }


@register_operation("material.configure")
def configure_material_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure Principled BSDF parameters of an existing material."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    mat = bpy.data.materials.get(name)
    if not mat:
        raise KeyError(f"Material '{name}' not found")

    bsdf = _get_bsdf_node(mat)
    if not bsdf:
        raise ValueError(f"Material '{name}' does not have a Principled BSDF node")

    updated = {}

    if "base_color" in args and args["base_color"] is not None:
        col = args["base_color"]
        if len(col) == 3:
            col = [*col, 1.0]
        if _set_bsdf_input(bsdf, ["Base Color"], tuple(col)):
            updated["base_color"] = col

    if "roughness" in args and args["roughness"] is not None:
        val = float(args["roughness"])
        if _set_bsdf_input(bsdf, ["Roughness"], val):
            updated["roughness"] = val

    if "metallic" in args and args["metallic"] is not None:
        val = float(args["metallic"])
        if _set_bsdf_input(bsdf, ["Metallic"], val):
            updated["metallic"] = val

    if "specular" in args and args["specular"] is not None:
        val = float(args["specular"])
        if _set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], val):
            updated["specular"] = val

    if "transmission" in args and args["transmission"] is not None:
        val = float(args["transmission"])
        if _set_bsdf_input(bsdf, ["Transmission Weight", "Transmission"], val):
            updated["transmission"] = val

    if "emission_color" in args and args["emission_color"] is not None:
        ec = args["emission_color"]
        if len(ec) == 3:
            ec = [*ec, 1.0]
        if _set_bsdf_input(bsdf, ["Emission Color", "Emission"], tuple(ec)):
            updated["emission_color"] = ec

    if "emission_strength" in args and args["emission_strength"] is not None:
        val = float(args["emission_strength"])
        if _set_bsdf_input(bsdf, ["Emission Strength"], val):
            updated["emission_strength"] = val

    if "alpha" in args and args["alpha"] is not None:
        val = float(args["alpha"])
        if _set_bsdf_input(bsdf, ["Alpha"], val):
            updated["alpha"] = val

    if "ior" in args and args["ior"] is not None:
        val = float(args["ior"])
        if _set_bsdf_input(bsdf, ["IOR"], val):
            updated["ior"] = val

    return {
        "name": mat.name,
        "updated": updated,
    }


@register_operation("material.assign")
def assign_material_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Assign a material to an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    object_name = args.get("object_name")
    material_name = args.get("material_name")
    slot_index = args.get("slot_index")

    if not object_name or not material_name:
        raise ValueError("Both 'object_name' and 'material_name' are required")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise KeyError(f"Object '{object_name}' not found")

    mat = bpy.data.materials.get(material_name)
    if not mat:
        raise KeyError(f"Material '{material_name}' not found")

    if slot_index is not None and slot_index < len(obj.material_slots):
        obj.material_slots[slot_index].material = mat
        assigned_slot = slot_index
    else:
        if len(obj.material_slots) == 0:
            obj.data.materials.append(mat)
            assigned_slot = 0
        else:
            obj.material_slots[0].material = mat
            assigned_slot = 0

    return {
        "object_name": obj.name,
        "material_name": mat.name,
        "slot_index": assigned_slot,
    }


@register_operation("material.inspect")
def inspect_material_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect detailed properties and nodes of a material."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    mat = bpy.data.materials.get(name)
    if not mat:
        raise KeyError(f"Material '{name}' not found")

    bsdf = _get_bsdf_node(mat)
    info: Dict[str, Any] = {
        "name": mat.name,
        "use_nodes": mat.use_nodes,
        "users": mat.users,
    }

    if bsdf:
        info["base_color"] = _get_bsdf_input(bsdf, ["Base Color"])
        info["roughness"] = _get_bsdf_input(bsdf, ["Roughness"])
        info["metallic"] = _get_bsdf_input(bsdf, ["Metallic"])
        info["specular"] = _get_bsdf_input(bsdf, ["Specular IOR Level", "Specular"])
        info["transmission"] = _get_bsdf_input(bsdf, ["Transmission Weight", "Transmission"])
        info["emission_color"] = _get_bsdf_input(bsdf, ["Emission Color", "Emission"])
        info["emission_strength"] = _get_bsdf_input(bsdf, ["Emission Strength"])
        info["alpha"] = _get_bsdf_input(bsdf, ["Alpha"])
        info["ior"] = _get_bsdf_input(bsdf, ["IOR"])

    return info


@register_operation("texture.assign_image")
def assign_image_texture_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load an image file and connect it to a material shader node input."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    material_name = args.get("material_name")
    image_path = args.get("image_path")
    target_socket = args.get("target_socket", "Base Color")

    if not material_name or not image_path:
        raise ValueError("Both 'material_name' and 'image_path' are required")

    mat = bpy.data.materials.get(material_name)
    if not mat:
        raise KeyError(f"Material '{material_name}' not found")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Texture image file not found: {image_path}")

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = _get_bsdf_node(mat)
    if not bsdf:
        raise ValueError(f"Material '{material_name}' has no Principled BSDF node")

    image = bpy.data.images.load(image_path, check_existing=True)

    tex_node = nodes.new(type="ShaderNodeTexImage")
    tex_node.image = image
    tex_node.location = (bsdf.location.x - 300, bsdf.location.y)

    if target_socket in bsdf.inputs:
        links.new(tex_node.outputs["Color"], bsdf.inputs[target_socket])
    elif "Base Color" in bsdf.inputs:
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

    return {
        "material_name": mat.name,
        "image_name": image.name,
        "connected_to": target_socket,
    }


@register_operation("uv.list")
def list_uv_layers_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List UV layers on a mesh object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        raise ValueError(f"Object '{name}' is not a valid mesh object")

    uv_layers = [
        {"name": layer.name, "active": (layer == obj.data.uv_layers.active)}
        for layer in obj.data.uv_layers
    ]
    return {
        "object_name": obj.name,
        "total": len(uv_layers),
        "uv_layers": uv_layers,
    }


@register_operation("uv.unwrap")
def unwrap_uv_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Unwrap mesh UVs using Smart UV Project or standard projection."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    method = str(args.get("method", "SMART")).upper()
    island_margin = float(args.get("island_margin", 0.01))

    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        raise ValueError(f"Object '{name}' is not a valid mesh object")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")

    if method == "SMART":
        angle_limit = float(args.get("angle_limit", 66.0))
        bpy.ops.uv.smart_project(
            angle_limit=math.radians(angle_limit),
            island_margin=island_margin,
        )
    elif method == "CUBE":
        bpy.ops.uv.cube_project()
    elif method == "SPHERE":
        bpy.ops.uv.sphere_project()
    elif method == "CYLINDER":
        bpy.ops.uv.cylinder_project()
    else:
        bpy.ops.uv.smart_project(island_margin=island_margin)

    bpy.ops.object.mode_set(mode="OBJECT")

    active_uv = obj.data.uv_layers.active
    return {
        "object_name": obj.name,
        "method": method,
        "active_uv_layer": active_uv.name if active_uv else None,
    }


@register_operation("uv.inspect")
def inspect_uv_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect UV coordinates coverage and statistics on an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        raise ValueError(f"Object '{name}' is not a valid mesh object")

    active_uv = obj.data.uv_layers.active
    if not active_uv:
        return {
            "object_name": obj.name,
            "has_uvs": False,
            "message": "Object has no UV layers",
        }

    return {
        "object_name": obj.name,
        "has_uvs": True,
        "active_uv_layer": active_uv.name,
        "total_uv_layers": len(obj.data.uv_layers),
        "polygon_count": len(obj.data.polygons),
    }
