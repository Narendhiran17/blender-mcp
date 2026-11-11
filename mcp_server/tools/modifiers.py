"""Modifier management tools for MCP Server."""

from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_modifier_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register modifier management tools with the MCP server."""

    @server.tool(
        name="blender_list_modifiers",
        description="List all modifiers active on an object with their types, parameters, and display flags.",
    )
    async def blender_list_modifiers(object_name: str) -> Dict[str, Any]:
        """List modifiers on an object."""
        return await client.execute("modifier.list", {"object_name": object_name})

    @server.tool(
        name="blender_add_modifier",
        description="Add a modifier to an object (e.g. 'SUBSURF', 'BEVEL', 'SOLIDIFY', 'MIRROR', 'ARRAY', 'BOOLEAN', 'DECIMATE', 'REMESH').",
    )
    async def blender_add_modifier(
        object_name: str,
        modifier_type: str,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a modifier to an object."""
        args: Dict[str, Any] = {
            "object_name": object_name,
            "modifier_type": modifier_type,
        }
        if name:
            args["name"] = name
        if properties:
            args["properties"] = properties
        return await client.execute("modifier.add", args)

    @server.tool(
        name="blender_configure_modifier",
        description="Update settings on an existing modifier (e.g. levels, thickness, width, count).",
    )
    async def blender_configure_modifier(
        object_name: str,
        modifier_name: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Configure modifier properties."""
        return await client.execute(
            "modifier.configure",
            {
                "object_name": object_name,
                "modifier_name": modifier_name,
                "properties": properties,
            },
        )

    @server.tool(
        name="blender_apply_modifier",
        description="Permanently bake/apply a modifier into the object's mesh geometry.",
    )
    async def blender_apply_modifier(object_name: str, modifier_name: str) -> Dict[str, Any]:
        """Apply a modifier to geometry."""
        return await client.execute(
            "modifier.apply",
            {"object_name": object_name, "modifier_name": modifier_name},
        )

    @server.tool(
        name="blender_remove_modifier",
        description="Remove a modifier from an object's stack.",
    )
    async def blender_remove_modifier(object_name: str, modifier_name: str) -> Dict[str, Any]:
        """Remove a modifier."""
        return await client.execute(
            "modifier.remove",
            {"object_name": object_name, "modifier_name": modifier_name},
        )
