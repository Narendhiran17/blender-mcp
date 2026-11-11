"""Unit tests for Phase 5 Pydantic argument models."""

import pytest
from pydantic import ValidationError

from shared.models import (
    AddBoneArgs,
    AssignGeometryNodesArgs,
    ConfigureAnimationArgs,
    ConfigureGeometryNodesArgs,
    CreateArmatureArgs,
    CreateKeyframeArgs,
    InspectAnimationArgs,
    InspectArmatureArgs,
    InspectGeometryNodesArgs,
    ParentMeshToArmatureArgs,
    PlaybackRangeArgs,
)


def test_geometry_nodes_args():
    # Inspect
    inspect_args = InspectGeometryNodesArgs(object_name="Cube", modifier_name="GeometryNodes")
    assert inspect_args.object_name == "Cube"
    assert inspect_args.modifier_name == "GeometryNodes"
    assert inspect_args.group_name is None

    # Assign
    assign_args = AssignGeometryNodesArgs(object_name="Cube", group_name="TreeGen")
    assert assign_args.object_name == "Cube"
    assert assign_args.group_name == "TreeGen"
    assert assign_args.create_if_missing is True

    # Configure
    conf_args = ConfigureGeometryNodesArgs(
        object_name="Cube",
        inputs={"Count": 10, "Distance": 2.5},
    )
    assert conf_args.object_name == "Cube"
    assert conf_args.inputs["Count"] == 10
    assert conf_args.inputs["Distance"] == 2.5


def test_armature_and_rigging_args():
    # Create Armature
    create_args = CreateArmatureArgs(name="CharacterRig", location=(0.0, 0.0, 0.0))
    assert create_args.name == "CharacterRig"
    assert create_args.initial_bone_name == "Root"
    assert create_args.initial_bone_tail == (0.0, 0.0, 1.0)

    # Inspect Armature
    inspect_args = InspectArmatureArgs(name="CharacterRig")
    assert inspect_args.name == "CharacterRig"

    # Add Bone
    bone_args = AddBoneArgs(
        armature_name="CharacterRig",
        bone_name="Spine",
        head=(0.0, 0.0, 1.0),
        tail=(0.0, 0.0, 2.0),
        parent_bone="Root",
        use_connect=True,
    )
    assert bone_args.bone_name == "Spine"
    assert bone_args.parent_bone == "Root"
    assert bone_args.use_connect is True

    # Parent Mesh
    parent_args = ParentMeshToArmatureArgs(
        mesh_object_name="Body",
        armature_object_name="CharacterRig",
        parent_type="ARMATURE_AUTO",
    )
    assert parent_args.mesh_object_name == "Body"
    assert parent_args.parent_type == "ARMATURE_AUTO"


def test_animation_args():
    # Create Keyframe
    kf_args = CreateKeyframeArgs(
        object_name="Cube",
        data_path="location",
        frame=1.0,
        value=[0.0, 0.0, 5.0],
    )
    assert kf_args.object_name == "Cube"
    assert kf_args.frame == 1.0
    assert kf_args.index == -1

    # Inspect Animation
    inspect_anim = InspectAnimationArgs(object_name="Cube")
    assert inspect_anim.object_name == "Cube"

    # Configure Animation
    conf_anim = ConfigureAnimationArgs(
        object_name="Cube",
        data_path="location",
        interpolation="LINEAR",
    )
    assert conf_anim.interpolation == "LINEAR"
    assert conf_anim.clear_all is False

    # Playback Range
    range_args = PlaybackRangeArgs(frame_start=1, frame_end=250, fps=60)
    assert range_args.frame_start == 1
    assert range_args.frame_end == 250
    assert range_args.fps == 60
