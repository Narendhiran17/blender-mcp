"""Lighting, camera, and environment operations executing on Blender's main thread."""

import math
import os
from typing import Any, Dict, List, Optional
from ..bridge.serializers import serialize_blender_value
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


@register_operation("light.create")
def create_light_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a light object (POINT, SUN, SPOT, AREA)."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    light_type = str(args.get("light_type", "POINT")).upper()
    name = args.get("name") or f"{light_type.capitalize()}Light"
    location = tuple(args.get("location", [0.0, 0.0, 5.0]))
    rotation = tuple(args.get("rotation", [0.0, 0.0, 0.0]))
    energy = float(args.get("energy", 1000.0 if light_type != "SUN" else 5.0))
    color = tuple(args.get("color", [1.0, 1.0, 1.0]))

    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = energy
    light_data.color = color[:3]

    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    light_obj.location = location
    light_obj.rotation_euler = rotation

    bpy.context.scene.collection.objects.link(light_obj)

    return {
        "name": light_obj.name,
        "type": "LIGHT",
        "light_type": light_data.type,
        "location": list(light_obj.location),
        "energy": round(light_data.energy, 4),
        "color": list(light_data.color),
    }


@register_operation("light.configure")
def configure_light_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure parameters of an existing light."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "LIGHT":
        raise ValueError(f"Object '{name}' is not a light object")

    light_data = obj.data
    updated = {}

    if "energy" in args and args["energy"] is not None:
        light_data.energy = float(args["energy"])
        updated["energy"] = round(light_data.energy, 4)

    if "color" in args and args["color"] is not None:
        col = tuple(args["color"][:3])
        light_data.color = col
        updated["color"] = list(col)

    if "light_type" in args and args["light_type"] is not None:
        new_type = str(args["light_type"]).upper()
        light_data.type = new_type
        updated["light_type"] = new_type

    if "spot_size" in args and args["spot_size"] is not None and hasattr(light_data, "spot_size"):
        light_data.spot_size = math.radians(float(args["spot_size"]))
        updated["spot_size"] = float(args["spot_size"])

    return {
        "name": obj.name,
        "light_type": light_data.type,
        "updated": updated,
    }


@register_operation("camera.create")
def create_camera_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a camera object with optional transforms and focal length."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name", "Camera")
    location = tuple(args.get("location", [0.0, -5.0, 2.0]))
    rotation = tuple(args.get("rotation", [math.radians(75.0), 0.0, 0.0]))
    focal_length = float(args.get("focal_length", 50.0))
    clip_start = float(args.get("clip_start", 0.1))
    clip_end = float(args.get("clip_end", 1000.0))
    set_active = bool(args.get("set_active", True))

    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = focal_length
    cam_data.clip_start = clip_start
    cam_data.clip_end = clip_end

    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation

    bpy.context.scene.collection.objects.link(cam_obj)

    if set_active:
        bpy.context.scene.camera = cam_obj

    return {
        "name": cam_obj.name,
        "type": "CAMERA",
        "location": list(cam_obj.location),
        "rotation_euler": list(cam_obj.rotation_euler),
        "focal_length": round(cam_data.lens, 4),
        "is_active_camera": (bpy.context.scene.camera == cam_obj),
    }


@register_operation("camera.configure")
def configure_camera_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure focal length, clipping ranges, and camera parameters."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "CAMERA":
        raise ValueError(f"Object '{name}' is not a camera")

    cam = obj.data
    updated = {}

    if "focal_length" in args and args["focal_length"] is not None:
        cam.lens = float(args["focal_length"])
        updated["focal_length"] = round(cam.lens, 4)

    if "clip_start" in args and args["clip_start"] is not None:
        cam.clip_start = float(args["clip_start"])
        updated["clip_start"] = round(cam.clip_start, 4)

    if "clip_end" in args and args["clip_end"] is not None:
        cam.clip_end = float(args["clip_end"])
        updated["clip_end"] = round(cam.clip_end, 4)

    return {
        "name": obj.name,
        "focal_length": round(cam.lens, 4),
        "updated": updated,
    }


@register_operation("camera.set_active")
def set_active_camera_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set the active scene rendering camera."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing required argument: 'name'")

    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "CAMERA":
        raise ValueError(f"Object '{name}' is not a camera")

    bpy.context.scene.camera = obj
    return {
        "active_camera": obj.name,
    }


@register_operation("world.configure")
def configure_world_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure world illumination, background color, strength, or HDRI."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    bg_node = None
    for n in nodes:
        if n.type == "BACKGROUND":
            bg_node = n
            break

    if not bg_node:
        bg_node = nodes.new(type="ShaderNodeBackground")

    color = args.get("color")
    if color is not None:
        col = tuple(color[:3]) + ((1.0,) if len(color) == 3 else ())
        bg_node.inputs["Color"].default_value = col

    strength = args.get("strength")
    if strength is not None:
        bg_node.inputs["Strength"].default_value = float(strength)

    hdri_path = args.get("hdri_path")
    if hdri_path:
        if not os.path.exists(hdri_path):
            raise FileNotFoundError(f"HDRI file not found: {hdri_path}")
        hdri_image = bpy.data.images.load(hdri_path, check_existing=True)
        env_node = nodes.new(type="ShaderNodeTexEnvironment")
        env_node.image = hdri_image
        env_node.location = (bg_node.location.x - 300, bg_node.location.y)
        links.new(env_node.outputs["Color"], bg_node.inputs["Color"])

    bg_color = bg_node.inputs["Color"].default_value
    bg_strength = float(bg_node.inputs["Strength"].default_value)
    return {
        "world_name": world.name,
        "color": [round(c, 4) for c in bg_color] if hasattr(bg_color, "__iter__") else bg_color,
        "strength": round(bg_strength, 4),
        "has_hdri": bool(hdri_path),
    }


@register_operation("environment.inspect")
def inspect_environment_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect world illumination, active camera, and all lighting objects."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    lights = []
    for obj in scene.objects:
        if obj.type == "LIGHT":
            lights.append({
                "name": obj.name,
                "light_type": obj.data.type,
                "location": list(obj.location),
                "energy": round(obj.data.energy, 4),
                "color": list(obj.data.color),
            })

    active_cam = scene.camera.name if scene.camera else None
    world_name = scene.world.name if scene.world else None

    return {
        "active_camera": active_cam,
        "world": world_name,
        "lights_count": len(lights),
        "lights": lights,
    }
