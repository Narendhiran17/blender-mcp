"""Scene and collection tools for MCP Server."""

from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_scene_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register scene and collection tools with the MCP server."""

    @server.tool(
        name="blender_list_scenes",
        description="List all scenes in the current project with their render engines, active cameras, and object counts.",
    )
    async def blender_list_scenes() -> Dict[str, Any]:
        """List all scenes."""
        return await client.execute("scene.list")

    @server.tool(
        name="blender_inspect_scene",
        description="Inspect detailed configuration of a scene (resolution, FPS, active camera, render engine, units, collections).",
    )
    async def blender_inspect_scene(name: Optional[str] = None) -> Dict[str, Any]:
        """Inspect a specific scene or the active scene if name is omitted."""
        args = {}
        if name:
            args["name"] = name
        return await client.execute("scene.inspect", args)

    @server.tool(
        name="blender_create_scene",
        description="Create a new scene in the project (setup_mode can be 'NEW', 'LINK_COPY', or 'FULL_COPY').",
    )
    async def blender_create_scene(name: str = "New Scene", setup_mode: str = "NEW") -> Dict[str, Any]:
        """Create a new scene."""
        return await client.execute("scene.create", {"name": name, "setup_mode": setup_mode})

    @server.tool(
        name="blender_set_active_scene",
        description="Switch the active scene in Blender to the specified scene name.",
    )
    async def blender_set_active_scene(name: str) -> Dict[str, Any]:
        """Set the active scene."""
        return await client.execute("scene.set_active", {"name": name})

    @server.tool(
        name="blender_save_project",
        description="Save the Blender project (.blend). If never saved before, 'filepath' must be provided.",
    )
    async def blender_save_project(filepath: Optional[str] = None) -> Dict[str, Any]:
        """Save the project file."""
        args = {}
        if filepath:
            args["filepath"] = filepath
        return await client.execute("scene.save", args)

    @server.tool(
        name="blender_list_collections",
        description="List all collections in the active scene and their member objects.",
    )
    async def blender_list_collections() -> Dict[str, Any]:
        """List collections."""
        return await client.execute("collection.list")

    @server.tool(
        name="blender_create_collection",
        description="Create a new collection, optionally nested under a parent collection.",
    )
    async def blender_create_collection(
        name: str, parent_collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a collection."""
        args = {"name": name}
        if parent_collection:
            args["parent_collection"] = parent_collection
        return await client.execute("collection.create", args)

    @server.tool(
        name="blender_link_to_collection",
        description="Link an object into a collection, with option to unlink it from all other collections.",
    )
    async def blender_link_to_collection(
        object_name: str, collection_name: str, unlink_from_others: bool = False
    ) -> Dict[str, Any]:
        """Link an object to a collection."""
        return await client.execute(
            "collection.link_object",
            {
                "object_name": object_name,
                "collection_name": collection_name,
                "unlink_from_others": unlink_from_others,
            },
        )
