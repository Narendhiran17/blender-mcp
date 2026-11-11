# Blender AI Control MCP

## End-to-End Project Context, Product Specification, Architecture, and Development Roadmap

**Document purpose:** This is the single source of truth for building
the Blender AI Control MCP project. It consolidates the product intent,
scope, architecture, technology choices, Blender integration model, MCP
interface, AI-agent design, security requirements, repository structure,
testing strategy, and phased roadmap established so far.

**Project status:** Pre-development / Phase 1 ready\
**Initial target platform:** Windows desktop, running locally with
Blender installed\
**Product type:** Standalone, reusable Blender MCP server with a Blender
add-on/bridge\
**Primary objective:** Allow MCP-compatible AI clients and agents to
inspect, control, create, modify, validate, and render Blender projects
through structured, safe, reusable tools.

------------------------------------------------------------------------

# 1. Product Vision

Build a professional-grade, reusable **Blender AI Control MCP** that
exposes Blender's major capabilities through the Model Context Protocol
(MCP).

The product should let an AI assistant work with Blender in a controlled
and structured way. A user should be able to describe a 3D task in
natural language, while the AI plans the work, calls appropriate MCP
tools, executes operations inside Blender, inspects the results,
corrects issues, and returns a useful result.

Examples of intended requests:

-   Create a product model with a specified shape and dimensions.
-   Build a room, interior, or architectural scene.
-   Create and organize objects, collections, cameras, and lights.
-   Apply materials, textures, UVs, and shader-node configurations.
-   Create a character or game asset.
-   Rig and animate objects or characters.
-   Configure physics simulations.
-   Render a scene with specified output settings.
-   Inspect a project and report missing assets, invalid settings, or
    scene problems.
-   Prepare a model for export to a supported interchange format.

The project is intended to become a reusable foundation that can be
connected to different MCP-compatible AI clients. It is not initially a
separate end-user 3D editor or a replacement for Blender.

## 1.1 Product goals

1.  Provide structured MCP tools for Blender operations.
2.  Support a broad range of Blender workflows through domain-specific
    tools.
3.  Keep Blender execution local on the user's machine.
4.  Make operations reliable, observable, and recoverable.
5.  Prevent unsafe or unintended operations.
6.  Support AI-agent planning and multi-step workflows.
7.  Provide scene inspection and feedback so an agent can evaluate its
    work.
8.  Keep the core MCP server reusable and independent of any one AI
    client.
9.  Establish a maintainable architecture that can grow toward
    professional and enterprise use.

## 1.2 Non-goals for the first release

-   Replacing Blender's graphical interface.
-   Reimplementing the Blender engine.
-   Building a complete cloud rendering farm.
-   Supporting every Blender feature with perfect parity in the first
    milestone.
-   Allowing unrestricted AI-generated Python code to execute inside
    Blender.
-   Building a separate cross-platform desktop application before the
    MCP foundation is proven.

------------------------------------------------------------------------

# 2. Product Scope

The initial product scope is broad: cover the major Blender capability
areas through an extensible tool architecture. Implement and validate
these areas in phases rather than attempting all features at once.

## 2.1 Functional domains

  -----------------------------------------------------------------------
  Domain                              Intended capabilities
  ----------------------------------- -----------------------------------
  Scene management                    Create, inspect, rename, organize,
                                      save, and manage scenes and
                                      collections

  Object management                   Create, select, duplicate,
                                      transform, rename, delete, parent,
                                      and inspect objects

  Mesh modeling                       Create primitive meshes, edit
                                      geometry, perform common mesh
                                      operations, and inspect mesh data

  Modifiers                           Add, configure, inspect, apply,
                                      reorder, and remove modifiers

  Geometry Nodes                      Inspect and configure supported
                                      node groups and expose reusable
                                      operations

  Sculpting                           Support selected sculpt-related
                                      setup and inspection workflows
                                      where practical

  Retopology                          Provide supported mesh preparation
                                      and inspection workflows; advanced
                                      retopology can be a later milestone

  Materials                           Create and configure materials and
                                      shader nodes

  Textures                            Assign image textures, inspect
                                      texture references, and configure
                                      supported texture workflows

  UV mapping                          Create, inspect, and modify UV maps
                                      through supported operations

  Lighting                            Create and configure lights,
                                      lighting setups, and world
                                      illumination

  Cameras                             Create and configure cameras,
                                      framing, focal length, and camera
                                      selection

  Environment                         Configure world settings,
                                      backgrounds, and environment maps

  Rigging                             Create and inspect armatures,
                                      bones, parenting, and supported
                                      rigging operations

  Animation                           Create keyframes, inspect animation
                                      data, configure actions, and
                                      control timelines

  Physics                             Configure supported rigid-body,
                                      cloth, fluid, particle, and other
                                      simulation settings

  Rendering                           Configure render engine,
                                      resolution, samples, output, and
                                      render tasks

  Compositing                         Inspect and configure supported
                                      compositor node workflows

  Video Sequence Editor               Inspect and manage supported
                                      sequence-editor operations

  File and asset management           Open/save projects, inspect files,
                                      manage asset references, and export
                                      supported formats

  Inspection and validation           Report scene state, object
                                      properties, missing resources,
                                      invalid configuration, and workflow
                                      issues
  -----------------------------------------------------------------------

**Scope rule:** A domain is not considered complete merely because one
tool exists for it. Its supported operations, input schemas, validation
rules, failure modes, and tests must be documented.

## 2.2 Initial tool-count expectation

A first substantial release may contain approximately **60--80 MCP
tools**, distributed across the domains above. This is a planning
estimate, not a fixed requirement. Tool count must follow real workflow
coverage and should not be inflated by creating many redundant tools.

Prefer clear, composable tools with strict schemas over one giant tool
with dozens of unrelated parameters.

------------------------------------------------------------------------

# 3. Users and Main Use Cases

## 3.1 Intended users

-   3D artists who want AI assistance with repetitive Blender work.
-   Technical artists and developers building 3D pipelines.
-   Game-asset and product-visualization creators.
-   Architecture and interior-visualization workflows.
-   Developers building AI agents that need Blender access.
-   Teams that want controlled, auditable automation of Blender tasks.

## 3.2 Example end-to-end workflows

### Workflow A: Create a product scene

1.  User requests a product model and presentation scene.
2.  AI inspects the active Blender project.
3.  AI plans the object hierarchy and dimensions.
4.  AI creates and configures geometry.
5.  AI adds materials and textures.
6.  AI creates a camera and lights.
7.  AI configures render settings.
8.  AI renders a preview.
9.  AI inspects the scene and preview.
10. AI corrects issues and saves the project.

### Workflow B: Inspect an existing project

1.  AI connects to Blender.
2.  AI reads project and scene status.
3.  AI lists scenes, collections, objects, materials, cameras, and
    render settings.
4.  AI checks for missing resources and invalid configurations.
5.  AI produces a structured report.
6.  AI recommends fixes.
7.  AI applies only the fixes authorized by the user.

### Workflow C: Prepare an asset for export

1.  Inspect the selected object and its dependencies.
2.  Validate transforms, geometry, normals, UVs, and materials.
3.  Report problems.
4.  Apply approved corrections.
5.  Configure export options.
6.  Export to a supported format.
7.  Verify the output file and report its location.

------------------------------------------------------------------------

# 4. High-Level System Architecture

The system has five main layers.

``` text
+-----------------------------------------------------------+
|                    MCP-Compatible Client                  |
|          AI assistant / AI agent / MCP host                |
+-----------------------------+-----------------------------+
                              |
                              | MCP protocol (stdio)
                              v
+-----------------------------------------------------------+
|                    Python MCP Server                      |
|  Tool registry | Schemas | Validation | Resources | Prompts|
|  Permissions   | Task API | Logging    | Error mapping     |
+-----------------------------+-----------------------------+
                              |
                              | Authenticated localhost HTTP
                              v
+-----------------------------------------------------------+
|                  Local Blender Bridge                     |
|  HTTP endpoints | Authentication | Request queue           |
|  Task tracking  | Serialization   | Health/status          |
+-----------------------------+-----------------------------+
                              |
                              | Thread-safe queue
                              v
+-----------------------------------------------------------+
|                 Blender Add-on Runtime                    |
|  Main-thread dispatcher | Operation registry               |
|  Scene adapters         | Inspectors | Task manager          |
+-----------------------------+-----------------------------+
                              |
                              | Blender Python API (bpy)
                              v
+-----------------------------------------------------------+
|                     Blender Engine                        |
|  Scene | Objects | Meshes | Materials | Animation | Render |
|  Physics | Nodes | Compositor | Files                      |
+-----------------------------------------------------------+
```

## 4.1 Layer responsibilities

### Layer 1 --- MCP-compatible client

The client is the AI interface. It sends MCP tool calls and reads tool
results. The MCP server must not depend on one specific client.

### Layer 2 --- Python MCP server

Responsibilities:

-   Register and expose MCP tools.
-   Publish MCP resources and reusable prompts.
-   Validate all incoming arguments.
-   Apply permission checks.
-   Convert client requests into bridge requests.
-   Normalize bridge responses into MCP results.
-   Manage timeouts, task polling, and errors.
-   Keep tool definitions independent from Blender's internal
    implementation.

### Layer 3 --- Local Blender bridge

Responsibilities:

-   Provide authenticated local communication between the MCP server and
    Blender.
-   Accept structured requests.
-   Enqueue operations for Blender's main thread.
-   Track request and task status.
-   Return structured responses.
-   Expose health and status information.
-   Avoid calling Blender's Python API from background HTTP threads.

### Layer 4 --- Blender add-on runtime

Responsibilities:

-   Register the bridge and operation handlers.
-   Dispatch queued requests on Blender's main thread.
-   Execute approved operations through `bpy`.
-   Inspect the current project and scene.
-   Manage long-running tasks.
-   Return serializable results and meaningful errors.

### Layer 5 --- Blender engine

Blender performs the actual 3D work. The product controls Blender
through its supported Python API rather than reimplementing its engine.

------------------------------------------------------------------------

# 5. Blender Communication and Threading Design

This is a critical architectural requirement.

Blender's Python API (`bpy`) must be used on Blender's main thread. The
HTTP server may receive requests on a background thread, but that thread
must not directly manipulate Blender data.

## 5.1 Required request lifecycle

1.  MCP client calls a tool.
2.  MCP server validates the arguments and permissions.
3.  MCP server sends a request to the local bridge.
4.  Bridge authenticates the request.
5.  Bridge assigns or validates a request ID.
6.  Bridge places the request into a thread-safe queue.
7.  A Blender timer callback or equivalent main-thread dispatcher checks
    the queue.
8.  The dispatcher executes the registered operation on Blender's main
    thread.
9.  The operation returns a structured result.
10. The bridge updates the request/task state.
11. MCP server returns the result to the client.

## 5.2 Threading rules

-   Never call `bpy` directly from the HTTP server's background thread.
-   Never pass live Blender objects across threads.
-   Pass serializable identifiers and plain data through the queue.
-   Resolve Blender objects by validated identifiers on the main thread.
-   Keep each operation bounded where possible.
-   Use background task tracking for long-running operations such as
    renders.
-   Ensure cancellation and shutdown do not leave the queue in an
    inconsistent state.

## 5.3 Request envelope

A request should use a versioned, structured envelope. Example:

``` json
{
  "protocol_version": "1",
  "request_id": "req_01",
  "operation": "object.create_primitive",
  "arguments": {
    "primitive_type": "CUBE",
    "name": "ProductBody",
    "location": [0, 0, 0],
    "scale": [1, 1, 1]
  },
  "timeout_seconds": 30
}
```

The actual schema should be implemented and validated with Pydantic
models. The example is illustrative, not a final wire contract.

## 5.4 Response envelope

``` json
{
  "protocol_version": "1",
  "request_id": "req_01",
  "status": "completed",
  "result": {
    "object_name": "ProductBody",
    "object_type": "MESH"
  },
  "error": null
}
```

For failures, return a stable error code, concise message, and safe
diagnostic details. Do not expose secrets or internal stack traces to
the MCP client by default.

## 5.5 Long-running task lifecycle

Long-running operations should return a task ID rather than block
indefinitely.

Suggested task states:

-   `queued`
-   `running`
-   `completed`
-   `failed`
-   `cancel_requested`
-   `cancelled`
-   `timed_out`

The task manager should retain timestamps, progress where available,
operation name, and final result/error.

------------------------------------------------------------------------

# 6. Local Bridge API

The bridge should initially bind only to `127.0.0.1`.

Suggested endpoints:

  -----------------------------------------------------------------------
  Endpoint                Method                  Purpose
  ----------------------- ----------------------- -----------------------
  `/health`               GET                     Basic bridge health
                                                  check

  `/status`               GET                     Blender connection and
                                                  runtime status

  `/execute`              POST                    Submit a structured
                                                  operation

  `/tasks/{id}`           GET                     Read task state and
                                                  progress

  `/tasks/{id}/result`    GET                     Retrieve a completed
                                                  task result

  `/cancel`               POST                    Request cancellation
                                                  where supported

  `/scene`                GET                     Retrieve a scene
                                                  summary

  `/preview`              GET or POST             Obtain a preview
                                                  through a controlled
                                                  mechanism
  -----------------------------------------------------------------------

These are proposed internal bridge routes, not MCP tool names. Exact
HTTP methods and payloads must be finalized in the implementation
contract.

## 6.1 Bridge requirements

-   Localhost-only by default.
-   Random session token or equivalent authentication secret.
-   No unauthenticated execution endpoint.
-   Request size limits.
-   Strict operation allowlist.
-   Input validation.
-   Timeouts.
-   Structured logging.
-   Safe shutdown.
-   Clear connection status.
-   No arbitrary remote access in the initial version.

------------------------------------------------------------------------

# 7. MCP Interface Design

The MCP server should expose three types of capabilities:

1.  **Tools:** perform actions or inspections.
2.  **Resources:** provide read-oriented project and Blender context.
3.  **Prompts:** provide reusable workflow instructions.

## 7.1 Tool design principles

-   One tool should have one clear responsibility.
-   Use strict, descriptive input schemas.
-   Use stable object identifiers where possible; avoid relying only on
    names.
-   Make destructive behavior explicit.
-   Return structured results.
-   Include useful validation errors.
-   Use consistent naming, such as `object.create`, `object.inspect`, or
    `render.start`.
-   Avoid tools that accept arbitrary Python code.
-   Keep Blender-specific implementation details behind adapters.

## 7.2 Proposed tool domains

The following is the intended tool catalogue. Tool names are examples to
guide implementation; the final registry should be documented as it is
built.

### A. System and connection

-   `blender.health`
-   `blender.status`
-   `blender.version`
-   `blender.capabilities`

### B. Scene management

-   `scene.list`
-   `scene.inspect`
-   `scene.create`
-   `scene.set_active`
-   `scene.save`
-   `scene.configure`

### C. Object management

-   `object.list`
-   `object.inspect`
-   `object.create_primitive`
-   `object.rename`
-   `object.transform`
-   `object.duplicate`
-   `object.delete`
-   `object.set_parent`
-   `object.set_visibility`
-   `object.select`

### D. Mesh modeling

-   `mesh.inspect`
-   `mesh.add_geometry`
-   `mesh.edit`
-   `mesh.extrude`
-   `mesh.bevel`
-   `mesh.subdivide`
-   `mesh.merge`
-   `mesh.recalculate_normals`
-   `mesh.validate`

### E. Modifiers and Geometry Nodes

-   `modifier.list`
-   `modifier.add`
-   `modifier.configure`
-   `modifier.apply`
-   `modifier.remove`
-   `geometry_nodes.inspect`
-   `geometry_nodes.assign_group`
-   `geometry_nodes.configure`

### F. Materials, textures, and UVs

-   `material.list`
-   `material.create`
-   `material.configure`
-   `material.assign`
-   `material.inspect`
-   `texture.assign_image`
-   `uv.list`
-   `uv.unwrap`
-   `uv.inspect`

### G. Lighting, cameras, and environment

-   `light.create`
-   `light.configure`
-   `camera.create`
-   `camera.configure`
-   `camera.set_active`
-   `world.configure`
-   `environment.inspect`

### H. Rigging and animation

-   `armature.create`
-   `armature.inspect`
-   `rig.parent_mesh`
-   `animation.create_keyframe`
-   `animation.inspect`
-   `animation.configure`
-   `animation.playback_range`

### I. Physics and simulations

-   `physics.configure_rigidbody`
-   `physics.configure_cloth`
-   `physics.configure_fluid`
-   `physics.inspect`
-   `simulation.bake`
-   `simulation.inspect`

Support for each simulation type depends on Blender version, runtime
behavior, and test coverage.

### J. Rendering and compositing

-   `render.configure`
-   `render.preview`
-   `render.start`
-   `render.status`
-   `render.cancel`
-   `compositor.inspect`
-   `compositor.configure`

### K. Files, assets, and export

-   `project.open`
-   `project.save`
-   `project.inspect`
-   `asset.list`
-   `asset.inspect`
-   `asset.validate`
-   `export.model`
-   `export.status`

File operations must be restricted to approved workspaces unless the
user explicitly authorizes another location.

### L. Quality and validation

-   `validation.scene`
-   `validation.mesh`
-   `validation.materials`
-   `validation.assets`
-   `validation.render_settings`
-   `validation.export_readiness`

The catalogue should be adjusted based on actual Blender API support and
useful workflows. Do not expose placeholder tools that cannot perform
their advertised action.

## 7.3 MCP resources

Suggested read-oriented resources:

  Resource URI                  Content
  ----------------------------- --------------------------------------------
  `blender://system/info`       Blender version, platform, runtime details
  `blender://scene/active`      Active scene summary
  `blender://scene/objects`     Object inventory and key properties
  `blender://scene/materials`   Material inventory
  `blender://scene/cameras`     Camera inventory and active camera
  `blender://scene/animation`   Animation and timeline summary
  `blender://render/settings`   Current render configuration
  `blender://project/status`    Project path, save state, and status
  `blender://tasks/active`      Active and recent operation tasks

Resources should return concise, structured data. Large scene data
should support pagination or filtering.

## 7.4 Reusable MCP prompts

Suggested prompts:

-   Create a product model and presentation scene.
-   Create an architectural or interior scene.
-   Create a character or game asset.
-   Animate a selected object.
-   Inspect and explain the current scene.
-   Optimize a scene for rendering.
-   Diagnose and repair a mesh.
-   Prepare a model for export.
-   Configure a professional product render.

Prompts guide an AI client; they do not replace validation or permission
checks.

------------------------------------------------------------------------

# 8. AI Agent Architecture

The MCP server is the reliable control layer. AI agents are an optional
orchestration layer that plans and coordinates tools.

The core product must remain useful without a multi-agent framework. Any
agent framework should be replaceable and should not be tightly coupled
to the Blender bridge.

## 8.1 Proposed agent structure

``` text
                    Master Blender Agent
                            |
        +-------------------+-------------------+
        |                   |                   |
   Scene Agent         Modeling Agent       Quality Agent
        |                   |                   |
   Material Agent      Lighting Agent      Validation
        |                   |                   |
   Animation Agent    Simulation Agent     Inspection
        |                   |
   Rendering Agent    Export/Asset Agent
```

The Master Blender Agent is responsible for interpreting the user's
request, producing a plan, selecting specialists, coordinating
execution, checking results, and reporting completion.

Specialist agents are logical responsibilities. They do not all need to
be separate autonomous processes. Start with a single orchestrator and
well-defined task modules; split into separate agents only when that
adds measurable value.

## 8.2 Agent responsibilities

### Master Blender Agent

-   Understand the user's request.
-   Inspect the current project before changing it.
-   Break work into explicit tasks.
-   Select the right tools or specialist.
-   Maintain task state.
-   Enforce approval requirements.
-   Coordinate validation.
-   Summarize completed work and unresolved issues.

### Scene Agent

-   Inspect and organize scenes, collections, and objects.
-   Maintain naming and hierarchy conventions.

### Modeling Agent

-   Create and modify geometry.
-   Use mesh and modifier tools.
-   Check geometry after edits.

### Material Agent

-   Create and assign materials.
-   Configure shader nodes and textures.
-   Check missing image resources.

### Lighting Agent

-   Create lighting and environment setups.
-   Configure cameras and framing where appropriate.

### Animation Agent

-   Create keyframes and supported animation structures.
-   Inspect timing and playback ranges.

### Simulation Agent

-   Configure and run supported simulations.
-   Track long-running tasks and report failures.

### Rendering Agent

-   Configure render settings.
-   Start and track renders.
-   Return output locations and render metadata.

### Quality Agent

-   Run deterministic validations.
-   Inspect operation results.
-   Identify errors and missing dependencies.
-   Recommend or perform approved corrections.

## 8.3 Shared task context

Agents should share a structured task context containing:

-   Project ID and project path.
-   Active scene ID.
-   Object references and stable identifiers.
-   User request and acceptance criteria.
-   Execution plan.
-   Completed tasks.
-   Pending tasks.
-   Tool call results.
-   Validation results.
-   Checkpoint information.
-   Approval state.
-   Known errors and recovery actions.

Avoid relying on conversational memory alone for important execution
state.

## 8.4 Agent execution loop

Use the following loop:

``` text
Understand
   |
Inspect current Blender state
   |
Plan operations
   |
Validate plan and permissions
   |
Execute approved operations
   |
Inspect resulting scene
   |
Evaluate against acceptance criteria
   |
Correct issues if authorized
   |
Save/checkpoint
   |
Report result
```

This is a central product behavior: the agent should not assume that a
successful tool call means the visual or functional result is correct.

## 8.5 Visual feedback

A later milestone should support visual feedback:

1.  Request a viewport or render preview.
2.  Return the image through a supported MCP result mechanism.
3.  Let the AI evaluate the visual output.
4.  Compare it with the user's requested outcome.
5.  Propose or perform bounded corrections.
6.  Repeat until the acceptance criteria are met or the workflow reaches
    its iteration limit.

Use deterministic checks for measurable properties and visual evaluation
for appearance. Visual AI evaluation must not replace exact checks for
dimensions, object counts, file existence, or render configuration.

------------------------------------------------------------------------

# 9. Technology Stack

## 9.1 Core stack

  -----------------------------------------------------------------------
  Area                    Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Main language           Python 3.11+            MCP server and shared
                                                  logic

  3D application          Blender                 3D engine and UI

  Blender API             `bpy`, `bmesh`,         Scene and geometry
                          `mathutils`             control

  MCP implementation      Official MCP Python SDK MCP server and protocol

  Data validation         Pydantic                Request/response
                                                  schemas

  Configuration           Pydantic Settings       Environment and
                                                  configuration
                                                  management

  HTTP client             HTTPX                   MCP server to local
                                                  bridge communication

  Async support           Python `asyncio`        MCP and I/O
                                                  coordination

  Testing                 pytest, pytest-asyncio  Unit and integration
                                                  tests

  Linting                 Ruff                    Formatting and lint
                                                  checks

  Type checking           mypy                    Static type checks

  Optional agent          OpenAI Agents SDK       Reference orchestration
  framework                                       integration
  -----------------------------------------------------------------------

Pin and test compatible dependency versions before release. Do not
assume the newest version of every package is compatible with the
selected Blender and Python versions.

## 9.2 Important Blender Python compatibility note

Blender ships with its own Python runtime. The Python version used by
the MCP server and the Python version embedded in Blender may differ.

Therefore:

-   Keep the MCP server environment independent from Blender's embedded
    Python.
-   Install the Blender add-on using Blender's supported add-on
    installation process.
-   Avoid assuming that packages installed in the MCP server virtual
    environment are available inside Blender.
-   Keep add-on dependencies minimal.
-   Verify compatibility against the exact Blender release selected for
    development.
-   Document supported Blender versions.

## 9.3 Optional agent integration

The OpenAI Agents SDK may be used for a reference orchestrator, but the
MCP server itself should remain framework-neutral. Do not make the core
product depend on a single model provider.

------------------------------------------------------------------------

# 10. Repository Structure

Proposed repository layout:

``` text
blender-ai-control-mcp/
|
|-- blender_addon/
|   |-- __init__.py
|   |-- manifest.toml
|   |-- bridge/
|   |   |-- server.py
|   |   |-- auth.py
|   |   |-- request_queue.py
|   |   |-- dispatcher.py
|   |   |-- task_manager.py
|   |   |-- serializers.py
|   |
|   |-- operations/
|   |   |-- registry.py
|   |   |-- system.py
|   |   |-- scene.py
|   |   |-- objects.py
|   |   |-- mesh.py
|   |   |-- modifiers.py
|   |   |-- materials.py
|   |   |-- lighting.py
|   |   |-- cameras.py
|   |   |-- animation.py
|   |   |-- physics.py
|   |   |-- rendering.py
|   |   |-- files.py
|   |
|   |-- inspectors/
|   |   |-- scene_inspector.py
|   |   |-- object_inspector.py
|   |   |-- mesh_inspector.py
|   |   |-- material_inspector.py
|   |   |-- render_inspector.py
|   |
|   |-- security/
|   |   |-- permissions.py
|   |   |-- path_policy.py
|   |
|   |-- utils/
|       |-- errors.py
|       |-- logging.py
|       |-- versioning.py
|
|-- mcp_server/
|   |-- __init__.py
|   |-- main.py
|   |-- config.py
|   |-- client.py
|   |-- protocol.py
|   |-- registry.py
|   |-- resources.py
|   |-- prompts.py
|   |
|   |-- tools/
|   |   |-- system.py
|   |   |-- scene.py
|   |   |-- objects.py
|   |   |-- mesh.py
|   |   |-- modifiers.py
|   |   |-- materials.py
|   |   |-- lighting.py
|   |   |-- animation.py
|   |   |-- physics.py
|   |   |-- rendering.py
|   |   |-- files.py
|   |   |-- validation.py
|   |
|   |-- schemas/
|   |   |-- common.py
|   |   |-- requests.py
|   |   |-- responses.py
|   |   |-- objects.py
|   |   |-- materials.py
|   |   |-- rendering.py
|   |
|   |-- validation/
|       |-- arguments.py
|       |-- permissions.py
|
|-- agents/
|   |-- orchestrator.py
|   |-- task_context.py
|   |-- planner.py
|   |-- specialists/
|   |   |-- scene_agent.py
|   |   |-- modeling_agent.py
|   |   |-- material_agent.py
|   |   |-- lighting_agent.py
|   |   |-- animation_agent.py
|   |   |-- simulation_agent.py
|   |   |-- rendering_agent.py
|   |   |-- quality_agent.py
|
|-- shared/
|   |-- constants.py
|   |-- models.py
|   |-- errors.py
|   |-- protocol.py
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- blender/
|   |-- security/
|   |-- fixtures/
|
|-- scripts/
|   |-- install_addon.py
|   |-- check_blender.py
|   |-- run_server.py
|   |-- package_release.py
|
|-- config/
|   |-- default.yaml
|   |-- development.yaml
|
|-- docs/
|   |-- architecture.md
|   |-- api-contract.md
|   |-- tool-catalogue.md
|   |-- security.md
|   |-- setup-windows.md
|   |-- testing.md
|   |-- release.md
|
|-- .env.example
|-- .gitignore
|-- pyproject.toml
|-- README.md
|-- LICENSE
```

This is the target structure, not a requirement to create every file on
day one. Start with the smallest structure needed for Phase 1 and expand
it without changing the architectural boundaries.

------------------------------------------------------------------------

# 11. Security and Permission Model

The product controls a powerful desktop application and can modify or
delete user work. Security must be part of the architecture from the
beginning.

## 11.1 Mandatory controls

-   Bind the bridge to `127.0.0.1` by default.
-   Authenticate every bridge request using a random session token or
    equivalent.
-   Never expose the bridge to the public network by default.
-   Validate all MCP arguments and bridge payloads.
-   Use a strict operation registry and allowlist.
-   Do not expose unrestricted `execute_python_code`.
-   Restrict file access to approved workspaces.
-   Apply request size and execution time limits.
-   Log operations without logging secrets.
-   Use stable error codes.
-   Support checkpoints and recovery where practical.
-   Require explicit approval for destructive operations.
-   Make permission decisions in the server/bridge, not only in agent
    prompts.

## 11.2 Permission levels

  -----------------------------------------------------------------------
  Level                   Allowed behavior        Example
  ----------------------- ----------------------- -----------------------
  Read-only               Inspect Blender state   List objects, inspect
                                                  materials

  Bounded non-destructive Perform safe,           Create a new object,
                          reversible changes      add a camera

  Approval required       Destructive or          Delete objects,
                          high-impact changes     overwrite project,
                                                  apply destructive
                                                  modifiers

  Restricted              Arbitrary code or       Not exposed as a normal
                          external process        MCP tool
                          execution               
  -----------------------------------------------------------------------

The exact permission policy should be configurable, but safe defaults
must be enabled.

## 11.3 Destructive operation behavior

For destructive actions:

1.  Explain what will change.
2.  Identify the target object/project/file.
3.  Require user approval when policy says approval is necessary.
4.  Execute only the approved operation.
5.  Record the result.
6.  Provide a recovery path where possible.

A user approval in the AI conversation must be tied to the specific
action and target; it must not become blanket permission for unrelated
destructive operations.

------------------------------------------------------------------------

# 12. Reliability, Error Handling, and Recovery

## 12.1 Error categories

Define stable error categories, such as:

-   `BLENDER_NOT_RUNNING`
-   `BRIDGE_UNAVAILABLE`
-   `AUTHENTICATION_FAILED`
-   `INVALID_ARGUMENT`
-   `UNSUPPORTED_OPERATION`
-   `OBJECT_NOT_FOUND`
-   `PERMISSION_DENIED`
-   `OPERATION_FAILED`
-   `TASK_NOT_FOUND`
-   `TASK_TIMEOUT`
-   `TASK_CANCELLED`
-   `FILE_ACCESS_DENIED`
-   `BLENDER_VERSION_UNSUPPORTED`

## 12.2 Reliability requirements

-   Every request should have a request ID.
-   Every long-running task should have a task ID.
-   Tool results should distinguish success, failure, and pending
    execution.
-   Repeated requests should not accidentally duplicate destructive
    work.
-   Where appropriate, operations should be idempotent.
-   Save/checkpoint before high-impact workflows where practical.
-   On bridge restart, the MCP server should detect loss of connection
    and return a useful error.
-   On Blender shutdown, pending tasks should be marked appropriately.
-   Logs should make it possible to trace a tool call from MCP request
    to Blender execution.

------------------------------------------------------------------------

# 13. Testing Strategy

Testing must cover the MCP server, bridge, Blender integration,
security, and actual 3D outcomes.

## 13.1 Unit tests

Test:

-   Pydantic request and response schemas.
-   Tool argument validation.
-   Permission checks.
-   Operation registry behavior.
-   Serialization.
-   Error mapping.
-   Task state transitions.
-   File path policy.
-   MCP tool registration.

## 13.2 Bridge tests

Test:

-   Health and status routes.
-   Authentication.
-   Invalid requests.
-   Queue insertion.
-   Duplicate request IDs.
-   Timeouts.
-   Task status and result retrieval.
-   Cancellation behavior.
-   Safe shutdown.

## 13.3 Blender integration tests

Run tests against a supported Blender installation. Verify:

-   Add-on installation and enablement.
-   Bridge startup and shutdown.
-   Main-thread dispatch.
-   Primitive creation.
-   Object inspection and transformation.
-   Material creation and assignment.
-   Camera and light creation.
-   Project save.
-   Render configuration and preview.
-   Error handling when an object or scene does not exist.

## 13.4 End-to-end acceptance tests

The first complete acceptance test is:

1.  Start Blender.
2.  Enable the add-on.
3.  Start the MCP server.
4.  Connect an MCP-compatible client.
5.  Call the health tool.
6.  Read Blender status.
7.  Request creation of a cube.
8.  Verify the cube appears in Blender.
9.  Inspect the cube through MCP.
10. Save the project.
11. Confirm that the MCP response matches Blender's actual state.

Further acceptance workflows should cover materials, camera/light setup,
render preview, and scene validation.

## 13.5 Quality gates

A feature is not complete until:

-   Its schema is documented.
-   Its permissions are defined.
-   Success and failure cases are tested.
-   Blender main-thread requirements are respected.
-   The returned result is serializable.
-   The tool is documented.
-   A real Blender integration test has passed where applicable.

------------------------------------------------------------------------

# 14. Development Roadmap

Build the product incrementally. Do not attempt every Blender capability
in the first sprint.

The timeline below is an estimate for one developer. Actual duration
depends on Blender API complexity, testing depth, and the selected
release scope.

  -----------------------------------------------------------------------
  Phase                   Focus                   Main deliverable
  ----------------------- ----------------------- -----------------------
  Phase 1                 Foundation and          Working MCP-to-Blender
                          connection              connection

  Phase 2                 Core Blender controls   System, scene, object
                                                  tools

  Phase 3                 Modeling                Mesh and modifier tools

  Phase 4                 Materials and           Materials, textures,
                          environment             UVs, lights, cameras

  Phase 5                 Advanced 3D             Geometry Nodes,
                                                  rigging, animation

  Phase 6                 Simulation and          Physics tasks, render
                          rendering               management, compositing

  Phase 7                 AI orchestration        Master agent and
                                                  specialist task modules

  Phase 8                 Visual intelligence     Preview feedback and
                                                  correction loop

  Phase 9                 Hardening               Security, recovery,
                                                  performance,
                                                  compatibility

  Phase 10                Release                 Documentation,
                                                  packaging,
                                                  installation, examples
  -----------------------------------------------------------------------

A substantial first release was previously estimated at approximately
**41--61 working days** for one developer. This is an estimate, not a
commitment, and does not imply full parity with every Blender feature.

## 14.1 Phase 1 --- Foundation and connection

**Objective:** Prove that an MCP client can safely communicate with a
running Blender instance and execute one real operation.

Tasks:

1.  Create the repository.
2.  Create and activate a Python virtual environment.
3.  Install the MCP SDK and core dependencies.
4.  Create the minimal MCP server.
5.  Create the Blender add-on manifest and initialization module.
6.  Implement the local HTTP bridge.
7.  Add bridge authentication.
8.  Implement a thread-safe request queue.
9.  Implement Blender main-thread dispatch using a timer callback.
10. Add `/health` and `/status`.
11. Add MCP health and status tools.
12. Connect the MCP server to the bridge.
13. Add one operation: create a cube.
14. Call the operation from an MCP client.
15. Verify the cube in Blender.
16. Add unit and integration tests.
17. Document Windows setup and troubleshooting.

**Phase 1 acceptance criteria:**

-   Blender is running with the add-on enabled.
-   The bridge is available only on localhost.
-   The MCP server can authenticate with the bridge.
-   The MCP health tool returns a valid response.
-   The status tool reports Blender availability and version.
-   The cube-creation tool creates a cube through the main-thread
    dispatcher.
-   No `bpy` calls are made from the HTTP background thread.
-   Errors are returned in a structured form.
-   A basic test confirms the end-to-end flow.

## 14.2 Phase 2 --- Core Blender controls

Implement:

-   Scene listing and inspection.
-   Object listing and inspection.
-   Object creation, rename, transform, duplicate, selection, and
    visibility.
-   Project save.
-   Stable object references.
-   Consistent schemas and error handling.

Acceptance: the AI can inspect and perform basic scene/object workflows
without direct code execution.

## 14.3 Phase 3 --- Modeling

Implement:

-   Primitive creation.
-   Common mesh edits.
-   Extrude, bevel, subdivide, merge, and normal operations.
-   Mesh validation.
-   Modifier management.

Acceptance: an AI client can create and modify simple product geometry
through multiple structured tool calls.

## 14.4 Phase 4 --- Materials and environment

Implement:

-   Material creation and assignment.
-   Supported shader-node configuration.
-   Texture assignment.
-   UV inspection and basic unwrap operations.
-   Light and camera configuration.
-   World/environment configuration.

Acceptance: an AI client can create a basic product presentation scene.

## 14.5 Phase 5 --- Advanced 3D

Implement selected and tested workflows for:

-   Geometry Nodes.
-   Armatures and rigging.
-   Keyframe animation.
-   Actions and timeline inspection.
-   Additional mesh and asset workflows.

Acceptance: supported advanced workflows are documented and
integration-tested.

## 14.6 Phase 6 --- Simulation and rendering

Implement:

-   Supported physics configuration.
-   Simulation baking and task tracking.
-   Render settings.
-   Preview rendering.
-   Full render task management.
-   Cancellation where supported.
-   Compositor inspection and supported configuration.

Acceptance: the AI can configure a scene, launch a render, track its
status, and report the output.

## 14.7 Phase 7 --- AI orchestration

Implement:

-   Task context.
-   Planner.
-   Master orchestrator.
-   Specialist task modules.
-   Permission-aware planning.
-   Tool-result evaluation.
-   Retry and recovery policies.

Acceptance: a multi-step request can be planned, executed, validated,
and reported.

## 14.8 Phase 8 --- Visual intelligence

Implement:

-   Preview image retrieval.
-   Visual evaluation integration.
-   Iterative correction loop.
-   Iteration limits and stop conditions.
-   User review and approval checkpoints.

Acceptance: the agent can compare a preview with a request and perform
bounded corrections.

## 14.9 Phase 9 --- Production hardening

Implement:

-   Security review.
-   Performance profiling.
-   Compatibility testing.
-   Failure recovery.
-   Structured logs and diagnostics.
-   Packaging and upgrade behavior.
-   Documentation and support guidance.

## 14.10 Phase 10 --- Release

Deliver:

-   Versioned MCP server package.
-   Blender add-on package.
-   Installation guide.
-   MCP client configuration examples.
-   Supported Blender version matrix.
-   Tool catalogue.
-   Security documentation.
-   Test report.
-   Example workflows.
-   Known limitations.

------------------------------------------------------------------------

# 15. Windows Development Setup

The initial development environment is Windows 11 with Blender installed
locally.

## 15.1 Prerequisites

-   Windows 11.
-   Python 3.11 or a version confirmed compatible with the selected MCP
    SDK.
-   Blender installed.
-   Git.
-   VS Code or another Python IDE.
-   PowerShell.
-   An MCP-compatible client for integration testing.

## 15.2 Initial commands

Run in PowerShell:

``` powershell
mkdir blender-ai-control-mcp
cd blender-ai-control-mcp

python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install "mcp[cli]>=2,<3" pydantic pydantic-settings httpx pytest pytest-asyncio
```

These are initial development dependencies. Before implementation is
considered stable, pin verified versions in `pyproject.toml` and test
them against the selected Python and Blender versions.

If PowerShell blocks virtual-environment activation, use the appropriate
execution-policy setting for the current user or invoke the
environment's Python executable directly. Do not weaken system-wide
security settings unnecessarily.

## 15.3 Initial `pyproject.toml` dependency direction

``` toml
[project]
name = "blender-ai-control-mcp"
version = "0.1.0"
description = "A local MCP server and Blender add-on for structured AI control of Blender."
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=2,<3",
    "pydantic",
    "pydantic-settings",
    "httpx",
]

[project.optional-dependencies]
agents = [
    "openai-agents",
]
dev = [
    "pytest",
    "pytest-asyncio",
    "ruff",
    "mypy",
]
```

This is a starting dependency declaration. Resolve and pin tested
versions before sharing or releasing the package.

------------------------------------------------------------------------

# 16. Configuration and Environment Variables

Use environment-based configuration for secrets and machine-specific
settings.

Suggested `.env.example`:

``` dotenv
BLENDER_BRIDGE_HOST=127.0.0.1
BLENDER_BRIDGE_PORT=8765
BLENDER_BRIDGE_TOKEN=replace-with-a-random-local-secret
BLENDER_BRIDGE_TIMEOUT_SECONDS=30
BLENDER_WORKSPACE_PATH=
BLENDER_LOG_LEVEL=INFO
BLENDER_ALLOWED_OPERATIONS=*
```

Important:

-   `.env.example` contains placeholders only.
-   Never commit a real bridge token.
-   Add `.env` to `.gitignore`.
-   Do not treat `BLENDER_ALLOWED_OPERATIONS=*` as a safe production
    default. Use an explicit allowlist for normal use.
-   The bridge and MCP server must agree on the token and protocol
    version.
-   Validate workspace paths before enabling file operations.

------------------------------------------------------------------------

# 17. Logging and Observability

Logs should make it possible to trace a request from the MCP client to
Blender execution.

Each log event should include, where relevant:

-   Timestamp.
-   Request ID.
-   Task ID.
-   Operation name.
-   Execution layer.
-   Status.
-   Duration.
-   Blender version.
-   Error code.
-   Safe diagnostic message.

Do not log:

-   Authentication tokens.
-   Private file contents.
-   Unnecessary personal data.
-   Sensitive environment variables.

Provide a diagnostic/status operation that helps a user determine
whether Blender, the add-on, the bridge, and the MCP server are
connected.

------------------------------------------------------------------------

# 18. Versioning and Compatibility

The product has at least three independently versioned compatibility
surfaces:

1.  MCP server version.
2.  Blender add-on version.
3.  Bridge protocol version.

Requirements:

-   Include a protocol version in requests and responses.
-   Reject incompatible protocol versions with a clear error.
-   Maintain a tested Blender version matrix.
-   Check Blender capabilities at runtime rather than assuming every API
    exists.
-   Document deprecated tools and migration behavior.
-   Keep the MCP tool schema stable where possible.
-   Add compatibility tests before supporting a new Blender release.

------------------------------------------------------------------------

# 19. Documentation Deliverables

The repository should maintain:

  -----------------------------------------------------------------------
  Document                            Required content
  ----------------------------------- -----------------------------------
  `README.md`                         Product overview, prerequisites,
                                      quick start

  `docs/architecture.md`              System layers, data flow, threading

  `docs/api-contract.md`              Bridge request/response contract

  `docs/tool-catalogue.md`            MCP tools, arguments, permissions,
                                      results

  `docs/security.md`                  Threat model, authentication,
                                      permissions

  `docs/setup-windows.md`             Windows installation and
                                      configuration

  `docs/testing.md`                   Test strategy and execution

  `docs/release.md`                   Packaging, versioning, release
                                      process
  -----------------------------------------------------------------------

Update documentation whenever a tool, endpoint, permission, or protocol
contract changes.

------------------------------------------------------------------------

# 20. Definition of Done

A feature is complete only when all applicable criteria are met:

-   The feature has a clear user-facing purpose.
-   Its tool or resource contract is documented.
-   Inputs are validated.
-   Permissions are enforced.
-   Blender API calls occur on the main thread.
-   Results are structured and serializable.
-   Errors are mapped to stable error codes.
-   Unit tests pass.
-   Blender integration tests pass where required.
-   Logs are useful and do not expose secrets.
-   The documentation is updated.
-   The feature does not break previously completed workflows.

A phase is complete only when its acceptance criteria pass. Do not mark
a phase complete merely because its files or UI elements exist.

------------------------------------------------------------------------

# 21. Architectural Decisions and Constraints

These decisions are the current project baseline. Do not change them
casually.

1.  **Product direction:** Build a standalone, reusable Blender AI MCP
    server first.
2.  **Execution model:** Run locally on Windows with Blender installed.
3.  **Blender integration:** Use a Blender add-on and local bridge.
4.  **Communication:** MCP server communicates with the add-on through
    an authenticated localhost bridge.
5.  **Threading:** Blender API calls run only on Blender's main thread
    through a queue and dispatcher.
6.  **MCP design:** Use structured tools, resources, and prompts.
7.  **Scope:** Cover all major Blender domains progressively.
8.  **AI design:** Keep orchestration separate from the core MCP server.
9.  **Security:** No unrestricted Python execution tool; use allowlisted
    operations and explicit approvals.
10. **Development strategy:** Complete and test each phase before
    expanding.
11. **Architecture stability:** Do not introduce unrelated products,
    services, or frameworks without a concrete requirement.
12. **Quality:** Prefer tested, maintainable functionality over a large
    number of incomplete tools.

------------------------------------------------------------------------

# 22. Known Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  Blender API called from the wrong   Queue requests and dispatch through
  thread                              Blender's main thread

  Blender and server Python versions  Keep environments separate and
  differ                              minimize add-on dependencies

  Blender closes while a task is      Detect disconnection and mark tasks
  running                             with a stable failure state

  Long renders block requests         Use task IDs and asynchronous
                                      status polling

  AI performs destructive actions     Enforce permission checks and
                                      approval requirements

  AI creates incorrect geometry       Inspect and validate results; use
                                      preview feedback later

  Tool catalogue becomes too large    Use domain modules, consistent
                                      schemas, and workflow-driven
                                      prioritization

  Blender API changes between         Runtime capability checks and
  releases                            compatibility matrix

  File operations affect unintended   Workspace restrictions and path
  paths                               validation

  Agent framework becomes tightly     Keep agent orchestration optional
  coupled                             and framework-neutral

  Scope expands faster than testing   Phase gates and definition of done
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 23. Official Technical References

Use official documentation as the primary reference and verify version
compatibility during implementation.

-   Blender Python API: https://docs.blender.org/api/current/
-   Blender Python API gotchas:
    https://docs.blender.org/api/current/info_gotchas.html
-   Blender manual: https://docs.blender.org/manual/en/latest/
-   MCP documentation: https://modelcontextprotocol.io/
-   MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
-   OpenAI Agents SDK: https://openai.github.io/openai-agents-python/

These links are reference starting points. Confirm the current API and
package behavior before implementing or releasing a feature.

------------------------------------------------------------------------

# 24. Immediate Next Action --- Start Phase 1

Do not begin by implementing all 60--80 tools. First prove the
end-to-end connection.

## Phase 1 execution checklist

-   [ ] Create `blender-ai-control-mcp` repository.
-   [ ] Initialize Git.
-   [ ] Create Python virtual environment.
-   [ ] Install and verify MCP/Pydantic/HTTPX dependencies.
-   [ ] Create minimal `mcp_server` package.
-   [ ] Create minimal Blender add-on package and manifest.
-   [ ] Install and enable the add-on in Blender.
-   [ ] Start authenticated localhost bridge.
-   [ ] Implement thread-safe request queue.
-   [ ] Implement main-thread timer dispatcher.
-   [ ] Add bridge health and status endpoints.
-   [ ] Add MCP health and status tools.
-   [ ] Connect MCP server to the bridge.
-   [ ] Add `object.create_primitive` for a cube.
-   [ ] Invoke cube creation through the MCP client.
-   [ ] Verify the cube in Blender.
-   [ ] Add tests for validation, authentication, queueing, and the
    end-to-end flow.
-   [ ] Record the working setup and commands in
    `docs/setup-windows.md`.

## Phase 1 completion proof

The phase is complete only when a request made through an MCP client
creates a cube in the running Blender application through the
authenticated bridge and main-thread dispatcher, and the resulting
object can be inspected through MCP.

------------------------------------------------------------------------

# 25. Instructions for AI Coding Agents Working on This Repository

Any AI coding agent contributing to this project must follow these
rules:

1.  Read this document before changing the architecture.
2.  Treat the architectural decisions in Section 21 as the baseline.
3.  Work on the current phase only unless explicitly instructed
    otherwise.
4.  Do not remove, rename, or silently replace previously implemented
    features.
5.  Inspect the existing repository before creating or modifying files.
6.  Preserve existing public interfaces unless a migration is explicitly
    planned.
7.  Do not invent Blender API methods; verify them against the official
    API.
8.  Never call `bpy` from a background HTTP thread.
9.  Do not add arbitrary Python execution as an MCP capability.
10. Validate inputs at the MCP boundary and again at sensitive execution
    boundaries.
11. Add or update tests for every meaningful behavior change.
12. Update documentation when contracts or behavior change.
13. Do not add unnecessary dependencies or unrelated architecture.
14. Explain which files changed, why they changed, how to run the code,
    and how to verify the result.
15. If a requirement conflicts with this document, identify the conflict
    and ask for a decision rather than silently changing the product
    direction.
16. Do not claim a feature is complete unless its acceptance criteria
    and tests pass.
17. Prefer small, reviewable implementation steps that preserve a
    working system.

------------------------------------------------------------------------

# Final Product Statement

**Blender AI Control MCP** is a local-first, secure, extensible MCP
control layer for Blender. It connects MCP-compatible AI clients to
Blender through a Python MCP server, an authenticated localhost bridge,
and a Blender add-on that executes operations safely on Blender's main
thread. Its long-term capability covers scene creation and inspection,
modeling, materials, lighting, animation, simulation, rendering, asset
management, validation, and AI-driven multi-step workflows.

The immediate priority is to complete Phase 1 and prove the full
MCP-to-Blender cube-creation workflow before expanding the product.
