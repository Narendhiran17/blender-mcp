"""Geometry Nodes operations executing on Blender's main thread."""

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


@register_operation("geometry_nodes.list_groups")
def list_geometry_node_groups_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """List all Geometry Node groups in the active blend file."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    groups_data = []
    for ng in bpy.data.node_groups:
        if getattr(ng, "type", "") == "GEOMETRY":
            inputs = []
            outputs = []
            if hasattr(ng, "interface"):
                for item in ng.interface.items_tree:
                    if getattr(item, "item_type", "") == "SOCKET":
                        if item.in_out == "INPUT":
                            inputs.append(item.name)
                        elif item.in_out == "OUTPUT":
                            outputs.append(item.name)
            groups_data.append({
                "name": ng.name,
                "users": ng.users,
                "input_count": len(inputs),
                "output_count": len(outputs),
                "inputs": inputs,
                "outputs": outputs,
            })

    return {
        "count": len(groups_data),
        "groups": groups_data,
    }


@register_operation("geometry_nodes.inspect")
def inspect_geometry_nodes_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect a Geometry Nodes modifier on an object or a node group directly."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    mod_name = args.get("modifier_name", "GeometryNodes")
    group_name = args.get("group_name")

    ng = None
    mod = None
    obj = None

    if obj_name:
        obj = _get_object(obj_name)
        mod = obj.modifiers.get(mod_name)
        if not mod:
            raise KeyError(f"Modifier '{mod_name}' not found on object '{obj_name}'")
        if mod.type != "NODES":
            raise ValueError(f"Modifier '{mod_name}' is of type '{mod.type}', expected 'NODES'")
        ng = mod.node_group
    elif group_name:
        ng = bpy.data.node_groups.get(group_name)
        if not ng:
            raise KeyError(f"Geometry Node group '{group_name}' not found")
    else:
        raise ValueError("Must provide either 'object_name' or 'group_name' to inspect Geometry Nodes")

    inputs_info = []
    outputs_info = []
    if ng and hasattr(ng, "interface"):
        for item in ng.interface.items_tree:
            if getattr(item, "item_type", "") == "SOCKET":
                socket_data = {
                    "name": item.name,
                    "identifier": item.identifier,
                    "socket_type": getattr(item, "socket_type", ""),
                }
                # Default value if present
                def_val = getattr(item, "default_value", None)
                if def_val is not None:
                    if hasattr(def_val, "__iter__") and not isinstance(def_val, str):
                        socket_data["default_value"] = [round(float(v), 4) for v in def_val]
                    elif isinstance(def_val, float):
                        socket_data["default_value"] = round(def_val, 4)
                    else:
                        socket_data["default_value"] = def_val

                # If inspecting an active modifier, get the overridden value
                if mod is not None and item.in_out == "INPUT":
                    if item.identifier in mod:
                        val = mod[item.identifier]
                        if hasattr(val, "__iter__") and not isinstance(val, str):
                            socket_data["current_value"] = [round(float(v), 4) for v in val]
                        elif isinstance(val, float):
                            socket_data["current_value"] = round(val, 4)
                        else:
                            socket_data["current_value"] = val
                    else:
                        socket_data["current_value"] = socket_data.get("default_value")

                if item.in_out == "INPUT":
                    inputs_info.append(socket_data)
                elif item.in_out == "OUTPUT":
                    outputs_info.append(socket_data)

    nodes_summary = {}
    if ng and hasattr(ng, "nodes"):
        for node in ng.nodes:
            t = node.bl_idname
            nodes_summary[t] = nodes_summary.get(t, 0) + 1

    return {
        "object_name": obj_name,
        "modifier_name": mod.name if mod else None,
        "group_name": ng.name if ng else None,
        "input_count": len(inputs_info),
        "output_count": len(outputs_info),
        "inputs": inputs_info,
        "outputs": outputs_info,
        "nodes_summary": nodes_summary,
    }


@register_operation("geometry_nodes.assign_group")
def assign_geometry_nodes_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Assign or create a Geometry Nodes modifier and link a node group."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    if not obj_name:
        raise ValueError("Missing 'object_name'")

    obj = _get_object(obj_name)
    mod_name = args.get("modifier_name", "GeometryNodes")
    group_name = args.get("group_name")
    create_if_missing = args.get("create_if_missing", True)

    # Get or add modifier
    mod = obj.modifiers.get(mod_name)
    created_mod = False
    if not mod:
        mod = obj.modifiers.new(name=mod_name, type="NODES")
        created_mod = True
    elif mod.type != "NODES":
        raise ValueError(f"Existing modifier '{mod_name}' is type '{mod.type}', not 'NODES'")

    # Link or create node group
    if group_name:
        ng = bpy.data.node_groups.get(group_name)
        if not ng:
            if create_if_missing:
                ng = bpy.data.node_groups.new(name=group_name, type="GeometryNodeTree")
                in_node = ng.nodes.new("NodeGroupInput")
                out_node = ng.nodes.new("NodeGroupOutput")
                in_node.location = (-200, 0)
                out_node.location = (200, 0)
                ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
                ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
                ng.links.new(in_node.outputs[0], out_node.inputs[0])
            else:
                raise KeyError(f"Geometry Node group '{group_name}' not found")
        mod.node_group = ng
    elif not mod.node_group:
        default_name = f"{obj_name}_GeometryNodes"
        ng = bpy.data.node_groups.new(name=default_name, type="GeometryNodeTree")
        in_node = ng.nodes.new("NodeGroupInput")
        out_node = ng.nodes.new("NodeGroupOutput")
        in_node.location = (-200, 0)
        out_node.location = (200, 0)
        ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        ng.links.new(in_node.outputs[0], out_node.inputs[0])
        mod.node_group = ng

    return {
        "object_name": obj.name,
        "modifier_name": mod.name,
        "group_name": mod.node_group.name if mod.node_group else None,
        "created_modifier": created_mod,
    }


@register_operation("geometry_nodes.configure")
def configure_geometry_nodes_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure input parameters of a Geometry Nodes modifier on an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    mod_name = args.get("modifier_name", "GeometryNodes")
    inputs = args.get("inputs", {})

    obj = _get_object(obj_name)
    mod = obj.modifiers.get(mod_name)
    if not mod:
        raise KeyError(f"Modifier '{mod_name}' not found on object '{obj_name}'")
    if mod.type != "NODES":
        raise ValueError(f"Modifier '{mod_name}' is type '{mod.type}', expected 'NODES'")
    if not mod.node_group:
        raise ValueError(f"Modifier '{mod_name}' has no linked node group")

    ng = mod.node_group
    updated_inputs = {}

    # Map name -> identifier and identifier -> identifier
    socket_map = {}
    if hasattr(ng, "interface"):
        for item in ng.interface.items_tree:
            if getattr(item, "item_type", "") == "SOCKET" and item.in_out == "INPUT":
                socket_map[item.name] = item.identifier
                socket_map[item.identifier] = item.identifier

    for key, value in inputs.items():
        identifier = socket_map.get(key)
        if identifier:
            mod[identifier] = value
            updated_inputs[key] = value
        elif key in mod.keys():
            mod[key] = value
            updated_inputs[key] = value
        else:
            raise KeyError(f"Socket input '{key}' not found on Geometry Node group '{ng.name}'")

    return {
        "object_name": obj.name,
        "modifier_name": mod.name,
        "group_name": ng.name,
        "updated_inputs": updated_inputs,
    }
