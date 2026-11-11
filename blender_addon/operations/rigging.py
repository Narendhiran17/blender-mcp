"""Armature and rigging operations executing on Blender's main thread."""

from typing import Any, Dict, List, Optional
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


def _get_object(name: str):
    if bpy is None:
        raise RuntimeError("bpy module is not available")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")
    return obj


@register_operation("armature.create")
def create_armature_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Armature object, optionally with an initial root bone."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name", "Armature")
    location = args.get("location", [0.0, 0.0, 0.0])
    rotation = args.get("rotation", [0.0, 0.0, 0.0])
    scale = args.get("scale", [1.0, 1.0, 1.0])
    initial_bone_name = args.get("initial_bone_name", "Root")
    initial_bone_head = args.get("initial_bone_head", [0.0, 0.0, 0.0])
    initial_bone_tail = args.get("initial_bone_tail", [0.0, 0.0, 1.0])

    arm_data = bpy.data.armatures.new(name)
    arm_obj = bpy.data.objects.new(name, arm_data)
    arm_obj.location = location
    arm_obj.rotation_euler = rotation
    arm_obj.scale = scale

    bpy.context.scene.collection.objects.link(arm_obj)

    bones_created = []
    if initial_bone_name:
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode="EDIT")
        try:
            bone = arm_data.edit_bones.new(initial_bone_name)
            bone.head = initial_bone_head
            bone.tail = initial_bone_tail
            bones_created.append(bone.name)
        finally:
            bpy.ops.object.mode_set(mode="OBJECT")
            if prev_active:
                bpy.context.view_layer.objects.active = prev_active

    return {
        "name": arm_obj.name,
        "type": "ARMATURE",
        "location": [round(v, 4) for v in arm_obj.location],
        "bone_count": len(arm_data.bones),
        "bones": bones_created,
    }


@register_operation("armature.inspect")
def inspect_armature_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect bone hierarchy, positions, lengths, and parents of an armature."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing armature 'name'")

    arm_obj = _get_object(name)
    if arm_obj.type != "ARMATURE":
        raise ValueError(f"Object '{name}' is of type '{arm_obj.type}', expected 'ARMATURE'")

    arm_data = arm_obj.data
    bones_info = []
    for bone in arm_data.bones:
        bones_info.append({
            "name": bone.name,
            "head": [round(v, 4) for v in bone.head_local],
            "tail": [round(v, 4) for v in bone.tail_local],
            "length": round(bone.length, 4),
            "parent": bone.parent.name if bone.parent else None,
            "children": [c.name for c in bone.children],
            "use_connect": bone.use_connect,
        })

    return {
        "name": arm_obj.name,
        "bone_count": len(bones_info),
        "bones": bones_info,
    }


@register_operation("armature.add_bone")
def add_bone_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new bone to an existing armature in edit mode."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    arm_name = args.get("armature_name")
    if not arm_name:
        raise ValueError("Missing 'armature_name'")

    bone_name = args.get("bone_name")
    if not bone_name:
        raise ValueError("Missing 'bone_name'")

    head = args.get("head", [0.0, 0.0, 0.0])
    tail = args.get("tail", [0.0, 0.0, 1.0])
    parent_bone = args.get("parent_bone")
    use_connect = args.get("use_connect", False)
    roll = args.get("roll", 0.0)

    arm_obj = _get_object(arm_name)
    if arm_obj.type != "ARMATURE":
        raise ValueError(f"Object '{arm_name}' is not an ARMATURE")

    arm_data = arm_obj.data
    prev_active = bpy.context.view_layer.objects.active

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        new_bone = arm_data.edit_bones.new(bone_name)
        new_bone.head = head
        new_bone.tail = tail
        new_bone.roll = roll

        if parent_bone:
            parent = arm_data.edit_bones.get(parent_bone)
            if not parent:
                raise KeyError(f"Parent bone '{parent_bone}' not found in armature '{arm_name}'")
            new_bone.parent = parent
            new_bone.use_connect = use_connect

        created_name = new_bone.name
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
        if prev_active:
            bpy.context.view_layer.objects.active = prev_active

    return {
        "armature_name": arm_obj.name,
        "bone_name": created_name,
        "head": head,
        "tail": tail,
        "parent": parent_bone,
        "use_connect": use_connect,
    }


@register_operation("rig.parent_mesh")
def parent_mesh_to_armature_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Parent a mesh to an armature object with vertex weighting and modifier setup."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    mesh_name = args.get("mesh_object_name")
    arm_name = args.get("armature_object_name")
    parent_type = args.get("parent_type", "ARMATURE_AUTO")

    if not mesh_name or not arm_name:
        raise ValueError("Both 'mesh_object_name' and 'armature_object_name' are required")

    mesh_obj = _get_object(mesh_name)
    arm_obj = _get_object(arm_name)

    if mesh_obj.type != "MESH":
        raise ValueError(f"Object '{mesh_name}' is of type '{mesh_obj.type}', expected 'MESH'")
    if arm_obj.type != "ARMATURE":
        raise ValueError(f"Object '{arm_name}' is of type '{arm_obj.type}', expected 'ARMATURE'")

    # Ensure objects are visible in viewport for selection
    mesh_obj.hide_viewport = False
    arm_obj.hide_viewport = False

    # Select mesh, then armature as active
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    # Parent
    bpy.ops.object.parent_set(type=parent_type)

    return {
        "mesh_name": mesh_obj.name,
        "armature_name": arm_obj.name,
        "parent_type": parent_type,
        "parent": mesh_obj.parent.name if mesh_obj.parent else None,
        "vertex_group_count": len(mesh_obj.vertex_groups),
        "modifiers": [m.name for m in mesh_obj.modifiers],
    }
