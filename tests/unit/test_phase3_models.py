"""Unit tests for Phase 3 Modeling data models."""

from shared.models import (
    AddModifierArgs,
    ApplyModifierArgs,
    BevelMeshArgs,
    ConfigureModifierArgs,
    ExtrudeMeshArgs,
    MergeMeshArgs,
    RecalculateNormalsArgs,
    ShadeSmoothArgs,
    SubdivideMeshArgs,
)


def test_mesh_modeling_args():
    sub = SubdivideMeshArgs(name="Cube", cuts=2, smoothness=0.5)
    assert sub.cuts == 2
    assert sub.smoothness == 0.5

    bev = BevelMeshArgs(name="Cube", offset=0.05, segments=3, affect="EDGES")
    assert bev.offset == 0.05
    assert bev.segments == 3
    assert bev.affect == "EDGES"

    ext = ExtrudeMeshArgs(name="Cube", direction=(0.0, 0.0, 1.0), distance=2.5)
    assert ext.distance == 2.5
    assert ext.direction == (0.0, 0.0, 1.0)

    merge = MergeMeshArgs(name="Cube", distance=0.001)
    assert merge.distance == 0.001

    norm = RecalculateNormalsArgs(name="Cube", inside=True)
    assert norm.inside is True

    smooth = ShadeSmoothArgs(name="Cube", smooth=True)
    assert smooth.smooth is True


def test_modifier_args():
    add_mod = AddModifierArgs(
        object_name="Cube",
        modifier_type="SUBSURF",
        name="Subdivision",
        properties={"levels": 2, "render_levels": 3},
    )
    assert add_mod.object_name == "Cube"
    assert add_mod.modifier_type == "SUBSURF"
    assert add_mod.properties["levels"] == 2

    cfg_mod = ConfigureModifierArgs(
        object_name="Cube",
        modifier_name="Subdivision",
        properties={"levels": 3},
    )
    assert cfg_mod.modifier_name == "Subdivision"
    assert cfg_mod.properties["levels"] == 3

    apply_mod = ApplyModifierArgs(object_name="Cube", modifier_name="Subdivision")
    assert apply_mod.modifier_name == "Subdivision"
