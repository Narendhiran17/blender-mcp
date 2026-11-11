"""Animation and timeline operations executing on Blender's main thread."""

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


@register_operation("animation.create_keyframe")
def create_keyframe_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a keyframe on an object for a specific property at a given frame."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    if not obj_name:
        raise ValueError("Missing 'object_name'")

    data_path = args.get("data_path", "location")
    frame = float(args.get("frame", 1.0))
    value = args.get("value")
    index = int(args.get("index", -1))

    obj = _get_object(obj_name)

    # If a value is provided, update property before inserting keyframe
    if value is not None:
        if hasattr(obj, data_path):
            prop = getattr(obj, data_path)
            if index >= 0 and hasattr(prop, "__getitem__"):
                prop[index] = float(value)
            elif isinstance(value, (list, tuple)) and hasattr(prop, "__len__"):
                for i, v in enumerate(value):
                    if i < len(prop):
                        prop[i] = float(v)
            else:
                setattr(obj, data_path, value)

    if index >= 0:
        obj.keyframe_insert(data_path=data_path, frame=frame, index=index)
    else:
        obj.keyframe_insert(data_path=data_path, frame=frame)

    action_name = None
    if obj.animation_data and obj.animation_data.action:
        action_name = obj.animation_data.action.name

    return {
        "object_name": obj.name,
        "data_path": data_path,
        "frame": frame,
        "index": index,
        "action_name": action_name,
    }


@register_operation("animation.inspect")
def inspect_animation_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect animation actions, fcurves, and keyframe points on an object."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    if not obj_name:
        raise ValueError("Missing 'object_name'")

    obj = _get_object(obj_name)
    anim_data = obj.animation_data

    if not anim_data or not anim_data.action:
        return {
            "object_name": obj.name,
            "has_animation": False,
            "action_name": None,
            "fcurve_count": 0,
            "fcurves": [],
            "frame_range": [0.0, 0.0],
        }

    action = anim_data.action
    fcurves_info = []
    min_frame = float("inf")
    max_frame = float("-inf")

    for fc in action.fcurves:
        kps = []
        for kp in fc.keyframe_points:
            kps.append({
                "frame": round(kp.co[0], 2),
                "value": round(kp.co[1], 4),
                "interpolation": kp.interpolation,
            })
            if kp.co[0] < min_frame:
                min_frame = kp.co[0]
            if kp.co[0] > max_frame:
                max_frame = kp.co[0]

        fcurves_info.append({
            "data_path": fc.data_path,
            "array_index": fc.array_index,
            "keyframe_count": len(kps),
            "keyframes": kps,
        })

    frame_range = [round(min_frame, 2), round(max_frame, 2)] if min_frame != float("inf") else [0.0, 0.0]

    return {
        "object_name": obj.name,
        "has_animation": True,
        "action_name": action.name,
        "fcurve_count": len(fcurves_info),
        "fcurves": fcurves_info,
        "frame_range": frame_range,
    }


@register_operation("animation.configure")
def configure_animation_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure keyframe interpolation, clear animation data, or delete keyframes."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    obj_name = args.get("object_name")
    if not obj_name:
        raise ValueError("Missing 'object_name'")

    obj = _get_object(obj_name)
    clear_all = args.get("clear_all", False)
    if clear_all:
        if obj.animation_data:
            obj.animation_data_clear()
        return {
            "object_name": obj.name,
            "action_cleared": True,
            "modified_keyframes": 0,
            "deleted_keyframes": 0,
        }

    anim_data = obj.animation_data
    if not anim_data or not anim_data.action:
        return {
            "object_name": obj.name,
            "action_cleared": False,
            "modified_keyframes": 0,
            "deleted_keyframes": 0,
            "message": "No animation data found on object",
        }

    data_path_filter = args.get("data_path")
    interpolation = args.get("interpolation")
    delete_frame = args.get("delete_frame")

    action = anim_data.action
    modified_count = 0
    deleted_count = 0

    for fc in action.fcurves:
        if data_path_filter and fc.data_path != data_path_filter:
            continue

        if delete_frame is not None:
            target_f = float(delete_frame)
            to_remove = [kp for kp in fc.keyframe_points if abs(kp.co[0] - target_f) < 0.001]
            for kp in to_remove:
                fc.keyframe_points.remove(kp)
                deleted_count += 1

        if interpolation:
            for kp in fc.keyframe_points:
                kp.interpolation = interpolation
                modified_count += 1

    return {
        "object_name": obj.name,
        "action_cleared": False,
        "modified_keyframes": modified_count,
        "deleted_keyframes": deleted_count,
        "interpolation": interpolation,
    }


@register_operation("animation.playback_range")
def playback_range_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect or configure the scene timeline playback range and framerate."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    frame_start = args.get("frame_start")
    frame_end = args.get("frame_end")
    frame_current = args.get("frame_current")
    fps = args.get("fps")

    if frame_start is not None:
        scene.frame_start = int(frame_start)
    if frame_end is not None:
        scene.frame_end = int(frame_end)
    if frame_current is not None:
        scene.frame_set(int(frame_current))
    if fps is not None:
        scene.render.fps = int(fps)

    total_frames = max(0, scene.frame_end - scene.frame_start + 1)
    duration_sec = total_frames / scene.render.fps if scene.render.fps > 0 else 0.0

    return {
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "fps": scene.render.fps,
        "total_frames": total_frames,
        "duration_seconds": round(duration_sec, 2),
    }
