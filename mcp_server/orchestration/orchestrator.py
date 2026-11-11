"""Master Blender Orchestrator coordinating specialists and plan execution."""

import logging
from typing import Any, Dict, Optional
from mcp_server.client import BlenderBridgeClient, default_client
from .context import TaskContext
from .specialists import QualitySpecialist

logger = logging.getLogger("blender_ai_control.orchestrator")


class MasterOrchestrator:
    """Master orchestrator executing multi-step plans with deterministic validation."""

    def __init__(self, client: Optional[BlenderBridgeClient] = None):
        self.client = client or default_client
        self.quality = QualitySpecialist(self.client)
        self.active_contexts: Dict[str, TaskContext] = {}

    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """Execute all steps in a TaskContext with validation."""
        self.active_contexts[context.task_id] = context
        context.status = "executing"

        # 1. Execute plan steps sequentially
        for step in context.get_pending_steps():
            logger.info("Executing step [%s] %s (%s)...", step.step_id, step.description, step.operation)
            step.status = "in_progress"

            try:
                result = await self.client.execute(step.operation, step.arguments)
                context.mark_step_completed(step.step_id, result)

                # Track generated output files (e.g. renders)
                if "filepath" in result and result.get("status") == "success":
                    context.output_files.append(result["filepath"])

                # Track created objects
                if "name" in result and step.operation.startswith("object.create"):
                    context.known_objects.append(result["name"])

            except Exception as e:
                logger.error("Step [%s] failed: %s", step.step_id, str(e))
                context.mark_step_failed(step.step_id, str(e))
                context.status = "failed"
                break

        # 2. Run deterministic quality checks if plan completed
        if context.status != "failed":
            context.status = "validating"
            try:
                val_results = await self.quality.validate_scene(required_objects=context.known_objects)
                context.validations.extend(val_results)
                all_passed = all(v.passed for v in val_results)
                context.status = "completed" if all_passed else "completed_with_warnings"
            except Exception as e:
                logger.warning("Quality validation error: %s", str(e))
                context.errors.append(f"Validation failed: {str(e)}")
                context.status = "completed_with_warnings"

        return {
            "summary": context.to_summary(),
            "validations": [v.model_dump() for v in context.validations],
            "completed_steps": len(context.completed_steps),
            "output_files": context.output_files,
        }
