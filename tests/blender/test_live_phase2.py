"""Live Blender integration test for Phase 2: Core Blender Controls."""

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
async def test_live_blender_phase2_workflows():
    fixtures_dir = WORKSPACE / "tests" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    temp_blend_file = fixtures_dir / "phase2_saved_project.blend"
    if temp_blend_file.exists():
        temp_blend_file.unlink()

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

        # 2. Scene listing and inspection
        scenes = await client.execute("scene.list")
        assert scenes["total"] >= 1
        assert scenes["active_scene"] == "Scene"

        scene_info = await client.execute("scene.inspect", {"name": "Scene"})
        assert scene_info["name"] == "Scene"
        assert "render_engine" in scene_info

        # 3. Create collection
        col_res = await client.execute("collection.create", {"name": "Props_Collection"})
        assert col_res["name"] == "Props_Collection"

        cols = await client.execute("collection.list")
        col_names = [c["name"] for c in cols["collections"]]
        assert "Props_Collection" in col_names

        # 4. Create object & link to collection
        created = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CUBE",
                "name": "Phase2_Parent",
                "location": [0.0, 0.0, 0.0],
                "size": 2.0,
            },
        )
        assert created["name"] == "Phase2_Parent"

        link_res = await client.execute(
            "collection.link_object",
            {
                "object_name": "Phase2_Parent",
                "collection_name": "Props_Collection",
                "unlink_from_others": False,
            },
        )
        assert "Props_Collection" in link_res["current_collections"]

        # 5. Transform object
        trans_res = await client.execute(
            "object.transform",
            {
                "name": "Phase2_Parent",
                "location": [2.0, 4.0, 1.0],
                "scale": [1.5, 1.5, 1.5],
            },
        )
        assert trans_res["location"] == [2.0, 4.0, 1.0]
        assert trans_res["scale"] == [1.5, 1.5, 1.5]

        # 6. Create child object and parent it
        child_created = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CYLINDER",
                "name": "Phase2_Child",
                "location": [2.0, 4.0, 3.0],
                "size": 1.0,
            },
        )
        assert child_created["name"] == "Phase2_Child"

        parent_res = await client.execute(
            "object.set_parent",
            {
                "child_name": "Phase2_Child",
                "parent_name": "Phase2_Parent",
                "keep_transform": True,
            },
        )
        assert parent_res["parent"] == "Phase2_Parent"

        # Inspect parent and child hierarchy
        parent_inspect = await client.execute("object.inspect", {"name": "Phase2_Parent"})
        assert "Phase2_Child" in parent_inspect["children"]

        child_inspect = await client.execute("object.inspect", {"name": "Phase2_Child"})
        assert child_inspect["parent"] == "Phase2_Parent"

        # 7. Duplicate object
        dup_res = await client.execute(
            "object.duplicate",
            {
                "name": "Phase2_Parent",
                "new_name": "Phase2_Duplicate",
                "offset": [10.0, 0.0, 0.0],
            },
        )
        assert dup_res["name"] == "Phase2_Duplicate"
        assert dup_res["location"][0] == 12.0  # 2.0 + 10.0

        # 8. Rename object
        rename_res = await client.execute(
            "object.rename",
            {
                "old_name": "Phase2_Duplicate",
                "new_name": "Phase2_Renamed",
            },
        )
        assert rename_res["new_name"] == "Phase2_Renamed"

        # 9. Set visibility
        vis_res = await client.execute(
            "object.set_visibility",
            {
                "name": "Phase2_Renamed",
                "hide_viewport": True,
                "hide_render": True,
            },
        )
        assert vis_res["visible_viewport"] is False
        assert vis_res["visible_render"] is False

        # 10. Select object
        sel_res = await client.execute(
            "object.select",
            {
                "name": "Phase2_Renamed",
                "select": True,
                "deselect_others": True,
                "set_active": True,
            },
        )
        assert sel_res["active_object"] == "Phase2_Renamed"
        assert sel_res["selected_objects"] == ["Phase2_Renamed"]

        # 11. Delete object
        del_res = await client.execute("object.delete", {"name": "Phase2_Renamed"})
        assert del_res["deleted"] is True

        obj_list = await client.execute("object.list")
        remaining_names = [o["name"] for o in obj_list["objects"]]
        assert "Phase2_Renamed" not in remaining_names

        # 12. Save project file
        save_res = await client.execute(
            "scene.save",
            {"filepath": str(temp_blend_file)},
        )
        assert save_res["is_saved"] is True
        assert temp_blend_file.exists()
        assert temp_blend_file.stat().st_size > 0

    finally:
        try:
            await client.execute("system.shutdown")
            proc.wait(timeout=5.0)
        except Exception:
            proc.kill()
        if temp_blend_file.exists():
            temp_blend_file.unlink()
