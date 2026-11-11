"""Material, texture, and UV tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_material_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register material, texture, and UV tools with the MCP server."""

    @server.tool(
        name="blender_list_materials",
        description="List all materials in the project, or list materials assigned to a specific object.",
    )
    async def blender_list_materials(object_name: Optional[str] = None) -> Dict[str, Any]:
        """List materials."""
        args = {}
        if object_name:
            args["object_name"] = object_name
        return await client.execute("material.list", args)

    @server.tool(
        name="blender_create_material",
        description="Create a new Principled BSDF material with optional base color, roughness, and metallic properties.",
    )
    async def blender_create_material(
        name: str = "NewMaterial",
        base_color: Optional[List[float]] = None,
        roughness: Optional[float] = None,
        metallic: Optional[float] = None,
        specular: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a new material."""
        args: Dict[str, Any] = {"name": name}
        if base_color is not None:
            args["base_color"] = base_color
        if roughness is not None:
            args["roughness"] = roughness
        if metallic is not None:
            args["metallic"] = metallic
        if specular is not None:
            args["specular"] = specular
        return await client.execute("material.create", args)

    @server.tool(
        name="blender_configure_material",
        description="Configure Principled BSDF shader properties (base_color, roughness, metallic, transmission, emission, alpha, ior).",
    )
    async def blender_configure_material(
        name: str,
        base_color: Optional[List[float]] = None,
        roughness: Optional[float] = None,
        metallic: Optional[float] = None,
        specular: Optional[float] = None,
        transmission: Optional[float] = None,
        emission_color: Optional[List[float]] = None,
        emission_strength: Optional[float] = None,
        alpha: Optional[float] = None,
        ior: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Configure material properties."""
        args: Dict[str, Any] = {"name": name}
        if base_color is not None:
            args["base_color"] = base_color
        if roughness is not None:
            args["roughness"] = roughness
        if metallic is not None:
            args["metallic"] = metallic
        if specular is not None:
            args["specular"] = specular
        if transmission is not None:
            args["transmission"] = transmission
        if emission_color is not None:
            args["emission_color"] = emission_color
        if emission_strength is not None:
            args["emission_strength"] = emission_strength
        if alpha is not None:
            args["alpha"] = alpha
        if ior is not None:
            args["ior"] = ior
        return await client.execute("material.configure", args)

    @server.tool(
        name="blender_assign_material",
        description="Assign a material to an object, optionally specifying the material slot index.",
    )
    async def blender_assign_material(
        object_name: str,
        material_name: str,
        slot_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Assign material to an object."""
        args: Dict[str, Any] = {
            "object_name": object_name,
            "material_name": material_name,
        }
        if slot_index is not None:
            args["slot_index"] = slot_index
        return await client.execute("material.assign", args)

    @server.tool(
        name="blender_inspect_material",
        description="Inspect material settings and current values of its Principled BSDF shader inputs.",
    )
    async def blender_inspect_material(name: str) -> Dict[str, Any]:
        """Inspect detailed material shader inputs."""
        return await client.execute("material.inspect", {"name": name})

    @server.tool(
        name="blender_assign_image_texture",
        description="Load an image texture and connect it to a material shader socket (e.g. 'Base Color', 'Roughness').",
    )
    async def blender_assign_image_texture(
        material_name: str,
        image_path: str,
        target_socket: str = "Base Color",
    ) -> Dict[str, Any]:
        """Assign image texture to material."""
        return await client.execute(
            "texture.assign_image",
            {
                "material_name": material_name,
                "image_path": image_path,
                "target_socket": target_socket,
            },
        )

    @server.tool(
        name="blender_list_uv_layers",
        description="List UV layers on a mesh object and identify the active layer.",
    )
    async def blender_list_uv_layers(name: str) -> Dict[str, Any]:
        """List UV layers."""
        return await client.execute("uv.list", {"name": name})

    @server.tool(
        name="blender_unwrap_uv",
        description="Unwrap mesh UVs using Smart UV Project, Cube, Sphere, or Cylinder projection.",
    )
    async def blender_unwrap_uv(
        name: str,
        method: str = "SMART",
        island_margin: float = 0.01,
        angle_limit: float = 66.0,
    ) -> Dict[str, Any]:
        """Unwrap mesh UVs."""
        return await client.execute(
            "uv.unwrap",
            {
                "name": name,
                "method": method,
                "island_margin": island_margin,
                "angle_limit": angle_limit,
            },
        )

    @server.tool(
        name="blender_inspect_uv",
        description="Inspect UV layer coverage and stats for a mesh object.",
    )
    async def blender_inspect_uv(name: str) -> Dict[str, Any]:
        """Inspect UV details."""
        return await client.execute("uv.inspect", {"name": name})
