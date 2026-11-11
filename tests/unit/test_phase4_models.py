"""Unit tests for Phase 4 Materials, Textures, Lighting & Camera models."""

from shared.models import (
    AssignImageTextureArgs,
    AssignMaterialArgs,
    ConfigureCameraArgs,
    ConfigureLightArgs,
    ConfigureMaterialArgs,
    ConfigureWorldArgs,
    CreateCameraArgs,
    CreateLightArgs,
    CreateMaterialArgs,
    UnwrapUVArgs,
)


def test_material_args():
    mat_args = CreateMaterialArgs(
        name="Chrome",
        base_color=(0.8, 0.8, 0.8),
        roughness=0.1,
        metallic=0.9,
    )
    assert mat_args.name == "Chrome"
    assert mat_args.metallic == 0.9

    cfg_mat = ConfigureMaterialArgs(
        name="Chrome",
        roughness=0.05,
        emission_strength=2.0,
    )
    assert cfg_mat.roughness == 0.05
    assert cfg_mat.emission_strength == 2.0

    assign_mat = AssignMaterialArgs(object_name="Cube", material_name="Chrome", slot_index=0)
    assert assign_mat.slot_index == 0

    assign_tex = AssignImageTextureArgs(
        material_name="Chrome",
        image_path="C:/textures/albedo.png",
        target_socket="Base Color",
    )
    assert assign_tex.target_socket == "Base Color"


def test_uv_args():
    uv_args = UnwrapUVArgs(name="Cube", method="SMART", island_margin=0.02, angle_limit=60.0)
    assert uv_args.method == "SMART"
    assert uv_args.island_margin == 0.02


def test_lighting_camera_world_args():
    light = CreateLightArgs(
        light_type="SPOT",
        name="KeyLight",
        location=(3.0, -3.0, 5.0),
        energy=1500.0,
    )
    assert light.light_type == "SPOT"
    assert light.energy == 1500.0

    cfg_light = ConfigureLightArgs(name="KeyLight", spot_size=45.0)
    assert cfg_light.spot_size == 45.0

    cam = CreateCameraArgs(name="MainCam", focal_length=85.0, set_active=True)
    assert cam.focal_length == 85.0
    assert cam.set_active is True

    cfg_cam = ConfigureCameraArgs(name="MainCam", focal_length=50.0)
    assert cfg_cam.focal_length == 50.0

    world = ConfigureWorldArgs(color=[0.1, 0.1, 0.15], strength=0.8)
    assert world.color == [0.1, 0.1, 0.15]
    assert world.strength == 0.8
