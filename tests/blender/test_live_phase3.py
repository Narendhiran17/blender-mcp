"""Live Blender integration test for Phase 3: Mesh Modeling & Modifiers."""

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
async def test_live_blender_phase3_workflows():
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

        # 2. Create base primitive cube
        cube_name = "Phase3_Product_Mesh"
        created = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CUBE",
                "name": cube_name,
                "location": [0.0, 0.0, 0.0],
                "size": 2.0,
            },
        )
        assert created["name"] == cube_name

        # 3. Inspect mesh
        mesh_info = await client.execute("mesh.inspect", {"name": cube_name})
        assert mesh_info["vertex_count"] == 8
        assert mesh_info["polygon_count"] == 6
        assert mesh_info["is_watertight"] is True
        assert mesh_info["non_manifold_edges"] == 0

        # 4. Subdivide mesh
        sub_res = await client.execute(
            "mesh.subdivide",
            {"name": cube_name, "cuts": 1, "smoothness": 0.0},
        )
        assert sub_res["cuts_applied"] == 1
        assert sub_res["vertex_count"] > 8
        assert sub_res["polygon_count"] == 24

        # 5. Extrude mesh faces
        ext_res = await client.execute(
            "mesh.extrude",
            {"name": cube_name, "direction": [0.0, 0.0, 1.0], "distance": 1.5},
        )
        assert ext_res["extruded_faces_count"] > 0
        assert ext_res["vertex_count"] > sub_res["vertex_count"]

        # 6. Recalculate normals
        norm_res = await client.execute(
            "mesh.recalculate_normals",
            {"name": cube_name, "inside": False},
        )
        assert norm_res["faces_count"] > 0

        # 7. Shade smooth
        smooth_res = await client.execute(
            "mesh.shade_smooth",
            {"name": cube_name, "smooth": True},
        )
        assert smooth_res["smooth"] is True

        # 8. Bevel mesh edges
        bev_res = await client.execute(
            "mesh.bevel",
            {"name": cube_name, "offset": 0.05, "segments": 1, "affect": "EDGES"},
        )
        assert bev_res["offset"] == 0.05

        # 9. Validate mesh
        val_res = await client.execute("mesh.validate", {"name": cube_name})
        assert val_res["is_valid"] is True
        assert val_res["non_manifold_edges"] == 0
        assert val_res["loose_verts"] == 0

        # 10. Modifiers: Add SUBSURF and SOLIDIFY
        mod_sub = await client.execute(
            "modifier.add",
            {
                "object_name": cube_name,
                "modifier_type": "SUBSURF",
                "name": "SubdivisionMod",
                "properties": {"levels": 2, "render_levels": 3},
            },
        )
        assert mod_sub["modifier_name"] == "SubdivisionMod"

        mod_sol = await client.execute(
            "modifier.add",
            {
                "object_name": cube_name,
                "modifier_type": "SOLIDIFY",
                "name": "SolidifyMod",
                "properties": {"thickness": 0.15},
            },
        )
        assert mod_sol["modifier_name"] == "SolidifyMod"

        # 11. List modifiers
        mod_list = await client.execute("modifier.list", {"object_name": cube_name})
        mod_names = [m["name"] for m in mod_list["modifiers"]]
        assert "SubdivisionMod" in mod_names
        assert "SolidifyMod" in mod_names

        # 12. Configure modifier
        cfg_res = await client.execute(
            "modifier.configure",
            {
                "object_name": cube_name,
                "modifier_name": "SubdivisionMod",
                "properties": {"levels": 1},
            },
        )
        assert cfg_res["updated_properties"]["levels"] == 1

        # 13. Apply modifier
        apply_res = await client.execute(
            "modifier.apply",
            {"object_name": cube_name, "modifier_name": "SolidifyMod"},
        )
        assert apply_res["applied"] is True

        # 14. Remove modifier
        rem_res = await client.execute(
            "modifier.remove",
            {"object_name": cube_name, "modifier_name": "SubdivisionMod"},
        )
        assert rem_res["removed"] is True

        # Confirm modifiers stack is now empty
        final_mods = await client.execute("modifier.list", {"object_name": cube_name})
        assert final_mods["total"] == 0

    finally:
        try:
            await client.execute("system.shutdown")
            proc.wait(timeout=5.0)
        except Exception:
            proc.kill()
