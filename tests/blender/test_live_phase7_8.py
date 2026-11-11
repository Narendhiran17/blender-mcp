"""Live Blender integration test for Phase 7 (Orchestration) and Phase 8 (Visual Intelligence)."""

import os
import subprocess
import time
from pathlib import Path
import pytest

from mcp_server.client import BlenderBridgeClient
from mcp_server.orchestration.orchestrator import MasterOrchestrator
from mcp_server.orchestration.planner import TaskPlanner
from mcp_server.visual.evaluator import VisualEvaluator

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
WORKSPACE = Path(__file__).resolve().parent.parent.parent
RUNNER_SCRIPT = WORKSPACE / "scripts" / "blender_runner.py"

blender_exists = Path(BLENDER_EXE).exists()


@pytest.mark.skipif(not blender_exists, reason="Blender executable not found")
@pytest.mark.asyncio
async def test_live_blender_phase7_8_orchestration_and_visual():
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

        # 2. Test TaskPlanner
        prompt = "Create a cosmetic bottle product presentation scene"
        context = TaskPlanner.plan_workflow(prompt)
        assert len(context.plan) >= 5
        assert len(context.acceptance_criteria) > 0

        # 3. Test MasterOrchestrator end-to-end execution
        orchestrator = MasterOrchestrator(client)
        exec_summary = await orchestrator.execute(context)

        # Assert plan completed
        assert exec_summary["summary"]["status"] in ("completed", "completed_with_warnings")
        assert exec_summary["completed_steps"] >= 5
        assert len(exec_summary["output_files"]) >= 1

        # Assert deterministic scene validations ran
        validations = exec_summary["validations"]
        assert len(validations) > 0
        checks = [v["check_name"] for v in validations]
        assert "blender_bridge_status" in checks
        assert "object_exists_Product_Model" in checks

        # 4. Test Visual Intelligence on rendered preview
        rendered_preview = exec_summary["output_files"][0]
        assert os.path.exists(rendered_preview)

        visual_result = VisualEvaluator.evaluate(
            rendered_preview,
            expected_min_width=100,
            expected_min_height=100,
        )
        assert visual_result["passes_quality_gate"] is True
        assert visual_result["metrics"]["format"] == "PNG"
        assert visual_result["metrics"]["width"] > 0
        assert visual_result["metrics"]["height"] > 0

        # Clean up output file
        if os.path.exists(rendered_preview):
            os.remove(rendered_preview)

    finally:
        # Cleanup Blender process
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
