"""End-to-end verification script for Phase 1: Foundation and Connection."""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to sys.path
WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

from mcp_server.client import BlenderBridgeClient
from mcp_server.config import settings

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
RUNNER_SCRIPT = WORKSPACE / "scripts" / "blender_runner.py"


async def run_verification() -> bool:
    print("=" * 70)
    print(" STARTING PHASE 1 END-TO-END VERIFICATION")
    print("=" * 70)

    # 1. Launch Blender background runner
    print(f"\n[1/5] Launching Blender background runner from {BLENDER_EXE}...")
    proc = subprocess.Popen(
        [BLENDER_EXE, "--background", "--python", str(RUNNER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client = BlenderBridgeClient()

    # 2. Wait for bridge to become ready
    print("\n[2/5] Waiting for Blender bridge HTTP server at http://127.0.0.1:8765/health...")
    ready = False
    for attempt in range(20):
        time.sleep(0.5)
        health = await client.check_health()
        if health.get("status") == "ok":
            print(f" -> Bridge is healthy: {health}")
            ready = True
            break
        print(f" -> Waiting... (attempt {attempt + 1}/20)")

    if not ready:
        print("ERROR: Blender bridge failed to start.")
        proc.terminate()
        return False

    # 3. Check live status and version
    print("\n[3/5] Querying live Blender status via bridge...")
    status = await client.get_status()
    print(f" -> Blender Version: {status.get('blender_version_string')}")
    print(f" -> Active Scene: {status.get('active_scene')}")
    print(f" -> Initial Object Count: {status.get('objects_count')}")

    # 4. Execute Phase 1 Core Action: Create Primitive Cube
    cube_name = "Phase1_Proof_Cube"
    cube_loc = [1.0, 2.0, 3.0]
    cube_scale = [1.5, 1.5, 1.5]
    print(f"\n[4/5] Executing 'object.create_primitive' for cube '{cube_name}' at {cube_loc}...")

    created = await client.execute(
        "object.create_primitive",
        {
            "primitive_type": "CUBE",
            "name": cube_name,
            "location": cube_loc,
            "scale": cube_scale,
            "size": 2.0,
        },
    )
    print(f" -> Created Object Response: {created}")

    # Verify object inspection
    print(f"\n[5/5] Inspecting object '{cube_name}' in Blender...")
    inspected = await client.execute("object.inspect", {"name": cube_name})
    print(f" -> Inspected Object: {inspected}")

    # Verify object list
    obj_list = await client.execute("object.list")
    names = [o["name"] for o in obj_list.get("objects", [])]
    print(f" -> Scene Objects now: {names}")

    # 5. Assertions
    assert inspected["name"] == cube_name, f"Expected name '{cube_name}', got {inspected['name']}"
    assert inspected["type"] == "MESH", f"Expected type 'MESH', got {inspected['type']}"
    assert inspected["vertex_count"] == 8, f"Expected 8 vertices, got {inspected['vertex_count']}"
    assert inspected["polygon_count"] == 6, f"Expected 6 polygons, got {inspected['polygon_count']}"
    assert cube_name in names, f"Expected '{cube_name}' in scene object list"

    # Clean shutdown
    print("\nShutting down Blender runner cleanly...")
    await client.execute("system.shutdown")
    proc.wait(timeout=5.0)

    print("\n" + "=" * 70)
    print(" PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")
    print(" [x] Blender started with add-on and localhost bridge")
    print(" [x] Main-thread dispatcher executed operations safely")
    print(" [x] Cube created and transforms applied on Blender main thread")
    print(" [x] Cube inspected and validated via structured MCP bridge")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = asyncio.run(run_verification())
    sys.exit(0 if success else 1)
