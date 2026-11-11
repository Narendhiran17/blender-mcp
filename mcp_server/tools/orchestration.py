"""AI Orchestration tools for MCP Server."""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client
from mcp_server.orchestration.context import TaskContext
from mcp_server.orchestration.orchestrator import MasterOrchestrator
from mcp_server.orchestration.planner import TaskPlanner

_orchestrator: Optional[MasterOrchestrator] = None


def get_orchestrator(client: BlenderBridgeClient) -> MasterOrchestrator:
    global _orchestrator
    if _orchestrator is None or _orchestrator.client != client:
        _orchestrator = MasterOrchestrator(client)
    return _orchestrator


def register_orchestration_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register AI Orchestration tools with the MCP server."""

    @server.tool(
        name="blender_plan_task",
        description="Decompose a natural language Blender request into a structured multi-step execution plan across specialists.",
    )
    async def blender_plan_task(user_request: str) -> Dict[str, Any]:
        """Generate a structured execution plan for a request."""
        ctx = TaskPlanner.plan_workflow(user_request)
        return {
            "task_id": ctx.task_id,
            "user_request": ctx.user_request,
            "acceptance_criteria": ctx.acceptance_criteria,
            "steps": [s.model_dump() for s in ctx.plan],
            "total_steps": len(ctx.plan),
        }

    @server.tool(
        name="blender_execute_plan",
        description="Execute a high-level task through the Master Orchestrator (planning, execution across specialists, quality validation).",
    )
    async def blender_execute_plan(user_request: str) -> Dict[str, Any]:
        """Plan and execute a high-level task with deterministic validation."""
        ctx = TaskPlanner.plan_workflow(user_request)
        orchestrator = get_orchestrator(client)
        return await orchestrator.execute(ctx)
