"""Live Blender integration test for Phase 6: Simulation, Physics, Rendering & Compositing."""

import os
import subprocess
import time
from pathlib import Path
import pytest

from mcp_server.client import BlenderBridgeClient

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
WORKSPACE = Path(__file__).resolve().parent.parent.parent
RUNNER_SCRIPT = WORKSPACE / "scripts" / "blender_runner.py"

blender_exists = Path(BLENDER_EXE).exists()


@pytest.mark.skipif(not blender_exists, reason="Blender executable not found")
@pytest.mark.asyncio
async def test_live_blender_phase6_workflows():
    # Launch background Blender runner
    proc = subprocess.Popen(
        [BLENDER_EXE, "--background", "--python", str(RUNNER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client = BlenderBridgeClient()

    try:
        # 1. Wait for bridge to become healthy
        ready = False
        for _ in range(20):
            time.sleep(0.5)
            h = await client.check_health()
            if h.get("status") == "ok":
                ready = True
                break
        assert ready, "Bridge failed to become healthy"

        # 2. Physics: Rigid Body and Cloth
        # Ground plane
        await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "PLANE",
                "name": "Phase6_Ground",
                "location": [0.0, 0.0, 0.0],
                "size": 10.0,
            },
        )
        ground_rb = await client.execute(
            "physics.configure_rigidbody",
            {
                "name": "Phase6_Ground",
                "type": "PASSIVE",
                "friction": 0.8,
            },
        )
        assert ground_rb["type"] == "PASSIVE"
        assert ground_rb["friction"] == 0.8

        # Falling sphere
        await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "UV_SPHERE",
                "name": "Phase6_FallingSphere",
                "location": [0.0, 0.0, 5.0],
                "size": 1.0,
            },
        )
        sphere_rb = await client.execute(
            "physics.configure_rigidbody",
            {
                "name": "Phase6_FallingSphere",
                "type": "ACTIVE",
                "mass": 2.5,
                "friction": 0.4,
                "restitution": 0.6,
                "collision_shape": "SPHERE",
            },
        )
        assert sphere_rb["type"] == "ACTIVE"
        assert sphere_rb["mass"] == 2.5
        assert sphere_rb["restitution"] == 0.6

        # Cloth flag
        await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "PLANE",
                "name": "Phase6_ClothFlag",
                "location": [3.0, 0.0, 3.0],
                "size": 2.0,
            },
        )
        cloth_res = await client.execute(
            "physics.configure_cloth",
            {
                "name": "Phase6_ClothFlag",
                "mass": 0.15,
                "tension_stiffness": 20.0,
                "compression_stiffness": 20.0,
            },
        )
        assert cloth_res["mass"] == 0.15
        assert cloth_res["tension_stiffness"] == 20.0

        # Inspect physics
        inspect_sphere = await client.execute("physics.inspect", {"name": "Phase6_FallingSphere"})
        assert inspect_sphere["has_physics"] is True
        assert inspect_sphere["rigid_body"]["type"] == "ACTIVE"

        inspect_cloth = await client.execute("physics.inspect", {"name": "Phase6_ClothFlag"})
        assert inspect_cloth["has_physics"] is True
        assert inspect_cloth["cloth"]["modifier_name"] == "Cloth"

        # Bake simulation range
        bake_res = await client.execute(
            "simulation.bake",
            {"simulation_type": "RIGIDBODY", "frame_start": 1, "frame_end": 50},
        )
        assert bake_res["simulation_type"] == "RIGIDBODY"
        assert bake_res["frame_start"] == 1
        assert bake_res["frame_end"] == 50

        # 3. Compositing
        comp_before = await client.execute("compositor.inspect", {})
        assert "use_nodes" in comp_before

        comp_conf = await client.execute(
            "compositor.configure",
            {"use_nodes": True, "add_node_type": "CompositorNodeDenoise", "node_name": "TestDenoise"},
        )
        assert comp_conf["use_nodes"] is True
        assert comp_conf["added_node"] is not None

        comp_after = await client.execute("compositor.inspect", {})
        node_names = [n["name"] for n in comp_after["nodes"]]
        assert any("Denoise" in n for n in node_names)

        # 4. Rendering & Preview
        # Create light and camera
        await client.execute(
            "light.create",
            {
                "light_type": "SUN",
                "name": "Phase6_Sun",
                "location": [0.0, 0.0, 10.0],
                "energy": 5.0,
            },
        )
        await client.execute(
            "camera.create",
            {
                "name": "Phase6_RenderCamera",
                "location": [0.0, -8.0, 3.0],
                "rotation": [1.2, 0.0, 0.0],
                "set_active": True,
            },
        )

        render_conf = await client.execute(
            "render.configure",
            {
                "engine": "BLENDER_EEVEE_NEXT",
                "resolution_x": 320,
                "resolution_y": 240,
                "resolution_percentage": 100,
                "file_format": "PNG",
                "transparent_background": True,
            },
        )
        assert render_conf["resolution_x"] == 320
        assert render_conf["resolution_y"] == 240
        assert render_conf["transparent_background"] is True

        render_stat = await client.execute("render.status", {})
        assert render_stat["resolution_x"] == 320
        assert render_stat["active_camera"] == "Phase6_RenderCamera"

        # Execute render preview
        preview_res = await client.execute(
            "render.preview",
            {"resolution_percentage": 50, "write_image": True},
        )
        assert preview_res["status"] == "success"
        preview_path = preview_res["filepath"]
        assert os.path.exists(preview_path)
        assert preview_res["file_size_bytes"] > 0
        assert preview_res["width"] == 160
        assert preview_res["height"] == 120

        # Clean up preview file
        if os.path.exists(preview_path):
            os.remove(preview_path)

    finally:
        # Cleanup Blender process
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
