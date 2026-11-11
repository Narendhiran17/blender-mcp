"""Visual intelligence tools for MCP Server."""

from typing import Any, Dict
from mcp.server.mcpserver import MCPServer
from mcp_server.visual.evaluator import VisualEvaluator


def register_visual_tools(server: MCPServer) -> None:
    """Register visual intelligence tools with the MCP server."""

    @server.tool(
        name="blender_evaluate_visual_preview",
        description="Inspect and evaluate a rendered preview image file for dimensions, aspect ratio, exposure/luminance, and quality defects.",
    )
    async def blender_evaluate_visual_preview(
        filepath: str,
        expected_min_width: int = 100,
        expected_min_height: int = 100,
        min_luminance: float = 0.04,
        max_luminance: float = 0.96,
    ) -> Dict[str, Any]:
        """Evaluate a rendered preview image."""
        return VisualEvaluator.evaluate(
            filepath=filepath,
            expected_min_width=expected_min_width,
            expected_min_height=expected_min_height,
            min_luminance=min_luminance,
            max_luminance=max_luminance,
        )
