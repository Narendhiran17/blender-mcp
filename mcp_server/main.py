"""Main entry point for Blender AI Control MCP Server."""

import logging
import sys
from mcp.server.mcpserver import MCPServer
from mcp_server.config import settings
from mcp_server.prompts import register_prompts
from mcp_server.resources import register_resources
from mcp_server.tools.objects import register_object_tools
from mcp_server.tools.system import register_system_tools

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("blender_ai_control.mcp_server")


def create_server() -> MCPServer:
    """Create and configure the MCP server instance."""
    server = MCPServer(
        name="blender-ai-control",
        instructions="MCP server providing structured tools to inspect and control Blender 3D locally.",
    )

    register_system_tools(server)
    register_object_tools(server)
    register_resources(server)
    register_prompts(server)

    return server


def main() -> None:
    """Run MCP server over stdio."""
    server = create_server()
    logger.info("Starting Blender AI Control MCP Server on stdio...")
    server.run("stdio")


if __name__ == "__main__":
    main()
