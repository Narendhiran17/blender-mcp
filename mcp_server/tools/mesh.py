"""Mesh modeling tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_mesh_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register mesh editing and validation tools with the MCP server."""

    @server.tool(
        name="blender_inspect_mesh",
        description="Inspect mesh topology: vertex/edge/face counts, non-manifold geometry, loose components, watertightness, and UV layers.",
    )
    async def blender_inspect_mesh(name: str) -> Dict[str, Any]:
        """Inspect detailed mesh topology and geometry."""
        return await client.execute("mesh.inspect", {"name": name})

    @server.tool(
        name="blender_subdivide_mesh",
        description="Subdivide mesh faces and edges by a specified number of cuts and smoothness.",
    )
    async def blender_subdivide_mesh(
        name: str,
        cuts: int = 1,
        smoothness: float = 0.0,
    ) -> Dict[str, Any]:
        """Subdivide a mesh."""
        return await client.execute("mesh.subdivide", {"name": name, "cuts": cuts, "smoothness": smoothness})

    @server.tool(
        name="blender_bevel_mesh",
        description="Bevel edges or vertices of a mesh object with offset and segment count.",
    )
    async def blender_bevel_mesh(
        name: str,
        offset: float = 0.1,
        segments: int = 1,
        affect: str = "EDGES",
    ) -> Dict[str, Any]:
        """Bevel mesh geometry."""
        return await client.execute(
            "mesh.bevel",
            {"name": name, "offset": offset, "segments": segments, "affect": affect},
        )

    @server.tool(
        name="blender_extrude_mesh",
        description="Extrude faces of a mesh along a direction vector by a given distance.",
    )
    async def blender_extrude_mesh(
        name: str,
        direction: List[float] = [0.0, 0.0, 1.0],
        distance: float = 1.0,
        face_indices: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Extrude mesh faces."""
        args: Dict[str, Any] = {"name": name, "direction": direction, "distance": distance}
        if face_indices is not None:
            args["face_indices"] = face_indices
        return await client.execute("mesh.extrude", args)

    @server.tool(
        name="blender_merge_vertices",
        description="Merge vertices by distance threshold (remove duplicate/close vertices).",
    )
    async def blender_merge_vertices(name: str, distance: float = 0.0001) -> Dict[str, Any]:
        """Merge close or duplicate vertices."""
        return await client.execute("mesh.merge", {"name": name, "distance": distance})

    @server.tool(
        name="blender_recalculate_normals",
        description="Recalculate mesh face normals consistently outward or inward.",
    )
    async def blender_recalculate_normals(name: str, inside: bool = False) -> Dict[str, Any]:
        """Recalculate normals."""
        return await client.execute("mesh.recalculate_normals", {"name": name, "inside": inside})

    @server.tool(
        name="blender_shade_smooth",
        description="Set smooth shading (True) or flat faceted shading (False) on mesh polygons.",
    )
    async def blender_shade_smooth(name: str, smooth: bool = True) -> Dict[str, Any]:
        """Set smooth or flat polygon shading."""
        return await client.execute("mesh.shade_smooth", {"name": name, "smooth": smooth})

    @server.tool(
        name="blender_validate_mesh",
        description="Validate mesh integrity: checks for non-manifold edges/vertices, loose elements, zero-area faces, and watertightness.",
    )
    async def blender_validate_mesh(name: str) -> Dict[str, Any]:
        """Validate mesh for 3D printing and export readiness."""
        return await client.execute("mesh.validate", {"name": name})
