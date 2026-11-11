# Blender AI Control MCP — Tool Catalogue

Complete reference for all 71 MCP tools exposed by the **Blender AI Control MCP Server**.

---

## 1. System & Connection Tools (3)

### `blender_health`
* **Description:** Check if the local Blender bridge is running and reachable.
* **Arguments:** None
* **Returns:** Health status and protocol version.

### `blender_status`
* **Description:** Retrieve real-time project and scene status from Blender (version, active scene, objects count, active selection, dirty state).
* **Arguments:** None

### `blender_version`
* **Description:** Get Blender version and build platform information.
* **Arguments:** None

---

## 2. Scene & Collection Tools (8)

### `blender_list_scenes`
* **Description:** List all scenes in the current project with their render engines, active cameras, and object counts.
* **Arguments:** None

### `blender_inspect_scene`
* **Description:** Inspect detailed configuration of a scene (resolution, FPS, active camera, render engine, units, collections).
* **Arguments:**
  * `name` *(string, optional)*: Name of the scene (defaults to active scene).

### `blender_create_scene`
* **Description:** Create a new scene in the project.
* **Arguments:**
  * `name` *(string, default "New Scene")*: Name of the new scene.
  * `setup_mode` *(string, default "NEW")*: `"NEW"`, `"EMPTY"`, `"LINK_COPY"`, or `"FULL_COPY"`.

### `blender_set_active_scene`
* **Description:** Switch the active scene in Blender to the specified scene.
* **Arguments:**
  * `name` *(string, required)*: Name of the target scene.

### `blender_save_project`
* **Description:** Save the Blender project (.blend). If never saved before, `filepath` must be provided.
* **Arguments:**
  * `filepath` *(string, optional)*: Absolute path to save the `.blend` file.

### `blender_list_collections`
* **Description:** List all collections in the active scene and their member objects.
* **Arguments:** None

### `blender_create_collection`
* **Description:** Create a new collection, optionally nested under a parent collection.
* **Arguments:**
  * `name` *(string, required)*: Collection name.
  * `parent_collection` *(string, optional)*: Parent collection name.

### `blender_link_to_collection`
* **Description:** Link an object into a collection, with option to unlink it from all other collections.
* **Arguments:**
  * `object_name` *(string, required)*: Object to link.
  * `collection_name` *(string, required)*: Target collection.
  * `unlink_from_others` *(boolean, default false)*: Whether to remove the object from all other collections.

---

## 3. Object Management Tools (10)

### `blender_create_primitive`
* **Description:** Create a 3D primitive mesh in Blender.
* **Arguments:**
  * `primitive_type` *(string, default "CUBE")*: `"CUBE"`, `"UV_SPHERE"`, `"CYLINDER"`, `"PLANE"`, `"CONE"`, `"TORUS"`.
  * `name` *(string, optional)*: Name for newly created object.
  * `location` *(float array, default [0,0,0])*: `[X, Y, Z]` location.
  * `rotation` *(float array, default [0,0,0])*: `[X, Y, Z]` Euler rotation in radians.
  * `scale` *(float array, default [1,1,1])*: `[X, Y, Z]` scale multiplier.
  * `size` *(float, default 2.0)*: Overall dimensions/radius.

### `blender_inspect_object`
* **Description:** Inspect detailed properties of an object in Blender.
* **Arguments:**
  * `name` *(string, required)*: Name of object to inspect.
* **Returns:** Transforms, dimensions, vertex/poly count, parent, children, collections, materials, and modifiers.

### `blender_list_objects`
* **Description:** List objects in active scene, optionally filtered by type or collection.
* **Arguments:**
  * `object_type` *(string, optional)*: e.g. `"MESH"`, `"CAMERA"`, `"LIGHT"`.
  * `collection` *(string, optional)*: Filter by collection name.

### `blender_rename_object`
* **Description:** Rename an existing object in Blender.
* **Arguments:**
  * `old_name` *(string, required)*: Current name.
  * `new_name` *(string, required)*: New name.

### `blender_transform_object`
* **Description:** Set or adjust location, rotation, or scale of an object.
* **Arguments:**
  * `name` *(string, required)*: Object name.
  * `location` *(float array, optional)*: `[X, Y, Z]` location.
  * `rotation` *(float array, optional)*: `[X, Y, Z]` Euler rotation in radians.
  * `scale` *(float array, optional)*: `[X, Y, Z]` scale.
  * `relative` *(boolean, default false)*: If true, adds/multiplies relative to existing transforms.

### `blender_duplicate_object`
* **Description:** Duplicate an object (deep copy or linked) with optional offset and new name.
* **Arguments:**
  * `name` *(string, required)*: Object to duplicate.
  * `new_name` *(string, optional)*: Name for duplicated copy.
  * `linked` *(boolean, default false)*: Shared mesh data if true.
  * `offset` *(float array, optional)*: `[X, Y, Z]` translation offset.

### `blender_delete_object`
* **Description:** Delete an object from Blender and unreference data blocks.
* **Arguments:**
  * `name` *(string, required)*: Name of object to delete.
  * `delete_data` *(boolean, default true)*: Whether to clean up unreferenced mesh data.

### `blender_set_parent`
* **Description:** Parent a child object to a parent object, or unparent if parent_name is omitted.
* **Arguments:**
  * `child_name` *(string, required)*: Name of child object.
  * `parent_name` *(string, optional)*: Name of parent object (omit or null to unparent).
  * `keep_transform` *(boolean, default true)*: Preserve world space transform without snapping.

### `blender_set_visibility`
* **Description:** Set object visibility in 3D viewport and/or final render.
* **Arguments:**
  * `name` *(string, required)*: Name of object.
  * `hide_viewport` *(boolean, optional)*: Show/hide in viewport.
  * `hide_render` *(boolean, optional)*: Show/hide in render.

### `blender_select_object`
* **Description:** Select or deselect an object, optionally deselect other objects, and set as active object.
* **Arguments:**
  * `name` *(string, optional)*: Target object.
  * `select` *(boolean, default true)*: Select or deselect.
  * `deselect_others` *(boolean, default false)*: Clear other selections.
  * `set_active` *(boolean, default true)*: Set as active object in context.

---

## 4. Mesh Modeling Tools (8)

### `blender_inspect_mesh`
* **Description:** Inspect detailed mesh topology: vertex, edge, and polygon counts, non-manifold edges/vertices, loose elements, watertightness status, and UV layers.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.

### `blender_subdivide_mesh`
* **Description:** Subdivide mesh faces and edges by a specified number of cuts and smoothness.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `cuts` *(integer, default 1)*: Number of cuts.
  * `smoothness` *(float, default 0.0)*: Smoothness factor (0.0 to 1.0).

### `blender_bevel_mesh`
* **Description:** Bevel edges or vertices of a mesh object.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `offset` *(float, default 0.1)*: Bevel width.
  * `segments` *(integer, default 1)*: Number of bevel segments.
  * `affect` *(string, default "EDGES")*: `"EDGES"` or `"VERTICES"`.

### `blender_extrude_mesh`
* **Description:** Extrude faces of a mesh along a direction vector by a given distance.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `direction` *(float array, default [0, 0, 1])*: Direction vector `[X, Y, Z]`.
  * `distance` *(float, default 1.0)*: Distance to extrude.
  * `face_indices` *(integer array, optional)*: Specific face indices to extrude (defaults to all).

### `blender_merge_vertices`
* **Description:** Merge vertices within a distance threshold (remove doubles).
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `distance` *(float, default 0.0001)*: Merge threshold distance.

### `blender_recalculate_normals`
* **Description:** Recalculate mesh face normals consistently outward or inward.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `inside` *(boolean, default false)*: Whether to invert normals inward.

### `blender_shade_smooth`
* **Description:** Set smooth shading or flat faceted shading on mesh polygons.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `smooth` *(boolean, default true)*: Enable smooth shading (True) or flat shading (False).

### `blender_validate_mesh`
* **Description:** Comprehensive mesh validation: checks non-manifold edges/vertices, loose geometry, zero-area faces, and watertightness for export or 3D printing.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.

---

## 5. Modifier Management Tools (5)

### `blender_list_modifiers`
* **Description:** List all modifiers on an object with their types, parameters, and display flags.
* **Arguments:**
  * `object_name` *(string, required)*: Name of object.

### `blender_add_modifier`
* **Description:** Add a modifier to an object (e.g. `'SUBSURF'`, `'BEVEL'`, `'SOLIDIFY'`, `'MIRROR'`, `'ARRAY'`, `'BOOLEAN'`, `'DECIMATE'`, `'REMESH'`).
* **Arguments:**
  * `object_name` *(string, required)*: Name of object.
  * `modifier_type` *(string, required)*: Modifier type enum.
  * `name` *(string, optional)*: Custom name for modifier.
  * `properties` *(object, optional)*: Initial properties (e.g. `{"levels": 2, "thickness": 0.2}`).

### `blender_configure_modifier`
* **Description:** Update settings on an existing modifier.
* **Arguments:**
  * `object_name` *(string, required)*: Name of object.
  * `modifier_name` *(string, required)*: Modifier name.
  * `properties` *(object, required)*: Property key-values to configure.

### `blender_apply_modifier`
* **Description:** Permanently bake/apply a modifier into the object's mesh geometry.
* **Arguments:**
  * `object_name` *(string, required)*: Name of object.
  * `modifier_name` *(string, required)*: Name of modifier to apply.

### `blender_remove_modifier`
* **Description:** Remove a modifier from an object's stack.
* **Arguments:**
  * `object_name` *(string, required)*: Name of object.
  * `modifier_name` *(string, required)*: Name of modifier to remove.

---

## 6. Materials, Textures, & UV Tools (9)

### `blender_list_materials`
* **Description:** List all materials in the project or assigned to a specific object.
* **Arguments:**
  * `object_name` *(string, optional)*: Optional filter by object name.

### `blender_create_material`
* **Description:** Create a new Principled BSDF material.
* **Arguments:**
  * `name` *(string, default "NewMaterial")*: Material name.
  * `base_color` *(float array, optional)*: `[R, G, B]` (0.0 to 1.0).
  * `roughness` *(float, optional)*: Roughness factor (0.0 to 1.0).
  * `metallic` *(float, optional)*: Metallic factor (0.0 to 1.0).
  * `specular` *(float, optional)*: Specular factor.

### `blender_configure_material`
* **Description:** Configure Principled BSDF parameters (base_color, roughness, metallic, transmission, emission_color, emission_strength, alpha, ior).
* **Arguments:**
  * `name` *(string, required)*: Name of material to configure.
  * `base_color`, `roughness`, `metallic`, `specular`, `transmission`, `emission_color`, `emission_strength`, `alpha`, `ior`.

### `blender_assign_material`
* **Description:** Assign a material to an object slot.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.
  * `material_name` *(string, required)*: Material to assign.
  * `slot_index` *(integer, optional)*: Material slot index (default 0).

### `blender_inspect_material`
* **Description:** Inspect detailed input socket values of a material's Principled BSDF node.
* **Arguments:**
  * `name` *(string, required)*: Material name.

### `blender_assign_image_texture`
* **Description:** Load an image texture file and connect it to a material shader input socket (e.g. 'Base Color').
* **Arguments:**
  * `material_name` *(string, required)*: Material to modify.
  * `image_path` *(string, required)*: Absolute path to image file.
  * `target_socket` *(string, default "Base Color")*: Input socket name.

### `blender_list_uv_layers`
* **Description:** List UV layers on a mesh object.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.

### `blender_unwrap_uv`
* **Description:** Automatically unwrap mesh UVs using Smart UV Project, Cube, Sphere, or Cylinder projection.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.
  * `method` *(string, default "SMART")*: `"SMART"`, `"CUBE"`, `"SPHERE"`, `"CYLINDER"`.
  * `island_margin` *(float, default 0.01)*: Spacing between UV islands.
  * `angle_limit` *(float, default 66.0)*: Smart project angle threshold in degrees.

### `blender_inspect_uv`
* **Description:** Inspect UV coverage and layer statistics on an object.
* **Arguments:**
  * `name` *(string, required)*: Mesh object name.

---

## 7. Lighting, Camera, & Environment Tools (7)

### `blender_create_light`
* **Description:** Create a light source in the scene.
* **Arguments:**
  * `light_type` *(string, default "POINT")*: `"POINT"`, `"SUN"`, `"SPOT"`, `"AREA"`.
  * `name` *(string, optional)*: Light object name.
  * `location` *(float array, default [0, 0, 5])*: `[X, Y, Z]` location.
  * `rotation` *(float array, default [0, 0, 0])*: `[X, Y, Z]` Euler rotation.
  * `energy` *(float, default 1000.0)*: Power in Watts.
  * `color` *(float array, default [1, 1, 1])*: `[R, G, B]` light color.

### `blender_configure_light`
* **Description:** Configure light power, color, type, and spot beam angle.
* **Arguments:**
  * `name` *(string, required)*: Light object name.
  * `energy`, `color`, `light_type`, `spot_size`.

### `blender_create_camera`
* **Description:** Create a camera object with focal length (mm) and clipping ranges.
* **Arguments:**
  * `name` *(string, default "Camera")*: Camera name.
  * `location` *(float array, default [0, -5, 2])*: `[X, Y, Z]` location.
  * `rotation` *(float array, default [1.3, 0, 0])*: `[X, Y, Z]` Euler rotation in radians.
  * `focal_length` *(float, default 50.0)*: Lens focal length in mm.
  * `clip_start` *(float, default 0.1)*: Near clipping plane.
  * `clip_end` *(float, default 1000.0)*: Far clipping plane.
  * `set_active` *(boolean, default true)*: Set as active rendering camera.

### `blender_configure_camera`
* **Description:** Configure focal length (mm) or clipping distances on an existing camera.
* **Arguments:**
  * `name` *(string, required)*: Camera name.
  * `focal_length`, `clip_start`, `clip_end`.

### `blender_set_active_camera`
* **Description:** Set the specified camera as the active rendering camera for the scene.
* **Arguments:**
  * `name` *(string, required)*: Camera name.

### `blender_configure_world`
* **Description:** Configure world illumination (background color, strength multiplier, or HDRI environment map).
* **Arguments:**
  * `color` *(float array, optional)*: `[R, G, B]` background color.
  * `strength` *(float, optional)*: Background intensity multiplier.
  * `hdri_path` *(string, optional)*: Path to HDRI `.exr` or `.hdr` file.

### `blender_inspect_environment`
* **Description:** Inspect scene illumination: active camera, world background, and all lights in the scene.
* **Arguments:** None

---

## 7. Geometry Nodes Tools (4)

### `blender_list_geometry_node_groups`
* **Description:** List all Geometry Node groups in the active Blender project with user counts and input/output socket names.
* **Arguments:** None
* **Returns:** List of node groups with socket signatures.

### `blender_inspect_geometry_nodes`
* **Description:** Inspect a Geometry Nodes modifier on an object or a node group directly (socket signatures, default values, current modifier overrides, node types).
* **Arguments:**
  * `object_name` *(string, optional)*: Object with modifier.
  * `modifier_name` *(string, default "GeometryNodes")*: Modifier name on object.
  * `group_name` *(string, optional)*: Node group name.

### `blender_assign_geometry_nodes`
* **Description:** Assign a Geometry Nodes modifier to an object, optionally linking an existing node group or creating a new passthrough node tree.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.
  * `group_name` *(string, optional)*: Group name to assign or create.
  * `modifier_name` *(string, default "GeometryNodes")*: Modifier name.
  * `create_if_missing` *(boolean, default true)*: Create new node tree if not found.

### `blender_configure_geometry_nodes`
* **Description:** Configure input socket parameter values of a Geometry Nodes modifier on an object.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.
  * `inputs` *(object, required)*: Key-value map of socket names or identifiers to values.
  * `modifier_name` *(string, default "GeometryNodes")*: Modifier name.

---

## 8. Armatures & Rigging Tools (4)

### `blender_create_armature`
* **Description:** Create an Armature object in Blender, optionally with an initial root bone.
* **Arguments:**
  * `name` *(string, default "Armature")*: Armature name.
  * `location` *(float array, optional)*: `[X, Y, Z]` world position.
  * `rotation` *(float array, optional)*: `[X, Y, Z]` Euler rotation in radians.
  * `scale` *(float array, optional)*: `[X, Y, Z]` scale.
  * `initial_bone_name` *(string, optional, default "Root")*: First bone name.
  * `initial_bone_head` *(float array, default [0, 0, 0])*: Root bone head.
  * `initial_bone_tail` *(float array, default [0, 0, 1])*: Root bone tail.

### `blender_inspect_armature`
* **Description:** Inspect bone hierarchy, head/tail coordinates, lengths, connected flags, and parent relationships of an Armature.
* **Arguments:**
  * `name` *(string, required)*: Armature object name.

### `blender_add_bone`
* **Description:** Add a new bone to an existing armature in edit mode with head/tail positions, roll, and parent linkage.
* **Arguments:**
  * `armature_name` *(string, required)*: Armature object name.
  * `bone_name` *(string, required)*: Name of new bone.
  * `head` *(float array, default [0, 0, 0])*: Local head coordinates.
  * `tail` *(float array, default [0, 0, 1])*: Local tail coordinates.
  * `parent_bone` *(string, optional)*: Parent bone name.
  * `use_connect` *(boolean, default false)*: Connect head to parent tail.
  * `roll` *(float, default 0.0)*: Bone roll angle in radians.

### `blender_parent_mesh_to_armature`
* **Description:** Parent a mesh object to an armature with automatic weights skinning and modifier setup.
* **Arguments:**
  * `mesh_object_name` *(string, required)*: Mesh object name.
  * `armature_object_name` *(string, required)*: Armature object name.
  * `parent_type` *(string, default "ARMATURE_AUTO")*: `"ARMATURE_AUTO"`, `"ARMATURE_ENVELOPE"`, or `"ARMATURE"`.

---

## 9. Animation & Timeline Tools (4)

### `blender_create_keyframe`
* **Description:** Insert a keyframe on an object for a data property (`location`, `rotation_euler`, `scale`) at a specified timeline frame.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.
  * `frame` *(float, required)*: Timeline frame number.
  * `data_path` *(string, default "location")*: Property to animate.
  * `value` *(float or float array, optional)*: Value to set before keyframing.
  * `index` *(integer, default -1)*: Array index (-1 for all axes, 0 for X, 1 for Y, 2 for Z).

### `blender_inspect_animation`
* **Description:** Inspect active action, F-Curves, keyframe points (frame, value, interpolation), and frame range on an object.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.

### `blender_configure_animation`
* **Description:** Configure keyframe interpolation (`"BEZIER"`, `"LINEAR"`, `"CONSTANT"`), delete keyframes at a frame, or clear all animation data.
* **Arguments:**
  * `object_name` *(string, required)*: Target object.
  * `data_path` *(string, optional)*: Filter by property data path.
  * `interpolation` *(string, optional)*: `"BEZIER"`, `"LINEAR"`, or `"CONSTANT"`.
  * `clear_all` *(boolean, default false)*: Clear animation data completely.
  * `delete_frame` *(float, optional)*: Delete keyframes at frame number.

### `blender_playback_range`
* **Description:** Inspect or configure the scene timeline playback range: start frame, end frame, current playhead frame, and framerate (FPS).
* **Arguments:**
  * `frame_start` *(integer, optional)*: Timeline start frame.
  * `frame_end` *(integer, optional)*: Timeline end frame.
  * `frame_current` *(integer, optional)*: Playhead frame.
  * `fps` *(integer, optional)*: Playback frames per second.
* **Returns:** Current timeline state, total frames, and duration in seconds.

---

## 10. Physics & Simulation Tools (4)

### `blender_configure_rigidbody`
* **Description:** Add or configure rigid body physics on an object (mass, friction, restitution, shape, active/passive).
* **Arguments:**
  * `name` *(string, required)*: Object name.
  * `type` *(string, default "ACTIVE")*: `"ACTIVE"` or `"PASSIVE"`.
  * `mass` *(float, optional)*: Mass in kg.
  * `friction` *(float, optional)*: Surface friction (0.0 to 1.0).
  * `restitution` *(float, optional)*: Bounciness (0.0 to 1.0).
  * `collision_shape` *(string, optional)*: `"BOX"`, `"SPHERE"`, `"CAPSULE"`, `"CYLINDER"`, `"CONE"`, `"CONVEX_HULL"`, `"MESH"`.
  * `kinematic` *(boolean, optional)*: Motion driven by keyframes.
  * `enabled` *(boolean, optional)*: Enable or disable simulation on object.

### `blender_configure_cloth`
* **Description:** Add or configure cloth simulation modifier on an object (mass, tension, compression, shear, bending stiffness, collisions).
* **Arguments:**
  * `name` *(string, required)*: Object name.
  * `mass` *(float, optional)*: Vertex mass in kg.
  * `tension_stiffness`, `compression_stiffness`, `shear_stiffness`, `bending_stiffness` *(float, optional)*: Stiffness parameters.
  * `shrink_factor` *(float, optional)*: Shrink / expansion factor.
  * `use_collision` *(boolean, optional)*: Enable cloth collisions.

### `blender_inspect_physics`
* **Description:** Inspect all physics systems active on an object (rigid body, cloth, collision, particle systems).
* **Arguments:**
  * `name` *(string, required)*: Object name.

### `blender_bake_simulation`
* **Description:** Configure or bake simulation cache frame range (e.g. `"RIGIDBODY"`).
* **Arguments:**
  * `simulation_type` *(string, default "RIGIDBODY")*: Simulation cache type.
  * `frame_start` *(integer, optional)*: Start frame.
  * `frame_end` *(integer, optional)*: End frame.

---

## 11. Rendering & Compositing Tools (5)

### `blender_configure_render`
* **Description:** Configure render engine (`CYCLES`, `BLENDER_EEVEE_NEXT`, `BLENDER_EEVEE`, `WORKBENCH`), resolution, samples, output format (`PNG`, `JPEG`, `OPEN_EXR`), color mode, and transparent background.
* **Arguments:**
  * `engine` *(string, optional)*: Render engine identifier.
  * `resolution_x`, `resolution_y` *(integer, optional)*: Pixel resolution.
  * `resolution_percentage` *(integer, optional)*: Percentage scale (1-100).
  * `samples` *(integer, optional)*: Render samples.
  * `file_format` *(string, optional)*: Image format.
  * `color_mode` *(string, optional)*: `"RGB"`, `"RGBA"`, or `"BW"`.
  * `filepath` *(string, optional)*: Output filepath (validated against path policy).
  * `transparent_background` *(boolean, optional)*: Film transparency.

### `blender_render_preview`
* **Description:** Render a fast still image preview of the current frame and return output filepath, dimensions, file size, and render duration.
* **Arguments:**
  * `output_path` *(string, optional)*: Custom output path or safe temp directory if omitted.
  * `resolution_percentage` *(integer, default 50)*: Fast preview resolution percentage.
  * `samples` *(integer, default 16)*: Fast preview sample count.
  * `write_image` *(boolean, default true)*: Save image file to disk.

### `blender_render_status`
* **Description:** Retrieve current render configuration, active camera, resolution, and timeline settings.
* **Arguments:** None

### `blender_inspect_compositor`
* **Description:** Inspect the scene compositor node tree, active nodes, inputs, outputs, and links.
* **Arguments:** None

### `blender_configure_compositor`
* **Description:** Enable/disable scene compositing nodes and add nodes (e.g. `'CompositorNodeDenoise'`, `'CompositorNodeGlare'`).
* **Arguments:**
  * `use_nodes` *(boolean, default true)*: Enable scene compositing nodes.
  * `add_node_type` *(string, optional)*: Node type to create.
  * `node_name` *(string, optional)*: Custom name for added node.
