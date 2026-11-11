"""Rendering and compositing tools for MCP Server."""

from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_rendering_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register rendering and compositing tools with the MCP server."""

    @server.tool(
        name="blender_configure_render",
        description="Configure render engine (CYCLES, EEVEE, WORKBENCH), resolution, samples, output format, and paths.",
    )
    async def blender_configure_render(
        engine: Optional[str] = None,
        resolution_x: Optional[int] = None,
        resolution_y: Optional[int] = None,
        resolution_percentage: Optional[int] = None,
        samples: Optional[int] = None,
        file_format: Optional[str] = None,
        color_mode: Optional[str] = None,
        filepath: Optional[str] = None,
        transparent_background: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Configure render engine and parameters."""
        args: Dict[str, Any] = {}
        if engine is not None:
            args["engine"] = engine
        if resolution_x is not None:
            args["resolution_x"] = resolution_x
        if resolution_y is not None:
            args["resolution_y"] = resolution_y
        if resolution_percentage is not None:
            args["resolution_percentage"] = resolution_percentage
        if samples is not None:
            args["samples"] = samples
        if file_format is not None:
            args["file_format"] = file_format
        if color_mode is not None:
            args["color_mode"] = color_mode
        if filepath is not None:
            args["filepath"] = filepath
        if transparent_background is not None:
            args["transparent_background"] = transparent_background
        return await client.execute("render.configure", args)

    @server.tool(
        name="blender_render_preview",
        description="Render a quick still image preview of the current frame and return output filepath and metadata.",
    )
    async def blender_render_preview(
        output_path: Optional[str] = None,
        resolution_percentage: int = 50,
        samples: Optional[int] = 16,
        write_image: bool = True,
    ) -> Dict[str, Any]:
        """Render a preview image."""
        args: Dict[str, Any] = {
            "resolution_percentage": resolution_percentage,
            "write_image": write_image,
        }
        if output_path is not None:
            args["output_path"] = output_path
        if samples is not None:
            args["samples"] = samples
        return await client.execute("render.preview", args)

    @server.tool(
        name="blender_render_status",
        description="Retrieve current render configuration, active camera, resolution, and timeline settings.",
    )
    async def blender_render_status() -> Dict[str, Any]:
        """Query render settings and status."""
        return await client.execute("render.status", {})

    @server.tool(
        name="blender_inspect_compositor",
        description="Inspect the scene compositor node tree, active nodes, inputs, outputs, and links.",
    )
    async def blender_inspect_compositor() -> Dict[str, Any]:
        """Inspect compositor nodes and links."""
        return await client.execute("compositor.inspect", {})

    @server.tool(
        name="blender_configure_compositor",
        description="Enable/disable scene compositing nodes and add nodes (e.g. 'CompositorNodeDenoise', 'CompositorNodeGlare').",
    )
    async def blender_configure_compositor(
        use_nodes: bool = True,
        add_node_type: Optional[str] = None,
        node_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure compositor nodes."""
        args: Dict[str, Any] = {"use_nodes": use_nodes}
        if add_node_type is not None:
            args["add_node_type"] = add_node_type
        if node_name is not None:
            args["node_name"] = node_name
        return await client.execute("compositor.configure", args)
