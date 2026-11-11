"""Live Blender integration test for Phase 4: Materials, Textures, UVs, Lighting, & Cameras."""

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
async def test_live_blender_phase4_workflows():
    # Launch background Blender runner
    proc = subprocess.Popen(
        [BLENDER_EXE, "--background", "--python", str(RUNNER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client = BlenderBridgeClient()

    try:
        # 1. Wait for bridge
        ready = False
        for _ in range(20):
            time.sleep(0.5)
            h = await client.check_health()
            if h.get("status") == "ok":
                ready = True
                break
        assert ready, "Bridge failed to become healthy"

        # 2. Create product model primitive
        prod_name = "Phase4_Product_Bottle"
        created = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CYLINDER",
                "name": prod_name,
                "location": [0.0, 0.0, 1.0],
                "size": 2.0,
            },
        )
        assert created["name"] == prod_name

        # 3. Smart UV unwrap
        unwrap_res = await client.execute(
            "uv.unwrap",
            {"name": prod_name, "method": "SMART", "island_margin": 0.02},
        )
        assert unwrap_res["active_uv_layer"] is not None

        # 4. List and inspect UVs
        uv_list = await client.execute("uv.list", {"name": prod_name})
        assert uv_list["total"] >= 1

        uv_inspect = await client.execute("uv.inspect", {"name": prod_name})
        assert uv_inspect["has_uvs"] is True

        # 5. Create Material
        mat_name = "Mat_GoldPresentation"
        mat_res = await client.execute(
            "material.create",
            {
                "name": mat_name,
                "base_color": [1.0, 0.76, 0.33],
                "roughness": 0.2,
                "metallic": 0.9,
            },
        )
        assert mat_res["name"] == mat_name

        # 6. Assign material to product
        assign_res = await client.execute(
            "material.assign",
            {"object_name": prod_name, "material_name": mat_name},
        )
        assert assign_res["material_name"] == mat_name

        # 7. Inspect material
        mat_inspect = await client.execute("material.inspect", {"name": mat_name})
        assert pytest.approx(mat_inspect["metallic"], 0.01) == 0.9
        assert pytest.approx(mat_inspect["roughness"], 0.01) == 0.2

        # 8. Configure material
        cfg_mat = await client.execute(
            "material.configure",
            {"name": mat_name, "roughness": 0.15, "emission_strength": 1.5},
        )
        assert pytest.approx(cfg_mat["updated"]["roughness"], 0.01) == 0.15

        # 9. Create Lights (Key Spot and Fill Area)
        key_light = await client.execute(
            "light.create",
            {
                "light_type": "SPOT",
                "name": "Phase4_KeySpot",
                "location": [3.0, -3.0, 4.0],
                "energy": 1200.0,
                "color": [1.0, 0.95, 0.9],
            },
        )
        assert key_light["name"] == "Phase4_KeySpot"
        assert key_light["light_type"] == "SPOT"

        fill_light = await client.execute(
            "light.create",
            {
                "light_type": "AREA",
                "name": "Phase4_FillArea",
                "location": [-3.0, -2.0, 3.0],
                "energy": 600.0,
                "color": [0.8, 0.9, 1.0],
            },
        )
        assert fill_light["name"] == "Phase4_FillArea"

        # 10. Configure Light
        cfg_light = await client.execute(
            "light.configure",
            {"name": "Phase4_KeySpot", "energy": 1500.0},
        )
        assert cfg_light["updated"]["energy"] == 1500.0

        # 11. Create Camera
        cam_res = await client.execute(
            "camera.create",
            {
                "name": "Phase4_ProductCam",
                "location": [0.0, -4.5, 2.0],
                "focal_length": 85.0,
                "set_active": True,
            },
        )
        assert cam_res["name"] == "Phase4_ProductCam"
        assert cam_res["is_active_camera"] is True

        # 12. Configure Camera
        cfg_cam = await client.execute(
            "camera.configure",
            {"name": "Phase4_ProductCam", "focal_length": 75.0},
        )
        assert cfg_cam["updated"]["focal_length"] == 75.0

        # 13. Configure World
        world_res = await client.execute(
            "world.configure",
            {"color": [0.05, 0.05, 0.08], "strength": 0.8},
        )
        assert pytest.approx(world_res["strength"], 0.01) == 0.8

        # 14. Inspect Environment
        env_res = await client.execute("environment.inspect")
        assert env_res["active_camera"] == "Phase4_ProductCam"
        assert env_res["lights_count"] >= 2

    finally:
        try:
            await client.execute("system.shutdown")
            proc.wait(timeout=5.0)
        except Exception:
            proc.kill()
