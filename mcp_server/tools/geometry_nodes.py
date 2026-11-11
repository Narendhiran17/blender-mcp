"""Geometry Nodes tools for MCP Server."""

from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_geometry_nodes_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register Geometry Nodes tools with the MCP server."""

    @server.tool(
        name="blender_list_geometry_node_groups",
        description="List all Geometry Node groups in the active Blender project with socket counts.",
    )
    async def blender_list_geometry_node_groups() -> Dict[str, Any]:
        """List all geometry node groups."""
        return await client.execute("geometry_nodes.list_groups", {})

    @server.tool(
        name="blender_inspect_geometry_nodes",
        description="Inspect a Geometry Nodes modifier on an object or a node group directly (sockets, values, node types).",
    )
    async def blender_inspect_geometry_nodes(
        object_name: Optional[str] = None,
        modifier_name: str = "GeometryNodes",
        group_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Inspect Geometry Nodes modifier or node group."""
        args: Dict[str, Any] = {"modifier_name": modifier_name}
        if object_name:
            args["object_name"] = object_name
        if group_name:
            args["group_name"] = group_name
        return await client.execute("geometry_nodes.inspect", args)

    @server.tool(
        name="blender_assign_geometry_nodes",
        description="Assign a Geometry Nodes modifier to an object, optionally linking an existing or new node group.",
    )
    async def blender_assign_geometry_nodes(
        object_name: str,
        group_name: Optional[str] = None,
        modifier_name: str = "GeometryNodes",
        create_if_missing: bool = True,
    ) -> Dict[str, Any]:
        """Assign Geometry Nodes modifier to object."""
        args: Dict[str, Any] = {
            "object_name": object_name,
            "modifier_name": modifier_name,
            "create_if_missing": create_if_missing,
        }
        if group_name:
            args["group_name"] = group_name
        return await client.execute("geometry_nodes.assign_group", args)

    @server.tool(
        name="blender_configure_geometry_nodes",
        description="Configure input socket parameters of a Geometry Nodes modifier on an object.",
    )
    async def blender_configure_geometry_nodes(
        object_name: str,
        inputs: Dict[str, Any],
        modifier_name: str = "GeometryNodes",
    ) -> Dict[str, Any]:
        """Configure input sockets of a Geometry Nodes modifier."""
        return await client.execute(
            "geometry_nodes.configure",
            {
                "object_name": object_name,
                "modifier_name": modifier_name,
                "inputs": inputs,
            },
        )
