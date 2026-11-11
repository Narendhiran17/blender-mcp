"""Armature and rigging tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_rigging_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register armature and rigging tools with the MCP server."""

    @server.tool(
        name="blender_create_armature",
        description="Create an Armature object in Blender, optionally with an initial root bone.",
    )
    async def blender_create_armature(
        name: str = "Armature",
        location: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        initial_bone_name: Optional[str] = "Root",
        initial_bone_head: Optional[List[float]] = None,
        initial_bone_tail: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Create a new armature object."""
        args: Dict[str, Any] = {"name": name}
        if location is not None:
            args["location"] = location
        if rotation is not None:
            args["rotation"] = rotation
        if scale is not None:
            args["scale"] = scale
        if initial_bone_name is not None:
            args["initial_bone_name"] = initial_bone_name
        if initial_bone_head is not None:
            args["initial_bone_head"] = initial_bone_head
        if initial_bone_tail is not None:
            args["initial_bone_tail"] = initial_bone_tail
        return await client.execute("armature.create", args)

    @server.tool(
        name="blender_inspect_armature",
        description="Inspect bone hierarchy, coordinates, lengths, and parents of an Armature.",
    )
    async def blender_inspect_armature(name: str) -> Dict[str, Any]:
        """Inspect an armature object."""
        return await client.execute("armature.inspect", {"name": name})

    @server.tool(
        name="blender_add_bone",
        description="Add a new bone to an armature with head/tail positions, roll, and optional parenting.",
    )
    async def blender_add_bone(
        armature_name: str,
        bone_name: str,
        head: Optional[List[float]] = None,
        tail: Optional[List[float]] = None,
        parent_bone: Optional[str] = None,
        use_connect: bool = False,
        roll: float = 0.0,
    ) -> Dict[str, Any]:
        """Add a bone to an existing armature."""
        args: Dict[str, Any] = {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "head": head if head is not None else [0.0, 0.0, 0.0],
            "tail": tail if tail is not None else [0.0, 0.0, 1.0],
            "use_connect": use_connect,
            "roll": roll,
        }
        if parent_bone is not None:
            args["parent_bone"] = parent_bone
        return await client.execute("armature.add_bone", args)

    @server.tool(
        name="blender_parent_mesh_to_armature",
        description="Parent a mesh to an armature (e.g. 'ARMATURE_AUTO' for automatic weights, 'ARMATURE_ENVELOPE', 'ARMATURE').",
    )
    async def blender_parent_mesh_to_armature(
        mesh_object_name: str,
        armature_object_name: str,
        parent_type: str = "ARMATURE_AUTO",
    ) -> Dict[str, Any]:
        """Parent mesh to armature with skinning."""
        return await client.execute(
            "rig.parent_mesh",
            {
                "mesh_object_name": mesh_object_name,
                "armature_object_name": armature_object_name,
                "parent_type": parent_type,
            },
        )
