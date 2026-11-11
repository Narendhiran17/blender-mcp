"""Task Planner decomposing requests into structured execution steps."""

import re
from typing import Any, Dict, List
from .context import TaskContext, TaskStep
from .specialists import SpecialistType


class TaskPlanner:
    """Plans multi-step execution graphs for 3D workflows."""

    @staticmethod
    def plan_workflow(user_request: str) -> TaskContext:
        """Decompose a high-level request into explicit tool execution steps."""
        ctx = TaskContext(user_request=user_request)
        req_lower = user_request.lower()

        # Workflow: Product Scene / Model Presentation
        if any(w in req_lower for w in ("product", "bottle", "can", "presentation", "showcase", "table")):
            ctx.acceptance_criteria = [
                "Product mesh geometry exists and is smoothed/beveled",
                "BSDF material is configured and assigned",
                "Camera and studio lighting are properly configured",
                "Validation checks pass",
                "Preview image is rendered and verified",
            ]

            # Step 1: Model
            ctx.add_step(
                specialist=SpecialistType.MODELING.value,
                operation="object.create_primitive",
                description="Create primary product model primitive",
                arguments={"primitive_type": "CYLINDER", "name": "Product_Model", "location": [0.0, 0.0, 1.0], "size": 2.0},
            )
            # Step 2: Bevel
            ctx.add_step(
                specialist=SpecialistType.MODELING.value,
                operation="modifier.add",
                description="Add bevel modifier for realistic edges",
                arguments={"object_name": "Product_Model", "modifier_type": "BEVEL", "name": "Bevel", "properties": {"width": 0.05, "segments": 3}},
            )
            # Step 3: Material
            ctx.add_step(
                specialist=SpecialistType.MATERIAL.value,
                operation="material.create",
                description="Create glossy product material",
                arguments={"name": "Product_Material", "base_color": [0.1, 0.5, 0.8, 1.0], "roughness": 0.2, "metallic": 0.3},
            )
            ctx.add_step(
                specialist=SpecialistType.MATERIAL.value,
                operation="material.assign",
                description="Assign material to product model",
                arguments={"object_name": "Product_Model", "material_name": "Product_Material"},
            )
            # Step 4: Lighting & Camera
            ctx.add_step(
                specialist=SpecialistType.LIGHTING.value,
                operation="light.create",
                description="Create key light",
                arguments={"light_type": "AREA", "name": "KeyLight", "location": [3.0, -3.0, 4.0], "energy": 500.0},
            )
            ctx.add_step(
                specialist=SpecialistType.LIGHTING.value,
                operation="camera.create",
                description="Create presentation camera",
                arguments={"name": "StudioCamera", "location": [0.0, -5.0, 2.0], "rotation": [1.3, 0.0, 0.0], "set_active": True},
            )
            # Step 5: Render Setup
            ctx.add_step(
                specialist=SpecialistType.RENDERING.value,
                operation="render.configure",
                description="Configure render engine and resolution",
                arguments={"engine": "BLENDER_EEVEE_NEXT", "resolution_x": 640, "resolution_y": 480, "resolution_percentage": 100},
            )
            # Step 6: Render Preview
            ctx.add_step(
                specialist=SpecialistType.RENDERING.value,
                operation="render.preview",
                description="Render final preview image",
                arguments={"resolution_percentage": 50, "write_image": True},
            )

        # Workflow: Character / Rigging / Animation
        elif any(w in req_lower for w in ("character", "rig", "armature", "bone", "animate", "animation")):
            ctx.acceptance_criteria = [
                "Armature hierarchy created with root and spine",
                "Mesh parented with auto weighting",
                "Keyframes inserted across timeline",
            ]
            ctx.add_step(
                specialist=SpecialistType.ANIMATION.value,
                operation="animation.playback_range",
                description="Setup playback frame range",
                arguments={"frame_start": 1, "frame_end": 60, "fps": 30},
            )
            ctx.add_step(
                specialist=SpecialistType.ANIMATION.value,
                operation="armature.create",
                description="Create base armature with root bone",
                arguments={"name": "Hero_Armature", "initial_bone_name": "Root"},
            )
            ctx.add_step(
                specialist=SpecialistType.ANIMATION.value,
                operation="armature.add_bone",
                description="Add spine bone",
                arguments={"armature_name": "Hero_Armature", "bone_name": "Spine", "head": [0.0, 0.0, 1.0], "tail": [0.0, 0.0, 2.0], "parent_bone": "Root", "use_connect": True},
            )

        # Default Generic Plan: Inspect and Report
        else:
            ctx.acceptance_criteria = ["Scene status inspected"]
            ctx.add_step(
                specialist=SpecialistType.SCENE.value,
                operation="system.status",
                description="Inspect real-time Blender state",
                arguments={},
            )
            ctx.add_step(
                specialist=SpecialistType.SCENE.value,
                operation="scene.inspect",
                description="Inspect active scene settings",
                arguments={},
            )

        return ctx
