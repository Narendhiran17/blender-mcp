"""Lighting, camera, and environment tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_lighting_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register lighting, camera, and environment tools with the MCP server."""

    @server.tool(
        name="blender_create_light",
        description="Create a light source in the scene (light_type: 'POINT', 'SUN', 'SPOT', 'AREA') with location, power/energy, and color.",
    )
    async def blender_create_light(
        light_type: str = "POINT",
        name: Optional[str] = None,
        location: List[float] = [0.0, 0.0, 5.0],
        rotation: List[float] = [0.0, 0.0, 0.0],
        energy: float = 1000.0,
        color: List[float] = [1.0, 1.0, 1.0],
    ) -> Dict[str, Any]:
        """Create a light object."""
        args: Dict[str, Any] = {
            "light_type": light_type,
            "location": location,
            "rotation": rotation,
            "energy": energy,
            "color": color,
        }
        if name:
            args["name"] = name
        return await client.execute("light.create", args)

    @server.tool(
        name="blender_configure_light",
        description="Configure parameters of an existing light (energy, color, light_type, spot_size).",
    )
    async def blender_configure_light(
        name: str,
        energy: Optional[float] = None,
        color: Optional[List[float]] = None,
        light_type: Optional[str] = None,
        spot_size: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Configure light properties."""
        args: Dict[str, Any] = {"name": name}
        if energy is not None:
            args["energy"] = energy
        if color is not None:
            args["color"] = color
        if light_type is not None:
            args["light_type"] = light_type
        if spot_size is not None:
            args["spot_size"] = spot_size
        return await client.execute("light.configure", args)

    @server.tool(
        name="blender_create_camera",
        description="Create a camera object with location, rotation, focal length (mm), and clipping ranges.",
    )
    async def blender_create_camera(
        name: str = "Camera",
        location: List[float] = [0.0, -5.0, 2.0],
        rotation: List[float] = [1.3, 0.0, 0.0],
        focal_length: float = 50.0,
        clip_start: float = 0.1,
        clip_end: float = 1000.0,
        set_active: bool = True,
    ) -> Dict[str, Any]:
        """Create a camera."""
        return await client.execute(
            "camera.create",
            {
                "name": name,
                "location": location,
                "rotation": rotation,
                "focal_length": focal_length,
                "clip_start": clip_start,
                "clip_end": clip_end,
                "set_active": set_active,
            },
        )

    @server.tool(
        name="blender_configure_camera",
        description="Configure camera focal length (mm) or clipping distance.",
    )
    async def blender_configure_camera(
        name: str,
        focal_length: Optional[float] = None,
        clip_start: Optional[float] = None,
        clip_end: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Configure camera settings."""
        args: Dict[str, Any] = {"name": name}
        if focal_length is not None:
            args["focal_length"] = focal_length
        if clip_start is not None:
            args["clip_start"] = clip_start
        if clip_end is not None:
            args["clip_end"] = clip_end
        return await client.execute("camera.configure", args)

    @server.tool(
        name="blender_set_active_camera",
        description="Set the specified camera as the active rendering camera for the scene.",
    )
    async def blender_set_active_camera(name: str) -> Dict[str, Any]:
        """Set active scene camera."""
        return await client.execute("camera.set_active", {"name": name})

    @server.tool(
        name="blender_configure_world",
        description="Configure world illumination (background color, strength multiplier, or HDRI environment map).",
    )
    async def blender_configure_world(
        color: Optional[List[float]] = None,
        strength: Optional[float] = None,
        hdri_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure world background."""
        args: Dict[str, Any] = {}
        if color is not None:
            args["color"] = color
        if strength is not None:
            args["strength"] = strength
        if hdri_path is not None:
            args["hdri_path"] = hdri_path
        return await client.execute("world.configure", args)

    @server.tool(
        name="blender_inspect_environment",
        description="Inspect scene illumination: active camera, world background settings, and all light objects in the scene.",
    )
    async def blender_inspect_environment() -> Dict[str, Any]:
        """Inspect environment, active camera, and lights."""
        return await client.execute("environment.inspect")
