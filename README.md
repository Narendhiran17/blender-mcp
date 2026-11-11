# Blender AI Control MCP

> Structured, secure, local-first Model Context Protocol (MCP) server and Blender add-on for AI-driven 3D workflows.

[![Tests](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)]()
[![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)]()
[![MCP](https://img.shields.io/badge/MCP-2.0-purple.svg)]()

---

## Features (Phase 1 Ready)

* **MCP 2.0 Compliant:** Built on the official MCP Python SDK (`mcp`). Exposes tools, resources, and reusable workflow prompts over standard I/O (`stdio`).
* **Thread-Safe Blender Integration:** Bridge HTTP server safely receives requests on background threads and dispatches `bpy` calls on Blender's main thread via a persistent timer queue.
* **Localhost-Only Security:** Binds to `127.0.0.1` only with constant-time token validation.
* **No Arbitrary Code Execution:** Strictly typed, allowlisted domain operations.
* **Core Tools Included:**
  * `blender_health`: Check bridge health and connectivity.
  * `blender_status`: Inspect live Blender state, active scene, objects, and engine.
  * `blender_version`: Read Blender release and platform metadata.
  * `blender_create_primitive`: Create 3D primitives (Cube, Sphere, Cylinder, Plane, Cone, Torus) with location, rotation, scale, and size.
  * `blender_inspect_object`: Inspect vertex, polygon, and edge counts, dimensions, materials, and modifiers.
  * `blender_list_objects`: Retrieve inventory of objects in the active scene.

---

## Quick Start

### 1. Setup Environment
```powershell
# Create virtual environment and install dependencies
& "C:\Program Files\Python311\python.exe" -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install pytest pytest-asyncio ruff mypy
```

### 2. Install Blender Add-on
```powershell
.venv\Scripts\python.exe scripts\install_addon.py
```

### 3. Verify End-to-End
```powershell
.venv\Scripts\python.exe scripts\verify_phase1.py
```

### 4. Run Test Suite
```powershell
.venv\Scripts\pytest.exe -v
```

---

## MCP Client Configuration

To connect this server to any MCP client (such as Claude Desktop, Cursor, or Antigravity):

```json
{
  "mcpServers": {
    "blender": {
      "command": "c:\\Users\\naren\\OneDrive\\Desktop\\blender MCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "BLENDER_BRIDGE_HOST": "127.0.0.1",
        "BLENDER_BRIDGE_PORT": "8765"
      }
    }
  }
}
```

---

## Documentation

* [Windows Setup Guide](docs/setup-windows.md)
* [Bridge API Contract](docs/api-contract.md)
* [System Architecture & Threading](docs/architecture.md)
* [Project Specification & Roadmap](Blender_AI_Control_MCP_Project_Context.md)
