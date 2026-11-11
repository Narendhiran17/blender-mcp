"""Live Blender integration test for Phase 5: Geometry Nodes, Armatures, Rigging & Animation."""

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
async def test_live_blender_phase5_workflows():
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

        # 2. Armatures and Rigging Workflow
        arm_res = await client.execute(
            "armature.create",
            {
                "name": "Phase5_CharacterArmature",
                "location": [0.0, 0.0, 0.0],
                "initial_bone_name": "Root",
                "initial_bone_head": [0.0, 0.0, 0.0],
                "initial_bone_tail": [0.0, 0.0, 1.0],
            },
        )
        assert arm_res["name"] == "Phase5_CharacterArmature"
        assert arm_res["type"] == "ARMATURE"
        assert "Root" in arm_res["bones"]

        # Add Spine bone
        spine_res = await client.execute(
            "armature.add_bone",
            {
                "armature_name": "Phase5_CharacterArmature",
                "bone_name": "Spine",
                "head": [0.0, 0.0, 1.0],
                "tail": [0.0, 0.0, 2.0],
                "parent_bone": "Root",
                "use_connect": True,
            },
        )
        assert spine_res["bone_name"] == "Spine"
        assert spine_res["parent"] == "Root"

        # Add Hand bone
        hand_res = await client.execute(
            "armature.add_bone",
            {
                "armature_name": "Phase5_CharacterArmature",
                "bone_name": "Hand_R",
                "head": [0.0, 0.0, 1.8],
                "tail": [1.0, 0.0, 1.8],
                "parent_bone": "Spine",
                "use_connect": False,
            },
        )
        assert hand_res["bone_name"] == "Hand_R"

        # Inspect Armature
        inspect_arm = await client.execute(
            "armature.inspect",
            {"name": "Phase5_CharacterArmature"},
        )
        assert inspect_arm["bone_count"] == 3
        bone_names = [b["name"] for b in inspect_arm["bones"]]
        assert "Root" in bone_names
        assert "Spine" in bone_names
        assert "Hand_R" in bone_names

        # Create mesh object and parent to armature with auto weights
        mesh_res = await client.execute(
            "object.create_primitive",
            {
                "primitive_type": "CYLINDER",
                "name": "Phase5_CharacterMesh",
                "location": [0.0, 0.0, 1.0],
                "size": 1.0,
            },
        )
        assert mesh_res["name"] == "Phase5_CharacterMesh"

        parent_res = await client.execute(
            "rig.parent_mesh",
            {
                "mesh_object_name": "Phase5_CharacterMesh",
                "armature_object_name": "Phase5_CharacterArmature",
                "parent_type": "ARMATURE_AUTO",
            },
        )
        assert parent_res["parent"] == "Phase5_CharacterArmature"
        assert "Armature" in parent_res["modifiers"]

        # 3. Geometry Nodes Workflow
        # List groups initially
        groups_list = await client.execute("geometry_nodes.list_groups", {})
        assert "groups" in groups_list

        # Assign Geometry Nodes modifier and create group
        gn_assign = await client.execute(
            "geometry_nodes.assign_group",
            {
                "object_name": "Phase5_CharacterMesh",
                "modifier_name": "CharacterGeoNodes",
                "group_name": "ProceduralDetailGroup",
                "create_if_missing": True,
            },
        )
        assert gn_assign["modifier_name"] == "CharacterGeoNodes"
        assert gn_assign["group_name"] == "ProceduralDetailGroup"

        # Inspect Geometry Nodes
        gn_inspect = await client.execute(
            "geometry_nodes.inspect",
            {
                "object_name": "Phase5_CharacterMesh",
                "modifier_name": "CharacterGeoNodes",
            },
        )
        assert gn_inspect["group_name"] == "ProceduralDetailGroup"
        assert gn_inspect["input_count"] >= 1  # Standard Geometry socket

        # 4. Keyframe Animation and Timeline Workflow
        # Configure playback range
        playback_res = await client.execute(
            "animation.playback_range",
            {
                "frame_start": 1,
                "frame_end": 120,
                "frame_current": 1,
                "fps": 30,
            },
        )
        assert playback_res["frame_start"] == 1
        assert playback_res["frame_end"] == 120
        assert playback_res["fps"] == 30
        assert playback_res["total_frames"] == 120

        # Insert keyframe at frame 1 on armature
        kf1 = await client.execute(
            "animation.create_keyframe",
            {
                "object_name": "Phase5_CharacterArmature",
                "data_path": "location",
                "frame": 1.0,
                "value": [0.0, 0.0, 0.0],
            },
        )
        assert kf1["frame"] == 1.0

        # Insert keyframe at frame 60
        kf2 = await client.execute(
            "animation.create_keyframe",
            {
                "object_name": "Phase5_CharacterArmature",
                "data_path": "location",
                "frame": 60.0,
                "value": [0.0, 5.0, 0.0],
            },
        )
        assert kf2["frame"] == 60.0

        # Insert keyframe at frame 120
        kf3 = await client.execute(
            "animation.create_keyframe",
            {
                "object_name": "Phase5_CharacterArmature",
                "data_path": "location",
                "frame": 120.0,
                "value": [0.0, 0.0, 0.0],
            },
        )
        assert kf3["frame"] == 120.0

        # Inspect animation
        anim_inspect = await client.execute(
            "animation.inspect",
            {"object_name": "Phase5_CharacterArmature"},
        )
        assert anim_inspect["has_animation"] is True
        assert anim_inspect["fcurve_count"] == 3  # X, Y, Z
        assert anim_inspect["frame_range"] == [1.0, 120.0]

        # Configure animation interpolation to LINEAR
        conf_anim = await client.execute(
            "animation.configure",
            {
                "object_name": "Phase5_CharacterArmature",
                "data_path": "location",
                "interpolation": "LINEAR",
            },
        )
        assert conf_anim["modified_keyframes"] > 0
        assert conf_anim["interpolation"] == "LINEAR"

        # Verify keyframe interpolation in inspection
        anim_inspect_updated = await client.execute(
            "animation.inspect",
            {"object_name": "Phase5_CharacterArmature"},
        )
        for fc in anim_inspect_updated["fcurves"]:
            for kp in fc["keyframes"]:
                assert kp["interpolation"] == "LINEAR"

    finally:
        # Cleanup Blender process
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
