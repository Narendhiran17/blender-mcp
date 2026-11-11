"""Rendering and compositing operations executing on Blender's main thread."""

import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..security.path_policy import is_safe_workspace_path
from .registry import register_operation

try:
    import bpy
except ImportError:
    bpy = None


def _resolve_engine_name(engine_input: str) -> str:
    """Normalize and resolve render engine identifier across Blender versions."""
    upper = engine_input.strip().upper()
    if upper in ("CYCLES", "BLENDER_WORKBENCH"):
        return upper
    if "EEVEE" in upper:
        # Check available engine identifiers in Blender
        if bpy is not None:
            available = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
            if "BLENDER_EEVEE_NEXT" in available:
                return "BLENDER_EEVEE_NEXT"
            if "BLENDER_EEVEE" in available:
                return "BLENDER_EEVEE"
        return "BLENDER_EEVEE_NEXT"
    return upper


@register_operation("render.configure")
def configure_render_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure render engine, resolution, samples, output format, and paths."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    render = scene.render

    if "engine" in args and args["engine"]:
        resolved_engine = _resolve_engine_name(args["engine"])
        render.engine = resolved_engine

    if "resolution_x" in args and args["resolution_x"] is not None:
        render.resolution_x = int(args["resolution_x"])
    if "resolution_y" in args and args["resolution_y"] is not None:
        render.resolution_y = int(args["resolution_y"])
    if "resolution_percentage" in args and args["resolution_percentage"] is not None:
        render.resolution_percentage = int(args["resolution_percentage"])

    if "samples" in args and args["samples"] is not None:
        samples_val = int(args["samples"])
        if hasattr(scene, "cycles"):
            scene.cycles.samples = samples_val
        if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples_val

    if "file_format" in args and args["file_format"]:
        fmt = args["file_format"].upper()
        if fmt in ("PNG", "JPEG", "OPEN_EXR", "TIFF", "TARGA"):
            render.image_settings.file_format = fmt

    if "color_mode" in args and args["color_mode"]:
        mode = args["color_mode"].upper()
        if mode in ("RGB", "RGBA", "BW"):
            render.image_settings.color_mode = mode

    if "filepath" in args and args["filepath"]:
        target_path = args["filepath"]
        if not is_safe_workspace_path(target_path):
            raise PermissionError(f"Filepath '{target_path}' is outside allowed workspaces or targets a restricted system location")
        render.filepath = target_path

    if "transparent_background" in args and args["transparent_background"] is not None:
        render.film_transparent = bool(args["transparent_background"])

    effective_x = int(render.resolution_x * (render.resolution_percentage / 100.0))
    effective_y = int(render.resolution_y * (render.resolution_percentage / 100.0))

    return {
        "engine": render.engine,
        "resolution_x": render.resolution_x,
        "resolution_y": render.resolution_y,
        "resolution_percentage": render.resolution_percentage,
        "effective_width": effective_x,
        "effective_height": effective_y,
        "file_format": render.image_settings.file_format,
        "color_mode": render.image_settings.color_mode,
        "filepath": render.filepath,
        "transparent_background": render.film_transparent,
    }


@register_operation("render.preview")
def render_preview_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Render a fast preview image of the current frame and return its file metadata."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    render = scene.render

    output_path = args.get("output_path")
    if output_path:
        if not is_safe_workspace_path(output_path):
            raise PermissionError(f"Preview path '{output_path}' is outside allowed workspaces")
        target_file = Path(output_path).resolve()
    else:
        # Default to system temp dir
        temp_dir = Path(tempfile.gettempdir())
        target_file = temp_dir / f"blender_preview_{uuid.uuid4().hex[:8]}.png"

    target_file.parent.mkdir(parents=True, exist_ok=True)

    # Save original settings
    orig_filepath = render.filepath
    orig_pct = render.resolution_percentage
    orig_format = render.image_settings.file_format

    preview_pct = int(args.get("resolution_percentage", 50))
    render.resolution_percentage = preview_pct
    render.filepath = str(target_file)
    render.image_settings.file_format = "PNG"

    start_time = time.time()
    try:
        bpy.ops.render.render(write_still=True)
        render_duration = round(time.time() - start_time, 3)
    finally:
        # Restore settings
        render.filepath = orig_filepath
        render.resolution_percentage = orig_pct
        render.image_settings.file_format = orig_format

    # Verify output file
    if not target_file.exists():
        # Check if Blender appended an extension like .png
        if Path(str(target_file) + ".png").exists():
            target_file = Path(str(target_file) + ".png")
        else:
            raise RuntimeError(f"Render failed: file '{target_file}' was not created")

    effective_x = int(render.resolution_x * (preview_pct / 100.0))
    effective_y = int(render.resolution_y * (preview_pct / 100.0))
    file_size = target_file.stat().st_size

    return {
        "status": "success",
        "filepath": str(target_file),
        "width": effective_x,
        "height": effective_y,
        "file_size_bytes": file_size,
        "render_time_seconds": render_duration,
        "engine": render.engine,
    }


@register_operation("render.status")
def render_status_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve current render settings, active camera, and timeline properties."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    render = scene.render

    effective_x = int(render.resolution_x * (render.resolution_percentage / 100.0))
    effective_y = int(render.resolution_y * (render.resolution_percentage / 100.0))

    return {
        "engine": render.engine,
        "resolution_x": render.resolution_x,
        "resolution_y": render.resolution_y,
        "resolution_percentage": render.resolution_percentage,
        "effective_width": effective_x,
        "effective_height": effective_y,
        "fps": scene.render.fps,
        "frame_current": scene.frame_current,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "active_camera": scene.camera.name if scene.camera else None,
        "filepath": render.filepath,
        "file_format": render.image_settings.file_format,
        "transparent_background": render.film_transparent,
    }


@register_operation("compositor.inspect")
def inspect_compositor_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect the scene compositor node tree, active nodes, and links."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    use_nodes = scene.use_nodes

    nodes_info = []
    links_info = []

    if scene.node_tree:
        tree = scene.node_tree
        for node in tree.nodes:
            nodes_info.append({
                "name": node.name,
                "type": node.bl_idname,
                "label": node.label,
                "inputs": [inp.name for inp in node.inputs],
                "outputs": [out.name for out in node.outputs],
            })

        for link in tree.links:
            links_info.append({
                "from_node": link.from_node.name,
                "from_socket": link.from_socket.name,
                "to_node": link.to_node.name,
                "to_socket": link.to_socket.name,
            })

    return {
        "use_nodes": use_nodes,
        "node_count": len(nodes_info),
        "link_count": len(links_info),
        "nodes": nodes_info,
        "links": links_info,
    }


@register_operation("compositor.configure")
def configure_compositor_operation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Configure compositing nodes, enable node tree, or add compositor nodes."""
    if bpy is None:
        raise RuntimeError("bpy module is not available")

    scene = bpy.context.scene
    use_nodes = args.get("use_nodes", True)
    scene.use_nodes = bool(use_nodes)

    added_node_name = None
    if scene.use_nodes and scene.node_tree:
        add_type = args.get("add_node_type")
        if add_type:
            new_node = scene.node_tree.nodes.new(add_type)
            if "node_name" in args and args["node_name"]:
                new_node.name = args["node_name"]
            added_node_name = new_node.name

    return {
        "use_nodes": scene.use_nodes,
        "node_count": len(scene.node_tree.nodes) if scene.node_tree else 0,
        "added_node": added_node_name,
    }
