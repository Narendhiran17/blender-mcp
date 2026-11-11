"""MCP resources for Blender AI Control."""

from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_resources(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register read-oriented resources with MCP server."""

    @server.resource("blender://system/info")
    async def get_system_info() -> str:
        """Blender system and connection information."""
        health = await client.check_health()
        version = await client.execute("system.version")
        return f"Blender Health: {health}\nVersion Info: {version}"

    @server.resource("blender://scene/active")
    async def get_active_scene() -> str:
        """Active scene summary."""
        status = await client.get_status()
        return f"Scene Status: {status}"

    @server.resource("blender://scene/objects")
    async def get_scene_objects() -> str:
        """Object inventory in the active scene."""
        result = await client.execute("object.list")
        return f"Scene Objects: {result}"
