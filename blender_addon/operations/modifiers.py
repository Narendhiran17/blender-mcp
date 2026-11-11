"""Modifier management operations executing on Blender's main thread."""

from typing import Any, Dict, List, Optional
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


def _get_object_with_modifiers(name: str):
    if bpy is None:
        raise RuntimeError("bpy module is not available")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise KeyError(f"Object '{name}' not found")
    return obj


@register_operation("modifier.list")
def list_modifiers_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all modifiers on an object with their types and settings."""
    obj = _get_object_with_modifiers(args["object_name"] if "object_name" in args else args["name"])

    modifiers_data = []
    for mod in obj.modifiers:
        mod_info = {
            "name": mod.name,
            "type": mod.type,
            "show_viewport": mod.show_viewport,
            "show_render": mod.show_render,
            "show_in_editmode": getattr(mod, "show_in_editmode", False),
        }

        # Extract specific common properties
        if mod.type == "SUBSURF":
            mod_info["levels"] = getattr(mod, "levels", None)
            mod_info["render_levels"] = getattr(mod, "render_levels", None)
            mod_info["subdivision_type"] = getattr(mod, "subdivision_type", None)
        elif mod.type == "BEVEL":
            mod_info["width"] = getattr(mod, "width", None)
            mod_info["segments"] = getattr(mod, "segments", None)
            mod_info["limit_method"] = getattr(mod, "limit_method", None)
        elif mod.type == "SOLIDIFY":
            mod_info["thickness"] = getattr(mod, "thickness", None)
            mod_info["offset"] = getattr(mod, "offset", None)
        elif mod.type == "MIRROR":
            mod_info["use_axis"] = [getattr(mod, f"use_axis_{axis.lower()}", False) for axis in ("X", "Y", "Z")]
        elif mod.type == "ARRAY":
            mod_info["count"] = getattr(mod, "count", None)
            mod_info["relative_offset_displace"] = list(getattr(mod, "relative_offset_displace", []))

        modifiers_data.append(mod_info)

    return {
        "object_name": obj.name,
        "total": len(modifiers_data),
        "modifiers": modifiers_data,
    }


@register_operation("modifier.add")
def add_modifier_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new modifier to an object and configure its initial properties."""
    obj = _get_object_with_modifiers(args.get("object_name") or args.get("name"))
    mod_type = str(args.get("modifier_type") or args.get("type")).upper()
    name = args.get("name") or mod_type.capitalize()
    properties = args.get("properties") or {}

    mod = obj.modifiers.new(name=name, type=mod_type)

    # Configure any passed properties
    for prop_name, prop_val in properties.items():
        if hasattr(mod, prop_name):
            try:
                setattr(mod, prop_name, prop_val)
            except Exception as exc:
                print(f"[Blender AI Control] Warning: Failed setting property {prop_name}={prop_val}: {exc}")

    return {
        "object_name": obj.name,
        "modifier_name": mod.name,
        "modifier_type": mod.type,
    }


@register_operation("modifier.configure")
def configure_modifier_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Update settings on an existing modifier."""
    obj = _get_object_with_modifiers(args.get("object_name") or args.get("name"))
    mod_name = args.get("modifier_name") or args.get("name")
    properties = args.get("properties") or {}

    if not mod_name:
        raise ValueError("Missing required argument: 'modifier_name'")

    mod = obj.modifiers.get(mod_name)
    if not mod:
        raise KeyError(f"Modifier '{mod_name}' not found on object '{obj.name}'")

    updated = {}
    for prop_name, prop_val in properties.items():
        if hasattr(mod, prop_name):
            setattr(mod, prop_name, prop_val)
            updated[prop_name] = prop_val
        else:
            raise AttributeError(f"Modifier '{mod_name}' has no attribute '{prop_name}'")

    return {
        "object_name": obj.name,
        "modifier_name": mod.name,
        "updated_properties": updated,
    }


@register_operation("modifier.apply")
def apply_modifier_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Permanently apply a modifier to geometry."""
    obj = _get_object_with_modifiers(args.get("object_name") or args.get("name"))
    mod_name = args.get("modifier_name")

    if not mod_name:
        raise ValueError("Missing required argument: 'modifier_name'")

    mod = obj.modifiers.get(mod_name)
    if not mod:
        raise KeyError(f"Modifier '{mod_name}' not found on object '{obj.name}'")

    # Set as active object
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.modifier_apply(modifier=mod.name)

    return {
        "applied": True,
        "object_name": obj.name,
        "modifier_name": mod_name,
    }


@register_operation("modifier.remove")
def remove_modifier_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Remove a modifier from an object."""
    obj = _get_object_with_modifiers(args.get("object_name") or args.get("name"))
    mod_name = args.get("modifier_name")

    if not mod_name:
        raise ValueError("Missing required argument: 'modifier_name'")

    mod = obj.modifiers.get(mod_name)
    if not mod:
        raise KeyError(f"Modifier '{mod_name}' not found on object '{obj.name}'")

    obj.modifiers.remove(mod)

    return {
        "removed": True,
        "object_name": obj.name,
        "modifier_name": mod_name,
    }


@register_operation("modifier.reorder")
def reorder_modifier_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Move modifier UP or DOWN in the stack."""
    obj = _get_object_with_modifiers(args.get("object_name") or args.get("name"))
    mod_name = args.get("modifier_name")
    direction = str(args.get("direction", "UP")).upper()

    if not mod_name:
        raise ValueError("Missing required argument: 'modifier_name'")

    mod = obj.modifiers.get(mod_name)
    if not mod:
        raise KeyError(f"Modifier '{mod_name}' not found on object '{obj.name}'")

    bpy.context.view_layer.objects.active = obj
    if direction == "UP":
        bpy.ops.object.modifier_move_up(modifier=mod_name)
    elif direction == "DOWN":
        bpy.ops.object.modifier_move_down(modifier=mod_name)
    else:
        raise ValueError("Direction must be 'UP' or 'DOWN'")

    order = [m.name for m in obj.modifiers]
    return {
        "object_name": obj.name,
        "modifier_name": mod_name,
        "current_order": order,
    }
