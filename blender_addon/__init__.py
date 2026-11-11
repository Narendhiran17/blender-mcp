"""Blender AI Control Add-on and Local Bridge Entry Point."""

bl_info = {
    "name": "Blender AI Control Bridge",
    "author": "Blender AI Control Team",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "System",
    "description": "MCP Bridge for AI control of Blender",
    "warning": "",
    "doc_url": "https://github.com/blender-ai-control/blender-ai-control-mcp",
    "category": "System",
}

import logging
import os

logger = logging.getLogger("blender_ai_control")


def register() -> None:
    """Register add-on, start dispatcher and localhost HTTP bridge."""
    from . import operations  # Ensures operations are registered
    from .bridge.auth import get_active_token, get_token_file_path
    from .bridge.dispatcher import start_dispatcher
    from .bridge.server import start_bridge

    # Read host and port from environment or defaults
    host = os.environ.get("BLENDER_BRIDGE_HOST", "127.0.0.1")
    port = int(os.environ.get("BLENDER_BRIDGE_PORT", "8765"))
    token = os.environ.get("BLENDER_BRIDGE_TOKEN")

    start_dispatcher()
    start_bridge(host=host, port=port, token=token)

    token_path = get_token_file_path()
    print("=" * 60)
    print(f" [Blender AI Control] Bridge active at http://{host}:{port}")
    print(f" [Blender AI Control] Token stored at: {token_path}")
    print("=" * 60)


def unregister() -> None:
    """Unregister add-on and cleanly stop dispatcher and bridge."""
    from .bridge.dispatcher import stop_dispatcher
    from .bridge.server import stop_bridge

    stop_bridge()
    stop_dispatcher()
    print("[Blender AI Control] Bridge stopped cleanly.")


if __name__ == "__main__":
    register()
