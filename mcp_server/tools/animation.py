"""Animation and timeline tools for MCP Server."""

from typing import Any, Dict, List, Optional, Union
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_animation_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register animation and timeline tools with the MCP server."""

    @server.tool(
        name="blender_create_keyframe",
        description="Insert a keyframe on an object for a data property (location, rotation_euler, scale) at a frame.",
    )
    async def blender_create_keyframe(
        object_name: str,
        frame: float,
        data_path: str = "location",
        value: Optional[Union[float, List[float]]] = None,
        index: int = -1,
    ) -> Dict[str, Any]:
        """Create a keyframe on an object."""
        args: Dict[str, Any] = {
            "object_name": object_name,
            "frame": frame,
            "data_path": data_path,
            "index": index,
        }
        if value is not None:
            args["value"] = value
        return await client.execute("animation.create_keyframe", args)

    @server.tool(
        name="blender_inspect_animation",
        description="Inspect actions, F-Curves, keyframe coordinates, and timeline frame range on an object.",
    )
    async def blender_inspect_animation(object_name: str) -> Dict[str, Any]:
        """Inspect animation data on an object."""
        return await client.execute("animation.inspect", {"object_name": object_name})

    @server.tool(
        name="blender_configure_animation",
        description="Configure animation keyframes (interpolation: 'BEZIER', 'LINEAR', 'CONSTANT'), delete keyframes, or clear action.",
    )
    async def blender_configure_animation(
        object_name: str,
        data_path: Optional[str] = None,
        interpolation: Optional[str] = None,
        clear_all: bool = False,
        delete_frame: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Configure or clear keyframes."""
        args: Dict[str, Any] = {
            "object_name": object_name,
            "clear_all": clear_all,
        }
        if data_path:
            args["data_path"] = data_path
        if interpolation:
            args["interpolation"] = interpolation
        if delete_frame is not None:
            args["delete_frame"] = delete_frame
        return await client.execute("animation.configure", args)

    @server.tool(
        name="blender_playback_range",
        description="Inspect or set scene timeline range: start frame, end frame, current frame, and framerate (fps).",
    )
    async def blender_playback_range(
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None,
        frame_current: Optional[int] = None,
        fps: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Inspect or configure scene playback range."""
        args: Dict[str, Any] = {}
        if frame_start is not None:
            args["frame_start"] = frame_start
        if frame_end is not None:
            args["frame_end"] = frame_end
        if frame_current is not None:
            args["frame_current"] = frame_current
        if fps is not None:
            args["fps"] = fps
        return await client.execute("animation.playback_range", args)
