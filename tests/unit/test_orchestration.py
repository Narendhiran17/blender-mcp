"""Unit tests for AI Orchestration components."""

import pytest
from mcp_server.orchestration.context import TaskContext
from mcp_server.orchestration.planner import TaskPlanner
from mcp_server.orchestration.specialists import SpecialistType


def test_task_context_lifecycle():
    ctx = TaskContext(user_request="Create a chair")
    assert ctx.status == "planning"
    assert len(ctx.plan) == 0

    s1 = ctx.add_step(
        specialist=SpecialistType.MODELING.value,
        operation="object.create_primitive",
        description="Create seat",
        arguments={"primitive_type": "CUBE", "name": "Seat"},
    )
    assert len(ctx.plan) == 1
    assert len(ctx.get_pending_steps()) == 1

    ctx.mark_step_completed(s1.step_id, {"name": "Seat"})
    assert len(ctx.get_pending_steps()) == 0
    assert len(ctx.completed_steps) == 1

    summary = ctx.to_summary()
    assert summary["total_steps"] == 1
    assert summary["completed_steps"] == 1


def test_planner_product_workflow():
    ctx = TaskPlanner.plan_workflow("Create a cosmetic bottle product presentation scene")
    assert len(ctx.plan) >= 5
    assert len(ctx.acceptance_criteria) > 0

    operations = [s.operation for s in ctx.plan]
    assert "object.create_primitive" in operations
    assert "modifier.add" in operations
    assert "material.create" in operations
    assert "light.create" in operations
    assert "camera.create" in operations
    assert "render.preview" in operations


def test_planner_rigging_workflow():
    ctx = TaskPlanner.plan_workflow("Rig and animate a character")
    assert len(ctx.plan) >= 3
    operations = [s.operation for s in ctx.plan]
    assert "animation.playback_range" in operations
    assert "armature.create" in operations
    assert "armature.add_bone" in operations
