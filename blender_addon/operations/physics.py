"""Physics and simulation operations executing on Blender's main thread."""

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


@register_operation("physics.configure_rigidbody")
def configure_rigidbody_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure or add rigid body physics to an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing 'name'")

    obj = _get_object(name)

    # Ensure rigid body component exists
    if not obj.rigid_body:
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.rigidbody.object_add()
        finally:
            if prev_active and prev_active != obj:
                bpy.context.view_layer.objects.active = prev_active

    rb = obj.rigid_body
    if not rb:
        raise RuntimeError(f"Failed to add rigid body to object '{name}'")

    if "type" in args:
        rb.type = args["type"]
    if "mass" in args and args["mass"] is not None:
        rb.mass = float(args["mass"])
    if "friction" in args and args["friction"] is not None:
        rb.friction = float(args["friction"])
    if "restitution" in args and args["restitution"] is not None:
        rb.restitution = float(args["restitution"])
    if "collision_shape" in args and args["collision_shape"] is not None:
        rb.collision_shape = args["collision_shape"]
    if "kinematic" in args and args["kinematic"] is not None:
        rb.kinematic = bool(args["kinematic"])
    if "enabled" in args and args["enabled"] is not None:
        rb.enabled = bool(args["enabled"])

    return {
        "object_name": obj.name,
        "type": rb.type,
        "mass": round(rb.mass, 4),
        "friction": round(rb.friction, 4),
        "restitution": round(rb.restitution, 4),
        "collision_shape": rb.collision_shape,
        "kinematic": rb.kinematic,
        "enabled": rb.enabled,
    }


@register_operation("physics.configure_cloth")
def configure_cloth_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure or add a cloth simulation modifier to an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing 'name'")

    obj = _get_object(name)

    mod = obj.modifiers.get("Cloth")
    if not mod:
        mod = obj.modifiers.new(name="Cloth", type="CLOTH")

    cs = mod.settings
    if "mass" in args and args["mass"] is not None:
        cs.mass = float(args["mass"])
    if "tension_stiffness" in args and args["tension_stiffness"] is not None:
        cs.tension_stiffness = float(args["tension_stiffness"])
    if "compression_stiffness" in args and args["compression_stiffness"] is not None:
        cs.compression_stiffness = float(args["compression_stiffness"])
    if "shear_stiffness" in args and args["shear_stiffness"] is not None:
        cs.shear_stiffness = float(args["shear_stiffness"])
    if "bending_stiffness" in args and args["bending_stiffness"] is not None:
        cs.bending_stiffness = float(args["bending_stiffness"])
    if "shrink_factor" in args and args["shrink_factor"] is not None:
        cs.shrink_min = float(args["shrink_factor"])

    if "use_collision" in args and args["use_collision"] is not None:
        if hasattr(mod, "collision_settings"):
            mod.collision_settings.use_collision = bool(args["use_collision"])

    return {
        "object_name": obj.name,
        "modifier_name": mod.name,
        "mass": round(cs.mass, 4),
        "tension_stiffness": round(cs.tension_stiffness, 4),
        "compression_stiffness": round(cs.compression_stiffness, 4),
        "shear_stiffness": round(cs.shear_stiffness, 4),
        "bending_stiffness": round(cs.bending_stiffness, 4),
        "shrink_factor": round(cs.shrink_min, 4),
    }


@register_operation("physics.inspect")
def inspect_physics_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect all physics systems active on an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    name = args.get("name")
    if not name:
        raise ValueError("Missing 'name'")

    obj = _get_object(name)

    rb_data = None
    if obj.rigid_body:
        rb = obj.rigid_body
        rb_data = {
            "type": rb.type,
            "mass": round(rb.mass, 4),
            "friction": round(rb.friction, 4),
            "restitution": round(rb.restitution, 4),
            "collision_shape": rb.collision_shape,
            "kinematic": rb.kinematic,
            "enabled": rb.enabled,
        }

    cloth_data = None
    for mod in obj.modifiers:
        if mod.type == "CLOTH":
            cs = mod.settings
            cloth_data = {
                "modifier_name": mod.name,
                "mass": round(cs.mass, 4),
                "tension_stiffness": round(cs.tension_stiffness, 4),
                "compression_stiffness": round(cs.compression_stiffness, 4),
                "shear_stiffness": round(cs.shear_stiffness, 4),
                "bending_stiffness": round(cs.bending_stiffness, 4),
            }
            break

    collision_data = None
    for mod in obj.modifiers:
        if mod.type == "COLLISION":
            collision_data = {"modifier_name": mod.name}
            break

    particle_systems = []
    if hasattr(obj, "particle_systems"):
        for ps in obj.particle_systems:
            particle_systems.append({
                "name": ps.name,
                "type": ps.settings.type if ps.settings else None,
                "count": ps.settings.count if ps.settings else 0,
            })

    return {
        "object_name": obj.name,
        "has_physics": any([rb_data, cloth_data, collision_data, particle_systems]),
        "rigid_body": rb_data,
        "cloth": cloth_data,
        "collision": collision_data,
        "particle_systems": particle_systems,
    }


@register_operation("simulation.bake")
def bake_simulation_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Bake physics simulation cache or setup cache frame range."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    sim_type = args.get("simulation_type", "RIGIDBODY").upper()
    frame_start = args.get("frame_start")
    frame_end = args.get("frame_end")

    if sim_type in ("RIGIDBODY", "ALL"):
        if not scene.rigidbody_world:
            bpy.ops.rigidbody.world_add()

        rw = scene.rigidbody_world
        if rw and rw.point_cache:
            if frame_start is not None:
                rw.point_cache.frame_start = int(frame_start)
            if frame_end is not None:
                rw.point_cache.frame_end = int(frame_end)

            start = rw.point_cache.frame_start
            end = rw.point_cache.frame_end
            return {
                "simulation_type": "RIGIDBODY",
                "status": "configured",
                "frame_start": start,
                "frame_end": end,
                "cached": rw.point_cache.is_baked,
            }

    return {
        "simulation_type": sim_type,
        "status": "unsupported_simulation_type",
        "supported": ["RIGIDBODY"],
    }
