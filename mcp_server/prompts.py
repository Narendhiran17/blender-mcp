"""Reusable MCP prompts for Blender workflows."""

from mcp.server.mcpserver import MCPServer


def register_prompts(server: MCPServer) -> None:
    """Register prompt templates with MCP server."""

    @server.prompt("inspect_and_report_scene")
    def inspect_and_report_scene() -> str:
        """Prompt to inspect the current Blender scene and report its structure."""
        return (
            "1. Call `blender_status` to understand current Blender state.\n"
            "2. Call `blender_list_objects` to get an inventory of objects in the scene.\n"
            "3. For key objects, call `blender_inspect_object` to check their dimensions and transforms.\n"
            "4. Provide a structured summary of the scene to the user."
        )

    @server.prompt("create_cube_test")
    def create_cube_test() -> str:
        """Prompt to test creating and inspecting a cube primitive."""
        return (
            "1. Verify connection using `blender_health`.\n"
            "2. Create a test cube using `blender_create_primitive(primitive_type='CUBE', name='TestCube')`.\n"
            "3. Inspect the created object using `blender_inspect_object(name='TestCube')`.\n"
            "4. Report the resulting dimensions and location."
        )
