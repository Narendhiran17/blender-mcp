# System Architecture

## Overview

Blender AI Control MCP provides a secure, structured interface between Model Context Protocol (MCP) clients and Blender 3D.

```text
[ MCP Host / Client ] (Cursor, Claude Desktop, Antigravity)
          │
          │ stdio (MCP Protocol 2.0)
          ▼
[ Python MCP Server ] (mcp_server package)
  - Tool Registry: blender_health, blender_status, blender_create_primitive, blender_inspect_object, blender_list_objects
  - Resource Registry: blender://system/info, blender://scene/active, blender://scene/objects
  - Prompts: inspect_and_report_scene, create_cube_test
  - Pydantic validation & schemas
          │
          │ Authenticated HTTP (127.0.0.1:8765)
          ▼
[ Local Blender Bridge ] (blender_addon.bridge)
  - HTTP Server running on daemon background thread
  - Token-based constant-time authentication
  - Thread-safe RequestQueue
          │
          │ Queue pop on Blender Timer Tick
          ▼
[ Blender Add-on Runtime & Dispatcher ] (blender_addon.bridge.dispatcher)
  - Registered via bpy.app.timers.register(process_queue)
  - Executes exclusively on Blender's Main Thread
  - Dispatches to registered operations
          │
          │ bpy / bmesh / mathutils
          ▼
[ Blender Engine ]
```

---

## Critical Threading Design

1. **Blender Main Thread Safety:**
   Blender’s Python API (`bpy`) is strictly single-threaded and unsafe to call from background threads.
2. **HTTP Background Processing:**
   The bridge HTTP server accepts incoming connections on a background daemon thread. It parses the envelope, authenticates the token, and enqueues a `QueuedRequest`.
3. **Timer Dispatcher Execution:**
   `bpy.app.timers.register(process_queue, persistent=True)` checks the queue every 20ms on Blender's main thread. It resolves handlers, runs the operation using `bpy`, sets the result, and signals the completion event.
4. **Synchronous Wait & Response:**
   The HTTP handler thread waits on the request's `completion_event` with a timeout, then formats and sends the JSON `ResponseEnvelope`.
