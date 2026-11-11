"""Object tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_object_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register object manipulation tools with the MCP server."""

    @server.tool(
        name="blender_create_primitive",
        description="Create a 3D primitive mesh in Blender (e.g., CUBE, UV_SPHERE, CYLINDER, PLANE, CONE, TORUS) with optional transforms and name.",
    )
    async def blender_create_primitive(
        primitive_type: str = "CUBE",
        name: Optional[str] = None,
        location: List[float] = [0.0, 0.0, 0.0],
        rotation: List[float] = [0.0, 0.0, 0.0],
        scale: List[float] = [1.0, 1.0, 1.0],
        size: float = 2.0,
    ) -> Dict[str, Any]:
        """Create a primitive mesh object in Blender."""
        args = {
            "primitive_type": primitive_type,
            "name": name,
            "location": location,
            "rotation": rotation,
            "scale": scale,
            "size": size,
        }
        return await client.execute("object.create_primitive", args)

    @server.tool(
        name="blender_inspect_object",
        description="Inspect an object in Blender to inspect its transforms, dimensions, vertex counts, materials, and modifiers.",
    )
    async def blender_inspect_object(name: str) -> Dict[str, Any]:
        """Inspect detailed properties of an object in Blender."""
        return await client.execute("object.inspect", {"name": name})

    @server.tool(
        name="blender_list_objects",
        description="List objects in the active Blender scene, optionally filtered by type (e.g. 'MESH', 'CAMERA', 'LIGHT').",
    )
    async def blender_list_objects(object_type: Optional[str] = None) -> Dict[str, Any]:
        """List objects in the active scene."""
        args = {}
        if object_type:
            args["type"] = object_type
        return await client.execute("object.list", args)
