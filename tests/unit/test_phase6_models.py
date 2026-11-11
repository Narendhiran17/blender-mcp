"""Unit tests for Phase 6 Pydantic argument models."""

import pytest
from pydantic import ValidationError

from shared.models import (
    BakeSimulationArgs,
    ConfigureClothArgs,
    ConfigureCompositorArgs,
    ConfigureRenderArgs,
    ConfigureRigidbodyArgs,
    InspectPhysicsArgs,
    RenderPreviewArgs,
)


def test_physics_models():
    # Rigidbody
    rb = ConfigureRigidbodyArgs(name="Sphere", type="ACTIVE", mass=2.5, friction=0.7)
    assert rb.name == "Sphere"
    assert rb.type == "ACTIVE"
    assert rb.mass == 2.5
    assert rb.friction == 0.7

    # Cloth
    cloth = ConfigureClothArgs(name="Flag", mass=0.2, tension_stiffness=25.0)
    assert cloth.name == "Flag"
    assert cloth.mass == 0.2
    assert cloth.tension_stiffness == 25.0

    # Physics inspect
    pi = InspectPhysicsArgs(name="Sphere")
    assert pi.name == "Sphere"

    # Bake
    bake = BakeSimulationArgs(simulation_type="RIGIDBODY", frame_start=1, frame_end=100)
    assert bake.simulation_type == "RIGIDBODY"
    assert bake.frame_start == 1
    assert bake.frame_end == 100


def test_rendering_and_compositor_models():
    # Render config
    rc = ConfigureRenderArgs(
        engine="CYCLES",
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=100,
        samples=128,
        file_format="PNG",
    )
    assert rc.engine == "CYCLES"
    assert rc.resolution_x == 1920
    assert rc.samples == 128

    # Render preview
    rp = RenderPreviewArgs(resolution_percentage=25, samples=8)
    assert rp.resolution_percentage == 25
    assert rp.samples == 8
    assert rp.write_image is True

    # Compositor config
    cc = ConfigureCompositorArgs(use_nodes=True, add_node_type="CompositorNodeDenoise")
    assert cc.use_nodes is True
    assert cc.add_node_type == "CompositorNodeDenoise"
