"""System tools for MCP Server."""

from typing import Any, Dict
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_system_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register system and health tools with the MCP server."""

    @server.tool(
        name="blender_health",
        description="Check if the local Blender bridge is running and reachable.",
    )
    async def blender_health() -> Dict[str, Any]:
        """Check the health of the Blender bridge connection."""
        return await client.check_health()

    @server.tool(
        name="blender_status",
        description="Get current status of Blender: version, active scene, object counts, and active selection.",
    )
    async def blender_status() -> Dict[str, Any]:
        """Retrieve real-time project and scene status from Blender."""
        return await client.get_status()

    @server.tool(
        name="blender_version",
        description="Get Blender version and build platform information.",
    )
    async def blender_version() -> Dict[str, Any]:
        """Retrieve Blender build and version information."""
        return await client.execute("system.version")
