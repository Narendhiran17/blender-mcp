"""Entry script to run the Blender AI Control MCP Server."""

import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

from mcp_server.main import main

if __name__ == "__main__":
    main()
