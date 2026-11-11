"""Physics and simulation tools for MCP Server."""

from typing import Any, Dict, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.client import BlenderBridgeClient, default_client


def register_physics_tools(server: MCPServer, client: BlenderBridgeClient = default_client) -> None:
    """Register physics and simulation tools with the MCP server."""

    @server.tool(
        name="blender_configure_rigidbody",
        description="Add or configure rigid body physics on an object (mass, friction, restitution, shape, active/passive).",
    )
    async def blender_configure_rigidbody(
        name: str,
        type: str = "ACTIVE",
        mass: Optional[float] = None,
        friction: Optional[float] = None,
        restitution: Optional[float] = None,
        collision_shape: Optional[str] = None,
        kinematic: Optional[bool] = None,
        enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Configure rigid body physics on an object."""
        args: Dict[str, Any] = {"name": name, "type": type}
        if mass is not None:
            args["mass"] = mass
        if friction is not None:
            args["friction"] = friction
        if restitution is not None:
            args["restitution"] = restitution
        if collision_shape is not None:
            args["collision_shape"] = collision_shape
        if kinematic is not None:
            args["kinematic"] = kinematic
        if enabled is not None:
            args["enabled"] = enabled
        return await client.execute("physics.configure_rigidbody", args)

    @server.tool(
        name="blender_configure_cloth",
        description="Add or configure cloth simulation modifier on an object (mass, tension, compression, shear, bending).",
    )
    async def blender_configure_cloth(
        name: str,
        mass: Optional[float] = None,
        tension_stiffness: Optional[float] = None,
        compression_stiffness: Optional[float] = None,
        shear_stiffness: Optional[float] = None,
        bending_stiffness: Optional[float] = None,
        shrink_factor: Optional[float] = None,
        use_collision: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Configure cloth simulation on an object."""
        args: Dict[str, Any] = {"name": name}
        if mass is not None:
            args["mass"] = mass
        if tension_stiffness is not None:
            args["tension_stiffness"] = tension_stiffness
        if compression_stiffness is not None:
            args["compression_stiffness"] = compression_stiffness
        if shear_stiffness is not None:
            args["shear_stiffness"] = shear_stiffness
        if bending_stiffness is not None:
            args["bending_stiffness"] = bending_stiffness
        if shrink_factor is not None:
            args["shrink_factor"] = shrink_factor
        if use_collision is not None:
            args["use_collision"] = use_collision
        return await client.execute("physics.configure_cloth", args)

    @server.tool(
        name="blender_inspect_physics",
        description="Inspect all physics settings active on an object (rigid body, cloth, collision, particle systems).",
    )
    async def blender_inspect_physics(name: str) -> Dict[str, Any]:
        """Inspect physics on an object."""
        return await client.execute("physics.inspect", {"name": name})

    @server.tool(
        name="blender_bake_simulation",
        description="Configure or bake simulation cache range (e.g. 'RIGIDBODY').",
    )
    async def blender_bake_simulation(
        simulation_type: str = "RIGIDBODY",
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Bake simulation cache."""
        args: Dict[str, Any] = {"simulation_type": simulation_type}
        if frame_start is not None:
            args["frame_start"] = frame_start
        if frame_end is not None:
            args["frame_end"] = frame_end
        return await client.execute("simulation.bake", args)
