"""Live Blender integration test executing real operations in Blender."""

import os
import subprocess
import time
from pathlib import Path
import pytest

from mcp_server.client import BlenderBridgeClient

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
RUNNER_SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "blender_runner.py"

blender_exists = Path(BLENDER_EXE).exists()


@pytest.mark.skipif(not blender_exists, reason="Blender executable not found at specified path")
@pytest.mark.asyncio
async def test_live_blender_cube_creation():
    # 1. Launch Blender background runner
    proc = subprocess.Popen(
        [BLENDER_EXE, "--background", "--python", str(RUNNER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client = BlenderBridgeClient()

    try:
        # 2. Wait for health check
        healthy = False
        for _ in range(20):
            time.sleep(0.5)
            health = await client.check_health()
            if health.get("status") == "ok":
                healthy = True
                break
        assert healthy, "Blender bridge failed to become healthy within timeout"

        # 3. Create a cube
        cube_name = "PytestLiveCube"
        created = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CUBE",
                "name": cube_name,
                "location": [0.0, 0.0, 1.0],
                "scale": [1.0, 1.0, 1.0],
                "size": 2.0,
            },
        )
        assert created["name"] == cube_name
        assert created["type"] == "MESH"

        # 4. Inspect object
        inspected = await client.execute("object.inspect", {"name": cube_name})
        assert inspected["name"] == cube_name
        assert inspected["vertex_count"] == 8
        assert inspected["polygon_count"] == 6

        # 5. List objects
        obj_list = await client.execute("object.list")
        names = [o["name"] for o in obj_list.get("objects", [])]
        assert cube_name in names

    finally:
        # Clean shutdown
        try:
            await client.execute("system.shutdown")
            proc.wait(timeout=5.0)
        except Exception:
            proc.kill()
