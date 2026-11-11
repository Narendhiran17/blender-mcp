"""Shared Task Context for AI Orchestration."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    specialist: str
    operation: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ValidationResult(BaseModel):
    check_name: str
    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)
    remediation_hint: Optional[str] = None


class TaskContext(BaseModel):
    """Structured context tracking an orchestration session."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_request: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "planning"  # planning, executing, validating, completed, failed
    plan: List[TaskStep] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    active_scene_name: Optional[str] = None
    known_objects: List[str] = Field(default_factory=list)
    validations: List[ValidationResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    output_files: List[str] = Field(default_factory=list)

    def add_step(self, specialist: str, operation: str, description: str, arguments: Dict[str, Any]) -> TaskStep:
        step = TaskStep(
            specialist=specialist,
            operation=operation,
            description=description,
            arguments=arguments,
        )
        self.plan.append(step)
        return step

    def get_pending_steps(self) -> List[TaskStep]:
        return [s for s in self.plan if s.status == "pending"]

    def mark_step_completed(self, step_id: str, result: Dict[str, Any]) -> None:
        for s in self.plan:
            if s.step_id == step_id:
                s.status = "completed"
                s.result = result
                self.completed_steps.append(step_id)
                break

    def mark_step_failed(self, step_id: str, error_msg: str) -> None:
        for s in self.plan:
            if s.step_id == step_id:
                s.status = "failed"
                s.error = error_msg
                self.errors.append(f"Step {step_id} failed: {error_msg}")
                break

    def to_summary(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "user_request": self.user_request,
            "status": self.status,
            "total_steps": len(self.plan),
            "completed_steps": len(self.completed_steps),
            "errors_count": len(self.errors),
            "validations_passed": all(v.passed for v in self.validations) if self.validations else None,
            "output_files": self.output_files,
        }
