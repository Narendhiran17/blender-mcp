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
        description="Inspect an object in Blender to inspect its transforms, dimensions, hierarchy (parent/children), collections, vertex counts, materials, and modifiers.",
    )
    async def blender_inspect_object(name: str) -> Dict[str, Any]:
        """Inspect detailed properties of an object in Blender."""
        return await client.execute("object.inspect", {"name": name})

    @server.tool(
        name="blender_list_objects",
        description="List objects in the active scene, optionally filtered by type (e.g. 'MESH', 'CAMERA', 'LIGHT') or collection name.",
    )
    async def blender_list_objects(
        object_type: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List objects in the active scene."""
        args = {}
        if object_type:
            args["type"] = object_type
        if collection:
            args["collection"] = collection
        return await client.execute("object.list", args)

    @server.tool(
        name="blender_rename_object",
        description="Rename an existing object in Blender.",
    )
    async def blender_rename_object(old_name: str, new_name: str) -> Dict[str, Any]:
        """Rename an object."""
        return await client.execute("object.rename", {"old_name": old_name, "new_name": new_name})

    @server.tool(
        name="blender_transform_object",
        description="Set or adjust location, rotation (Euler radians), or scale of an object. If relative=True, adds to current transforms.",
    )
    async def blender_transform_object(
        name: str,
        location: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        relative: bool = False,
    ) -> Dict[str, Any]:
        """Transform an object."""
        args: Dict[str, Any] = {"name": name, "relative": relative}
        if location is not None:
            args["location"] = location
        if rotation is not None:
            args["rotation"] = rotation
        if scale is not None:
            args["scale"] = scale
        return await client.execute("object.transform", args)

    @server.tool(
        name="blender_duplicate_object",
        description="Duplicate an object (deep copy or linked) with optional offset and new name.",
    )
    async def blender_duplicate_object(
        name: str,
        new_name: Optional[str] = None,
        linked: bool = False,
        offset: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Duplicate an object."""
        args: Dict[str, Any] = {"name": name, "linked": linked}
        if new_name:
            args["new_name"] = new_name
        if offset is not None:
            args["offset"] = offset
        return await client.execute("object.duplicate", args)

    @server.tool(
        name="blender_delete_object",
        description="Delete an object from Blender and optionally delete unreferenced mesh data.",
    )
    async def blender_delete_object(name: str, delete_data: bool = True) -> Dict[str, Any]:
        """Delete an object."""
        return await client.execute("object.delete", {"name": name, "delete_data": delete_data})

    @server.tool(
        name="blender_set_parent",
        description="Parent a child object to a parent object, or unparent if parent_name is empty/omitted. Preserves world transforms by default.",
    )
    async def blender_set_parent(
        child_name: str,
        parent_name: Optional[str] = None,
        keep_transform: bool = True,
    ) -> Dict[str, Any]:
        """Set or clear object parenting."""
        return await client.execute(
            "object.set_parent",
            {
                "child_name": child_name,
                "parent_name": parent_name,
                "keep_transform": keep_transform,
            },
        )

    @server.tool(
        name="blender_set_visibility",
        description="Set object visibility in 3D viewport and/or final render.",
    )
    async def blender_set_visibility(
        name: str,
        hide_viewport: Optional[bool] = None,
        hide_render: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Set object visibility."""
        args: Dict[str, Any] = {"name": name}
        if hide_viewport is not None:
            args["hide_viewport"] = hide_viewport
        if hide_render is not None:
            args["hide_render"] = hide_render
        return await client.execute("object.set_visibility", args)

    @server.tool(
        name="blender_select_object",
        description="Select or deselect an object, optionally deselect other objects, and set as active object.",
    )
    async def blender_select_object(
        name: Optional[str] = None,
        select: bool = True,
        deselect_others: bool = False,
        set_active: bool = True,
    ) -> Dict[str, Any]:
        """Select or deselect an object."""
        return await client.execute(
            "object.select",
            {
                "name": name,
                "select": select,
                "deselect_others": deselect_others,
                "set_active": set_active,
            },
        )
