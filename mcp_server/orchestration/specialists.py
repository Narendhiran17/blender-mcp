"""Specialist module definitions for AI Orchestration."""

from enum import Enum
from typing import Any, Dict, List, Optional
from mcp_server.client import BlenderBridgeClient
from .context import ValidationResult


class SpecialistType(str, Enum):
    SCENE = "SceneSpecialist"
    MODELING = "ModelingSpecialist"
    MATERIAL = "MaterialSpecialist"
    LIGHTING = "LightingSpecialist"
    ANIMATION = "AnimationSpecialist"
    SIMULATION = "SimulationSpecialist"
    RENDERING = "RenderSpecialist"
    QUALITY = "QualitySpecialist"


class QualitySpecialist:
    """Specialist responsible for deterministic validation and quality checks."""

    def __init__(self, client: BlenderBridgeClient):
        self.client = client

    async def validate_scene(self, required_objects: Optional[List[str]] = None) -> List[ValidationResult]:
        """Perform deterministic scene checks."""
        results = []

        # 1. System/Scene Health & Status
        status = await self.client.execute("system.status", {})
        results.append(
            ValidationResult(
                check_name="blender_bridge_status",
                passed=status.get("status") in ("ready", "running", "ok") or "objects_count" in status,
                details=status,
            )
        )

        # 2. Check required objects
        if required_objects:
            objs_data = await self.client.execute("object.list", {})
            existing_names = [o["name"] for o in objs_data.get("objects", [])]
            for req in required_objects:
                found = req in existing_names
                results.append(
                    ValidationResult(
                        check_name=f"object_exists_{req}",
                        passed=found,
                        details={"expected": req, "found": found},
                        remediation_hint=None if found else f"Create missing object '{req}' using ModelingSpecialist",
                    )
                )

        # 3. Environment check: Camera and Light presence
        env = await self.client.execute("environment.inspect", {})
        has_camera = env.get("active_camera") is not None
        has_light = env.get("light_count", 0) > 0 or len(env.get("lights", [])) > 0
        results.append(
            ValidationResult(
                check_name="active_camera_present",
                passed=has_camera,
                details={"active_camera": env.get("active_camera")},
                remediation_hint=None if has_camera else "Add an active camera using LightingSpecialist before rendering",
            )
        )
        results.append(
            ValidationResult(
                check_name="scene_lighting_present",
                passed=has_light,
                details={"light_count": env.get("light_count", 0)},
                remediation_hint=None if has_light else "Add a light or configure world illumination before rendering",
            )
        )

        # 4. Render configuration check
        rstat = await self.client.execute("render.status", {})
        valid_res = rstat.get("resolution_x", 0) > 0 and rstat.get("resolution_y", 0) > 0
        results.append(
            ValidationResult(
                check_name="render_resolution_valid",
                passed=valid_res,
                details=rstat,
            )
        )

        return results
