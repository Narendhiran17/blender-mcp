# Blender AI Control MCP

> Structured, secure, local-first Model Context Protocol (MCP) server and Blender add-on for AI-driven 3D workflows.

[![Tests](https://img.shields.io/badge/tests-42%20passed-brightgreen.svg)]()
[![Tools](https://img.shields.io/badge/MCP%20tools-74%20registered-blue.svg)]()
[![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)]()
[![MCP](https://img.shields.io/badge/MCP-2.0-purple.svg)]()
[![License](https://img.shields.io/badge/License-GPL--3.0%20%7C%20MIT-blue.svg)](LICENSE)

---

## Overview

**Blender AI Control MCP** provides complete, thread-safe, allowlisted AI control over Blender 3D without direct code execution (`eval`/`exec`). It implements 74 structured MCP tools across 13 functional domains, connecting AI assistants (Antigravity, Claude Desktop, Cursor, etc.) directly to a live Blender session.

### Complete 13 Functional Domains (74 Tools):
1. **System & Connection (3 tools):** Health check, real-time Blender project status, build version.
2. **Scene & Collections (8 tools):** Scene list, inspect, create, switch active, save `.blend`, collections hierarchy and object linking.
3. **Object Transforms & Hierarchy (7 tools):** Primitives (Cube, Sphere, Cylinder, Plane, Cone, Torus), rename, transform, duplicate, delete, parenting with inverse matrix preservation, visibility and selection.
4. **Mesh Modeling & Editing (8 tools):** Headless `bmesh` inspection, subdivide, bevel, extrude, merge, recalculate normals, shade smooth, geometric validation.
5. **Modifiers (6 tools):** List modifiers, add, configure, apply, remove, reorder stack.
6. **Materials, Textures & UVs (9 tools):** Principled BSDF creation & configuration, slot assignment, inspection, image texture linking, UV unwrapping (Smart, Cube, Sphere, Cylinder).
7. **Lighting, Cameras & Environment (7 tools):** Point/Sun/Spot/Area lights, cameras with focal length/clipping, active camera switching, world background illumination & HDRIs, environment inspection.
8. **Geometry Nodes (4 tools):** Node group listing, inspect sockets & overrides, assign modifier & create procedural passthrough groups, configure input parameters.
9. **Armatures & Rigging (4 tools):** Armature creation, bone hierarchy inspection, bone editing in edit mode, auto-weight mesh skinning.
10. **Animation & Timeline (4 tools):** Frame keyframing on location/rotation/scale, action & F-curve inspection, interpolation setting (Bezier, Linear, Constant), scene playback range & framerate.
11. **Physics & Simulation (4 tools):** Rigid body active/passive configuration, cloth simulation modifier, physics inspection, point cache baking.
12. **Rendering & Compositing (5 tools):** Cycles/Eevee engine configuration, fast preview still renders to disk, render status, compositor node tree inspection & node insertion (e.g. Denoise).
13. **AI Orchestration & Visual Intelligence (5 tools):** Multi-step task planner, master orchestrator execution loop, deterministic quality validation, and visual exposure/defect evaluation of preview renders.

---

## Architecture & Security

```text
MCP Client (Antigravity / Claude / Cursor)
      │
      ▼ (stdio)
Python MCP Server (74 tools, Pydantic schemas, Planner, Visual Evaluator)
      │
      ▼ (Localhost HTTP 127.0.0.1:8765, Bearer Token Auth)
Blender Add-on Bridge (Request Queue, Path Policy Sandbox)
      │
      ▼ (bpy.app.timers - Blender Main Thread)
Blender Engine (bpy, bmesh, mathutils, Cycles/Eevee)
```

* **Thread-Safety:** `bpy` API is strictly executed on Blender's main thread via persistent timer queues.
* **Security:** Localhost binding only (`127.0.0.1`), constant-time token validation (`hmac.compare_digest`), path traversal sandbox restricting file I/O to approved workspaces.
* **No `eval`/`exec`:** Every single capability is an allowlisted domain operation with strict schema validation.

---

## Quick Start

### 1. Setup Environment
```powershell
& "C:\Program Files\Python311\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install pytest pytest-asyncio ruff mypy
```

### 2. Install Add-on into Blender
```powershell
.\.venv\Scripts\python.exe scripts\install_addon.py
```
*Or install the zip package in Blender (`Edit > Preferences > Add-ons > Install from Disk`):*
`dist/blender_ai_control_addon-v1.0.0.zip`

### 3. Run Automated Tests
```powershell
.\.venv\Scripts\pytest.exe -v
```

---

## MCP Client Configuration

Add this server to your client configuration (e.g. Claude Desktop `claude_desktop_config.json`, Cursor, or Antigravity):

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:\\Users\\naren\\OneDrive\\Desktop\\blender MCP\\.venv\\Scripts\\python.exe",
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

* [Tool Catalogue (All 74 Tools)](docs/tool-catalogue.md)
* [Windows Setup Guide](docs/setup-windows.md)
* [Bridge API Contract](docs/api-contract.md)
* [System Architecture & Threading](docs/architecture.md)
* [Project Specification & Roadmap](Blender_AI_Control_MCP_Project_Context.md)

---

## License

This project is licensed under a dual-licensing model to ensure full compliance with the Blender Foundation's licensing policies while maximizing flexibility for external MCP AI clients:

* **Blender Add-on (`blender_addon/`):** Licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)** as required by Blender Python (`bpy`) integration.
* **MCP Server & Client Components (`mcp_server/`, `shared/`):** Dual-licensed under the **MIT License** (via Section 7 permission exception in [`LICENSE`](LICENSE)), allowing AI developer toolchains and MCP clients (Claude, Cursor, Antigravity) to integrate without copyleft constraints.

See [`LICENSE`](LICENSE) for the full text.
